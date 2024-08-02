"""The code for the Agenta SDK"""

from agenta.sdk.utils.debug import debug, DEBUG, SHIFT
import os
import sys
import time
import json
import inspect
import argparse
import asyncio
import traceback
import functools
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Callable, Dict, Optional, Tuple, List

from fastapi.middleware.cors import CORSMiddleware
from fastapi import Body, FastAPI, UploadFile, HTTPException

import agenta as ag
from agenta.sdk.context import save_context
from agenta.sdk.router import router as router
from agenta.sdk.tracing.logger import llm_logger as logging
from agenta.sdk.tracing.tracing_context import tracing_context, TracingContext
from agenta.sdk.decorators.base import BaseDecorator
from agenta.sdk.types import (
    Context,
    DictInput,
    FloatParam,
    InFile,
    IntParam,
    MultipleChoiceParam,
    MultipleChoice,
    GroupedMultipleChoiceParam,
    TextParam,
    MessagesInput,
    FileInputURL,
    BaseResponse,
    BinaryParam,
)
from pydantic import BaseModel
from typing import Type
from annotated_types import Ge, Le, Gt, Lt

from pydantic import BaseModel, HttpUrl

app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="")


logging.setLevel("DEBUG")


class PathValidator(BaseModel):
    url: HttpUrl


class route(BaseDecorator):
    # This decorator is used to expose specific stages of a workflow (embedding, retrieval, summarization, etc.)
    # as independent endpoints. It is designed for backward compatibility with existing code that uses
    # the @entrypoint decorator, which has certain limitations. By using @route(), we can create new
    # routes without altering the main workflow entrypoint. This helps in modularizing the services
    # and provides flexibility in how we expose different functionalities as APIs.
    def __init__(self, path, config: BaseModel):
        self.config: BaseModel = config
        if path != "" and path[0] != "/":
            path = "/" + path

        while path != "" and path[-1] == "/":
            path = path[:-1]

        PathValidator(url=f"http://localhost:8000{path}")

        self.route_path = path

    def __call__(self, f):
        self.e = entrypoint(f, route_path=self.route_path, config=self.config)

        return f


