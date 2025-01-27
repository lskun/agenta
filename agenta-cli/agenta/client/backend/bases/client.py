# This file was auto-generated by Fern from our API Definition.

from ..core.client_wrapper import SyncClientWrapper
import typing
from ..core.request_options import RequestOptions
from ..types.base_output import BaseOutput
from ..core.pydantic_utilities import parse_obj_as
from ..errors.unprocessable_entity_error import UnprocessableEntityError
from ..types.http_validation_error import HttpValidationError
from json.decoder import JSONDecodeError
from ..core.api_error import ApiError
from ..core.client_wrapper import AsyncClientWrapper


class BasesClient:
    def __init__(self, *, client_wrapper: SyncClientWrapper):
        self._client_wrapper = client_wrapper

    def list_bases(
        self,
        *,
        app_id: str,
        base_name: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.List[BaseOutput]:
        """
        Retrieve a list of bases filtered by app_id and base_name.

        Args:
            request (Request): The incoming request.
            app_id (str): The ID of the app to filter by.
            base_name (Optional[str], optional): The name of the base to filter by. Defaults to None.

        Returns:
            List[BaseOutput]: A list of BaseOutput objects representing the filtered bases.

        Raises:
            HTTPException: If there was an error retrieving the bases.

        Parameters
        ----------
        app_id : str

        base_name : typing.Optional[str]

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        typing.List[BaseOutput]
            Successful Response

        Examples
        --------
        from agenta import AgentaApi

        client = AgentaApi(
            api_key="YOUR_API_KEY",
            base_url="https://yourhost.com/path/to/api",
        )
        client.bases.list_bases(
            app_id="app_id",
        )
        """
        _response = self._client_wrapper.httpx_client.request(
            "bases",
            method="GET",
            params={
                "app_id": app_id,
                "base_name": base_name,
            },
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    typing.List[BaseOutput],
                    parse_obj_as(
                        type_=typing.List[BaseOutput],  # type: ignore
                        object_=_response.json(),
                    ),
                )
            if _response.status_code == 422:
                raise UnprocessableEntityError(
                    typing.cast(
                        HttpValidationError,
                        parse_obj_as(
                            type_=HttpValidationError,  # type: ignore
                            object_=_response.json(),
                        ),
                    )
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)


class AsyncBasesClient:
    def __init__(self, *, client_wrapper: AsyncClientWrapper):
        self._client_wrapper = client_wrapper

    async def list_bases(
        self,
        *,
        app_id: str,
        base_name: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.List[BaseOutput]:
        """
        Retrieve a list of bases filtered by app_id and base_name.

        Args:
            request (Request): The incoming request.
            app_id (str): The ID of the app to filter by.
            base_name (Optional[str], optional): The name of the base to filter by. Defaults to None.

        Returns:
            List[BaseOutput]: A list of BaseOutput objects representing the filtered bases.

        Raises:
            HTTPException: If there was an error retrieving the bases.

        Parameters
        ----------
        app_id : str

        base_name : typing.Optional[str]

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        typing.List[BaseOutput]
            Successful Response

        Examples
        --------
        import asyncio

        from agenta import AsyncAgentaApi

        client = AsyncAgentaApi(
            api_key="YOUR_API_KEY",
            base_url="https://yourhost.com/path/to/api",
        )


        async def main() -> None:
            await client.bases.list_bases(
                app_id="app_id",
            )


        asyncio.run(main())
        """
        _response = await self._client_wrapper.httpx_client.request(
            "bases",
            method="GET",
            params={
                "app_id": app_id,
                "base_name": base_name,
            },
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    typing.List[BaseOutput],
                    parse_obj_as(
                        type_=typing.List[BaseOutput],  # type: ignore
                        object_=_response.json(),
                    ),
                )
            if _response.status_code == 422:
                raise UnprocessableEntityError(
                    typing.cast(
                        HttpValidationError,
                        parse_obj_as(
                            type_=HttpValidationError,  # type: ignore
                            object_=_response.json(),
                        ),
                    )
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)