class entrypoint(BaseDecorator):
    """Decorator class to wrap a function for HTTP POST, terminal exposure and enable tracing.


    Example:
    ```python
        import agenta as ag

        @ag.entrypoint
        async def chain_of_prompts_llm(prompt: str):
            return ...
    ```
    """

    routes = list()

    def __init__(self, func: Callable[..., Any], route_path="", config: BaseModel = None):
        endpoint_name = "generate"
        playground_path = "/playground"
        run_path = "/run"
        func_signature = inspect.signature(func)
        config_params = config.dict() if config else ag.config.all()
        ingestible_files = self.extract_ingestible_files(func_signature)

        ### --- Playground / Drafts  --- #
        @debug()
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            func_params, api_config_params = self.split_kwargs(kwargs, self.config.dict())
            self.ingest_files(func_params, ingestible_files)
            ag.config.set(**api_config_params)

            # Set the configuration and environment of the LLM app parent span at run-time
            ag.tracing.update_baggage(
                {"config": config_params, "environment": "playground"}
            )

            # Exceptions are all handled inside self.execute_function()
            entrypoint_result = await self.execute_function(
                func, *args, params=func_params, config_params=config_params
            )

            return entrypoint_result

        self.update_function_signature(
            wrapper, func_signature, config_params, ingestible_files
        )

        # TODO:
        # - The whole ag.Config is now required for individual stages.
        #   Once ag.Config goes from Singleton to Instance, and
        #   depending on how ag.Config is implemented,
        #   we need to filter the part of ag.Config that matters to each route.

        if route_path == "":
            route = f"/{endpoint_name}"
            app.post(route, response_model=BaseResponse)(wrapper)
            entrypoint.routes.append(
                {
                    "func": func.__name__,
                    "endpoint": endpoint_name,
                    "params": {**config_params, **func_signature.parameters},
                    "config": config,
                }
            )

        route = f"{playground_path}{run_path}{route_path}"
        app.post(route, response_model=BaseResponse)(wrapper)
        entrypoint.routes.append(
            {
                "func": func.__name__,
                "endpoint": route[1:].replace("/", "_"),
                "params": {**config_params, **func_signature.parameters},
                "config": config,
            }
        )
        ### ---------------------------- #

        ### --- Deployed / Published --- #
        @debug()
        @functools.wraps(func)
        async def wrapper_deployed(*args, **kwargs) -> Any:
            func_params = {
                k: v for k, v in kwargs.items() if k not in ["config", "environment"]
            }

            if "environment" in kwargs and kwargs["environment"] is not None:
                ag.config.pull(environment_name=kwargs["environment"])
            elif "config" in kwargs and kwargs["config"] is not None:
                ag.config.pull(config_name=kwargs["config"])
            else:
                ag.config.pull(config_name="default")

            # Set the configuration and environment of the LLM app parent span at run-time
            ag.tracing.update_baggage(
                {"config": config_params, "environment": kwargs["environment"]}
            )

            entrypoint_result = await self.execute_function(
                func, *args, params=func_params, config_params=config_params
            )

            return entrypoint_result

        self.update_deployed_function_signature(
            wrapper_deployed,
            func_signature,
            ingestible_files,
        )

        if route_path == "/":
            route_deployed = f"/{endpoint_name}_deployed"
            app.post(route_deployed, response_model=BaseResponse)(wrapper_deployed)

        route_deployed = f"{run_path}{route_path}"
        app.post(route_deployed, response_model=BaseResponse)(wrapper_deployed)
        ### ---------------------------- #

        app.openapi_schema = None
        openapi_schema = app.openapi()

        for route in entrypoint.routes:
            self.override_schema(
                openapi_schema=openapi_schema,
                func_name=route["func"],
                endpoint=route["endpoint"],
                params=route["params"],
            )
            if route["config"] is not None:
                self.override_config_in_schema(
                    openapi_schema=openapi_schema,
                    func_name=route["func"],
                    endpoint=route["endpoint"],
                    config=route["config"],
                )

        if self.is_main_script(func) and route_path == "":
            self.handle_terminal_run(
                func,
                func_signature.parameters,  # type: ignore
                self.config.dict(),
                ingestible_files,
            )

    def extract_ingestible_files(
        self,
        func_signature: inspect.Signature,
    ) -> Dict[str, inspect.Parameter]:
        """Extract parameters annotated as InFile from function signature."""

        return {
            name: param
            for name, param in func_signature.parameters.items()
            if param.annotation is InFile
        }

    def split_kwargs(
        self, kwargs: Dict[str, Any], config_params: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Split keyword arguments into function parameters and API configuration parameters."""

        func_params = {k: v for k, v in kwargs.items() if k not in config_params}
        api_config_params = {k: v for k, v in kwargs.items() if k in config_params}
        return func_params, api_config_params

    def ingest_file(self, upfile: UploadFile):
        temp_file = NamedTemporaryFile(delete=False)
        temp_file.write(upfile.file.read())
        temp_file.close()
        return InFile(file_name=upfile.filename, file_path=temp_file.name)

    def ingest_files(
        self,
        func_params: Dict[str, Any],
        ingestible_files: Dict[str, inspect.Parameter],
    ) -> None:
        """Ingest files specified in function parameters."""

        for name in ingestible_files:
            if name in func_params and func_params[name] is not None:
                func_params[name] = self.ingest_file(func_params[name])

    async def execute_function(self, func: Callable[..., Any], *args, **func_params):
        """Execute the function and handle any exceptions."""

        try:
            """Note: The following block is for backward compatibility.
            It allows functions to work seamlessly whether they are synchronous or asynchronous.
            For synchronous functions, it calls them directly, while for asynchronous functions,
            it awaits their execution.
            """
            data = None
            trace = None

            token = None
            if tracing_context.get() is None:
                token = tracing_context.set(TracingContext())

            is_coroutine_function = inspect.iscoroutinefunction(func)

            if is_coroutine_function:
                result = await func(*args, **func_params["params"])
            else:
                result = func(*args, **func_params["params"])

            if token is not None:
                # check that it doesn't affect the tracing.tree
                trace = ag.tracing.dump_trace()

                tracing_context.reset(token)

            if isinstance(result, Context):
                save_context(result)

            if isinstance(result, Dict):
                if "message" in result:
                    data = {"message": result["message"]}
                else:
                    data = result
            elif isinstance(result, str):
                data = {"message": result}
            elif isinstance(result, int) or isinstance(result, float):
                data = {"message": str(result)}

            if data is None:
                warning = (
                    "Function executed successfully, but did return None. \n Are you sure you did not forget to return a value?",
                )

                data = {"message": warning}

            return BaseResponse(data=data, trace=trace)

        except Exception as e:
            self.handle_exception(e)

    def handle_exception(self, e: Exception):
        status_code = e.status_code if hasattr(e, "status_code") else 500
        message = str(e)
        stacktrace = traceback.format_exception(e, value=e, tb=e.__traceback__)  # type: ignore
        detail = {"message": message, "stacktrace": stacktrace}

        raise HTTPException(
            status_code=status_code,
            detail=detail,
        )

    def update_wrapper_signature(
        self, wrapper: Callable[..., Any], updated_params: List
    ):
        """
        Updates the signature of a wrapper function with a new list of parameters.

        Args:
            wrapper (callable): A callable object, such as a function or a method, that requires a signature update.
            updated_params (List[inspect.Parameter]): A list of `inspect.Parameter` objects representing the updated parameters
                for the wrapper function.
        """

        wrapper_signature = inspect.signature(wrapper)
        wrapper_signature = wrapper_signature.replace(parameters=updated_params)
        wrapper.__signature__ = wrapper_signature  # type: ignore

    def update_function_signature(
        self,
        wrapper: Callable[..., Any],
        func_signature: inspect.Signature,
        config_class: Type[BaseModel],  # TODO: change to our type
        ingestible_files: Dict[str, inspect.Parameter],
    ) -> None:
        """Update the function signature to include new parameters."""

        updated_params: List[inspect.Parameter] = []
        self.add_config_params_to_parser(updated_params, config_class)
        self.add_func_params_to_parser(updated_params, func_signature, ingestible_files)
        self.update_wrapper_signature(wrapper, updated_params)

    def update_deployed_function_signature(
        self,
        wrapper: Callable[..., Any],
        func_signature: inspect.Signature,
        ingestible_files: Dict[str, inspect.Parameter],
    ) -> None:
        """Update the function signature to include new parameters."""

        updated_params: List[inspect.Parameter] = []
        self.add_func_params_to_parser(updated_params, func_signature, ingestible_files)
        for param in [
            "config",
            "environment",
        ]:  # we add the config and environment parameters
            updated_params.append(
                inspect.Parameter(
                    name=param,
                    kind=inspect.Parameter.KEYWORD_ONLY,
                    default=Body(None),
                    annotation=str,
                )
            )
        self.update_wrapper_signature(wrapper, updated_params)

    def add_config_params_to_parser(
        self, updated_params: list, config_class: Type[BaseModel]
    ) -> None:
        """Add configuration parameters to function signature."""
        for name, field in config_class.__fields__.items():
            assert field.default is not None, f"Field {name} has no default value"
            updated_params.append(
                inspect.Parameter(
                    name=name,
                    kind=inspect.Parameter.KEYWORD_ONLY,
                    annotation=field.annotation.__name__,
                    default=Body(field.default)
                )
            )

    def add_func_params_to_parser(
        self,
        updated_params: list,
        func_signature: inspect.Signature,
        ingestible_files: Dict[str, inspect.Parameter],
    ) -> None:
        """Add function parameters to function signature."""
        for name, param in func_signature.parameters.items():
            if name in ingestible_files:
                updated_params.append(
                    inspect.Parameter(name, param.kind, annotation=UploadFile)
                )
            else:
                assert (
                    len(param.default.__class__.__bases__) == 1
                ), f"Inherited standard type of {param.default.__class__} needs to be one."
                updated_params.append(
                    inspect.Parameter(
                        name,
                        inspect.Parameter.KEYWORD_ONLY,
                        default=Body(..., embed=True),
                        annotation=param.default.__class__.__bases__[
                            0
                        ],  # determines and get the base (parent/inheritance) type of the sdk-type at run-time. \
                        # E.g __class__ is ag.MessagesInput() and accessing it parent type will return (<class 'list'>,), \
                        # thus, why we are accessing the first item.
                    )
                )

    def is_main_script(self, func: Callable) -> bool:
        """
        Check if the script containing the function is the main script being run.

        Args:
            func (Callable): The function object to check.

        Returns:
            bool: True if the script containing the function is the main script, False otherwise.

        Example:
            if is_main_script(my_function):
                print("This is the main script.")
        """
        return func.__module__ == "__main__"

    def handle_terminal_run(
        self,
        func: Callable,
        func_params: Dict[str, inspect.Parameter],
        config_params: Dict[str, Any],
        ingestible_files: Dict,
    ):
        """
        Parses command line arguments and sets configuration when script is run from the terminal.

        Args:
            func_params (dict): A dictionary containing the function parameters and their annotations.
            config_params (dict): A dictionary containing the configuration parameters.
            ingestible_files (dict): A dictionary containing the files that should be ingested.
        """

        # For required parameters, we add them as arguments
        parser = argparse.ArgumentParser()
        for name, param in func_params.items():
            if name in ingestible_files:
                parser.add_argument(name, type=str)
            else:
                parser.add_argument(name, type=param.annotation)

        for name, param in config_params.items():
            if type(param) is MultipleChoiceParam:
                parser.add_argument(
                    f"--{name}",
                    type=str,
                    default=param.default,
                    choices=param.choices,  # type: ignore
                )
            else:
                parser.add_argument(
                    f"--{name}",
                    type=type(param),
                    default=param,
                )

        args = parser.parse_args()

        # split the arg list into the arg in the app_param and
        # the args from the sig.parameter
        args_config_params = {k: v for k, v in vars(args).items() if k in config_params}
        args_func_params = {
            k: v for k, v in vars(args).items() if k not in config_params
        }
        for name in ingestible_files:
            args_func_params[name] = InFile(
                file_name=Path(args_func_params[name]).stem,
                file_path=args_func_params[name],
            )

        # Update args_config_params with default values from config_params if not provided in command line arguments
        args_config_params.update({key: value for key, value in config_params.items() if key not in args_config_params})

        # Set the configuration and environment of the LLM app parent span at run-time
        ag.tracing.update_baggage(
            {"config": args_config_params, "environment": "bash"}
        )

        loop = asyncio.get_event_loop()

        result = loop.run_until_complete(
            self.execute_function(
                func,
                **{"params": args_func_params, "config_params": args_config_params},
            )
        )

        print("\n========== Result ==========\n")

        print("-> data")
        print(json.dumps(result.data, indent=2))
        print("-> trace")
        print(json.dumps(result.trace, indent=2))

        with open("trace.json", "w") as trace_file:
            json.dump(result.trace, trace_file, indent=4)

    def override_config_in_schema(
        self, openapi_schema: dict, func_name: str, endpoint: str, config: Type[BaseModel]
    ):
        schema_to_override = openapi_schema["components"]["schemas"][
            f"Body_{func_name}_{endpoint}_post"
        ]["properties"]
        # New logic
        for param_name, param_val in config.__fields__.items():
            if param_val.annotation is str:
                if any(isinstance(constraint, MultipleChoice) for constraint in param_val.metadata):
                    choices = next(constraint.choices for constraint in param_val.metadata if isinstance(constraint, MultipleChoice))
                    if isinstance(choices, dict):
                        schema_to_override[param_name]["x-parameter"] = "grouped_choice"
                        schema_to_override[param_name]["choices"] = choices
                    elif isinstance(choices, list):
                        schema_to_override[param_name]["x-parameter"] = "choice"
                        schema_to_override[param_name]["choices"] = choices
                else:
                    schema_to_override[param_name]["x-parameter"] = "text"
            if param_val.annotation is bool:
                schema_to_override[param_name]["x-parameter"] = "bool"
            if param_val.annotation is int:
                schema_to_override[param_name]["x-parameter"] = "int"
                # Check for greater than or equal to constraint
                if any(isinstance(constraint, Ge) for constraint in param_val.metadata):
                    min_value = next(constraint.ge for constraint in param_val.metadata if isinstance(constraint, Ge))
                    schema_to_override[param_name]["minimum"] = min_value
                # Check for less than or equal to constraint
                if any(isinstance(constraint, Le) for constraint in param_val.metadata):
                    max_value = next(constraint.le for constraint in param_val.metadata if isinstance(constraint, Le))
                    schema_to_override[param_name]["maximum"] = max_value
            if param_val.annotation is float:
                schema_to_override[param_name]["x-parameter"] = "float"
                # Check for greater than constraint
                if any(isinstance(constraint, Gt) for constraint in param_val.metadata):
                    min_value = next(constraint.gt for constraint in param_val.metadata if isinstance(constraint, Gt))
                    schema_to_override[param_name]["minimum"] = min_value
                # Check for less than constraint
                if any(isinstance(constraint, Lt) for constraint in param_val.metadata):
                    max_value = next(constraint.lt for constraint in param_val.metadata if isinstance(constraint, Lt))
                    schema_to_override[param_name]["maximum"] = max_value

    def override_schema(
        self, openapi_schema: dict, func_name: str, endpoint: str, params: dict
    ):
        """
        Overrides the default openai schema generated by fastapi with additional information about:
        - The choices available for each MultipleChoiceParam instance
        - The min and max values for each FloatParam instance
        - The min and max values for each IntParam instance
        - The default value for DictInput instance
        - The default value for MessagesParam instance
        - The default value for FileInputURL instance
        - The default value for BinaryParam instance
        - ... [PLEASE ADD AT EACH CHANGE]

        Args:
            openapi_schema (dict): The openapi schema generated by fastapi
            func (str): The name of the function to override
            endpoint (str): The name of the endpoint to override
            params (dict(param_name, param_val)): The dictionary of the parameters for the function
        """
        def find_in_schema(schema_type_properties: dict, schema: dict, param_name: str, xparam: str):
            """Finds a parameter in the schema based on its name and x-parameter value"""
            for _, value in schema.items():
                value_title_lower = str(value.get("title")).lower()
                value_title = (
                    "_".join(value_title_lower.split())
                    if len(value_title_lower.split()) >= 2
                    else value_title_lower
                )

                if (
                    isinstance(value, dict)
                    and schema_type_properties.get("x-parameter") == xparam
                    and value_title == param_name
                ):
                    # this will update the default type schema with the properties gotten
                    # from the schema type (param_val) __schema_properties__ classmethod
                    for type_key, type_value in schema_type_properties.items():
                        # BEFORE:
                        # value = {'temperature': {'title': 'Temperature'}}
                        value[type_key] = type_value
                        # AFTER:
                        # value = {'temperature': { "type": "number", "title": "Temperature", "x-parameter": "float" }}
                    return value

        def get_type_from_param(param_val):
            param_type = "string"
            annotation = param_val.annotation

            if annotation == int:
                param_type = "integer"
            elif annotation == float:
                param_type = "number"
            elif annotation == dict:
                param_type = "object"
            elif annotation == bool:
                param_type = "boolean"
            elif annotation == list:
                param_type = "list"
            elif annotation == str:
                param_type = "string"
            else:
                print("ERROR, unhandled annotation:", annotation)

            return param_type

        schema_to_override = openapi_schema["components"]["schemas"][
            f"Body_{func_name}_post"
        ]["properties"]

        for param_name, param_val in params.items():
            if isinstance(param_val, GroupedMultipleChoiceParam):
                subschema = find_in_schema(
                    param_val.__schema_type_properties__(),
                    schema_to_override,
                    param_name,
                    "grouped_choice",
                )
                assert (
                    subschema
                ), f"GroupedMultipleChoiceParam '{param_name}' is in the parameters but could not be found in the openapi.json"
                subschema["choices"] = param_val.choices  # type: ignore
                subschema["default"] = param_val.default  # type: ignore

            elif isinstance(param_val, MultipleChoiceParam):
                subschema = find_in_schema(
                    param_val.__schema_type_properties__(),
                    schema_to_override,
                    param_name,
                    "choice",
                )
                default = str(param_val)
                param_choices = param_val.choices  # type: ignore
                choices = (
                    [default] + param_choices
                    if param_val not in param_choices
                    else param_choices
                )
                subschema["enum"] = choices
                subschema["default"] = (
                    default if default in param_choices else choices[0]
                )

            elif isinstance(param_val, FloatParam):
                subschema = find_in_schema(
                    param_val.__schema_type_properties__(),
                    schema_to_override,
                    param_name,
                    "float",
                )
                subschema["minimum"] = param_val.minval  # type: ignore
                subschema["maximum"] = param_val.maxval  # type: ignore
                subschema["default"] = param_val

            elif isinstance(param_val, IntParam):
                subschema = find_in_schema(
                    param_val.__schema_type_properties__(),
                    schema_to_override,
                    param_name,
                    "int",
                )
                subschema["minimum"] = param_val.minval  # type: ignore
                subschema["maximum"] = param_val.maxval  # type: ignore
                subschema["default"] = param_val

            elif (
                isinstance(param_val, inspect.Parameter)
                and param_val.annotation is DictInput
            ):
                subschema = find_in_schema(
                    param_val.annotation.__schema_type_properties__(),
                    schema_to_override,
                    param_name,
                    "dict",
                )
                subschema["default"] = param_val.default["default_keys"]

            elif isinstance(param_val, TextParam):
                subschema = find_in_schema(
                    param_val.__schema_type_properties__(),
                    schema_to_override,
                    param_name,
                    "text",
                )
                subschema["default"] = param_val

            elif (
                isinstance(param_val, inspect.Parameter)
                and param_val.annotation is MessagesInput
            ):
                subschema = find_in_schema(
                    param_val.annotation.__schema_type_properties__(),
                    schema_to_override,
                    param_name,
                    "messages",
                )
                subschema["default"] = param_val.default

            elif (
                isinstance(param_val, inspect.Parameter)
                and param_val.annotation is FileInputURL
            ):
                subschema = find_in_schema(
                    param_val.annotation.__schema_type_properties__(),
                    schema_to_override,
                    param_name,
                    "file_url",
                )
                subschema["default"] = "https://example.com"

            elif isinstance(param_val, BinaryParam):
                subschema = find_in_schema(
                    param_val.__schema_type_properties__(),
                    schema_to_override,
                    param_name,
                    "bool",
                )
                subschema["default"] = param_val.default  # type: ignore
            else:
                subschema = {
                    "title": str(param_name).capitalize(),
                    "type": get_type_from_param(param_val),
                }
                if param_val.default != inspect._empty:
                    subschema["default"] = param_val.default  # type: ignore
                schema_to_override[param_name] = subschema
