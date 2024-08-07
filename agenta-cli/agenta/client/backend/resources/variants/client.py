# This file was auto-generated by Fern from our API Definition.

import typing
import urllib.parse
from json.decoder import JSONDecodeError

from ...core.api_error import ApiError
from ...core.client_wrapper import AsyncClientWrapper, SyncClientWrapper
from ...core.jsonable_encoder import jsonable_encoder
from ...errors.unprocessable_entity_error import UnprocessableEntityError
from ...types.app_variant_response import AppVariantResponse
from ...types.app_variant_revision import AppVariantRevision
from ...types.docker_env_vars import DockerEnvVars
from ...types.http_validation_error import HttpValidationError
from ...types.image import Image
from ...types.uri import Uri
from ...types.variant_action import VariantAction
from .types.add_variant_from_base_and_config_response import (
    AddVariantFromBaseAndConfigResponse,
)

try:
    import pydantic.v1 as pydantic  # type: ignore
except ImportError:
    import pydantic  # type: ignore

# this is used as the default value for optional parameters
OMIT = typing.cast(typing.Any, ...)


class VariantsClient:
    def __init__(self, *, client_wrapper: SyncClientWrapper):
        self._client_wrapper = client_wrapper

    def add_variant_from_base_and_config(
        self,
        *,
        base_id: str,
        new_variant_name: str,
        new_config_name: str,
        parameters: typing.Dict[str, typing.Any],
    ) -> AddVariantFromBaseAndConfigResponse:
        """
        Add a new variant based on an existing one.
        Same as POST /config

        Args:
        payload (AddVariantFromBasePayload): Payload containing base variant ID, new variant name, and parameters.
        stoken_session (SessionContainer, optional): Session container. Defaults to result of verify_session().

        Raises:
        HTTPException: Raised if the variant could not be added or accessed.

        Returns:
        Union[AppVariantResponse, Any]: New variant details or exception.

        Parameters:
            - base_id: str.

            - new_variant_name: str.

            - new_config_name: str.

            - parameters: typing.Dict[str, typing.Any].
        """
        _response = self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_base_url()}/", "variants/from-base"
            ),
            json=jsonable_encoder(
                {
                    "base_id": base_id,
                    "new_variant_name": new_variant_name,
                    "new_config_name": new_config_name,
                    "parameters": parameters,
                }
            ),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(AddVariantFromBaseAndConfigResponse, _response.json())  # type: ignore
        if _response.status_code == 422:
            raise UnprocessableEntityError(pydantic.parse_obj_as(HttpValidationError, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def get_variant(self, variant_id: str) -> AppVariantResponse:
        """
        Parameters:
            - variant_id: str.
        ---
        from agenta.client import AgentaApi

        client = AgentaApi(
            api_key="YOUR_API_KEY",
            base_url="https://yourhost.com/path/to/api",
        )
        client.variants.get_variant(
            variant_id="variant_id",
        )
        """
        _response = self._client_wrapper.httpx_client.request(
            "GET",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_base_url()}/", f"variants/{variant_id}"
            ),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(AppVariantResponse, _response.json())  # type: ignore
        if _response.status_code == 422:
            raise UnprocessableEntityError(pydantic.parse_obj_as(HttpValidationError, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def start_variant(
        self,
        variant_id: str,
        *,
        action: VariantAction,
        env_vars: typing.Optional[DockerEnvVars] = OMIT,
    ) -> Uri:
        """
        Start a variant of an app.

        Args:
        variant_id (str): The ID of the variant to start.
        action (VariantAction): The action to perform on the variant (start).
        env_vars (Optional[DockerEnvVars], optional): The environment variables to inject to the Docker container. Defaults to None.
        stoken_session (SessionContainer, optional): The session container. Defaults to Depends(verify_session()).

        Returns:
        URI: The URL of the started variant.

        Raises:
        HTTPException: If the app container cannot be started.

        Parameters:
            - variant_id: str.

            - action: VariantAction.

            - env_vars: typing.Optional[DockerEnvVars].
        ---
        from agenta import VariantAction, VariantActionEnum
        from agenta.client import AgentaApi

        client = AgentaApi(
            api_key="YOUR_API_KEY",
            base_url="https://yourhost.com/path/to/api",
        )
        client.variants.start_variant(
            variant_id="variant_id",
            action=VariantAction(
                action=VariantActionEnum.START,
            ),
        )
        """
        _request: typing.Dict[str, typing.Any] = {"action": action}
        if env_vars is not OMIT:
            _request["env_vars"] = env_vars
        _response = self._client_wrapper.httpx_client.request(
            "PUT",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_base_url()}/", f"variants/{variant_id}"
            ),
            json=jsonable_encoder(_request),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(Uri, _response.json())  # type: ignore
        if _response.status_code == 422:
            raise UnprocessableEntityError(pydantic.parse_obj_as(HttpValidationError, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def remove_variant(self, variant_id: str) -> typing.Any:
        """
        Remove a variant from the server.
        In the case it's the last variant using the image, stop the container and remove the image.

        Arguments:
        app_variant -- AppVariant to remove

        Raises:
        HTTPException: If there is a problem removing the app variant

        Parameters:
            - variant_id: str.
        ---
        from agenta.client import AgentaApi

        client = AgentaApi(
            api_key="YOUR_API_KEY",
            base_url="https://yourhost.com/path/to/api",
        )
        client.variants.remove_variant(
            variant_id="variant_id",
        )
        """
        _response = self._client_wrapper.httpx_client.request(
            "DELETE",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_base_url()}/", f"variants/{variant_id}"
            ),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(typing.Any, _response.json())  # type: ignore
        if _response.status_code == 422:
            raise UnprocessableEntityError(pydantic.parse_obj_as(HttpValidationError, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def update_variant_parameters(
        self, variant_id: str, *, parameters: typing.Dict[str, typing.Any]
    ) -> typing.Any:
        """
        Updates the parameters for an app variant.

        Args:
        variant_id (str): The ID of the app variant to update.
        payload (UpdateVariantParameterPayload): The payload containing the updated parameters.
        stoken_session (SessionContainer, optional): The session container. Defaults to Depends(verify_session()).

        Raises:
        HTTPException: If there is an error while trying to update the app variant.

        Returns:
        JSONResponse: A JSON response containing the updated app variant parameters.

        Parameters:
            - variant_id: str.

            - parameters: typing.Dict[str, typing.Any].
        ---
        from agenta.client import AgentaApi

        client = AgentaApi(
            api_key="YOUR_API_KEY",
            base_url="https://yourhost.com/path/to/api",
        )
        client.variants.update_variant_parameters(
            variant_id="variant_id",
            parameters={},
        )
        """
        _response = self._client_wrapper.httpx_client.request(
            "PUT",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_base_url()}/",
                f"variants/{variant_id}/parameters",
            ),
            json=jsonable_encoder({"parameters": parameters}),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(typing.Any, _response.json())  # type: ignore
        if _response.status_code == 422:
            raise UnprocessableEntityError(pydantic.parse_obj_as(HttpValidationError, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def update_variant_image(self, variant_id: str, *, request: Image) -> typing.Any:
        """
        Updates the image used in an app variant.

        Args:
        variant_id (str): The ID of the app variant to update.
        image (Image): The image information to update.

        Raises:
        HTTPException: If an error occurs while trying to update the app variant.

        Returns:
        JSONResponse: A JSON response indicating whether the update was successful or not.

        Parameters:
            - variant_id: str.

            - request: Image.
        ---
        from agenta import Image
        from agenta.client import AgentaApi

        client = AgentaApi(
            api_key="YOUR_API_KEY",
            base_url="https://yourhost.com/path/to/api",
        )
        client.variants.update_variant_image(
            variant_id="variant_id",
            request=Image(
                docker_id="docker_id",
                tags="tags",
            ),
        )
        """
        _response = self._client_wrapper.httpx_client.request(
            "PUT",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_base_url()}/",
                f"variants/{variant_id}/image",
            ),
            json=jsonable_encoder(request),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(typing.Any, _response.json())  # type: ignore
        if _response.status_code == 422:
            raise UnprocessableEntityError(pydantic.parse_obj_as(HttpValidationError, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def update_variant_url(
        self,
        variant_id: str,
        url: str,
    ):
        """
        ...
        """

        _request: typing.Dict[str, typing.Any] = {
            "url": url,
        }

        _response = self._client_wrapper.httpx_client.request(
            "PUT",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_base_url()}/",
                f"variants/{variant_id}/url",
            ),
            json=jsonable_encoder(_request),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(typing.Any, _response.json())  # type: ignore
        if _response.status_code == 422:
            raise UnprocessableEntityError(pydantic.parse_obj_as(HttpValidationError, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def get_variant_revisions(self, variant_id: str) -> typing.List[AppVariantRevision]:
        """
        Parameters:
            - variant_id: str.
        ---
        from agenta.client import AgentaApi

        client = AgentaApi(
            api_key="YOUR_API_KEY",
            base_url="https://yourhost.com/path/to/api",
        )
        client.variants.get_variant_revisions(
            variant_id="variant_id",
        )
        """
        _response = self._client_wrapper.httpx_client.request(
            "GET",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_base_url()}/",
                f"variants/{variant_id}/revisions",
            ),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(typing.List[AppVariantRevision], _response.json())  # type: ignore
        if _response.status_code == 422:
            raise UnprocessableEntityError(pydantic.parse_obj_as(HttpValidationError, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def get_variant_revision(
        self, variant_id: str, revision_number: int
    ) -> AppVariantRevision:
        """
        Parameters:
            - variant_id: str.

            - revision_number: int.
        ---
        from agenta.client import AgentaApi

        client = AgentaApi(
            api_key="YOUR_API_KEY",
            base_url="https://yourhost.com/path/to/api",
        )
        client.variants.get_variant_revision(
            variant_id="variant_id",
            revision_number=1,
        )
        """
        _response = self._client_wrapper.httpx_client.request(
            "GET",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_base_url()}/",
                f"variants/{variant_id}/revisions/{revision_number}",
            ),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(AppVariantRevision, _response.json())  # type: ignore
        if _response.status_code == 422:
            raise UnprocessableEntityError(pydantic.parse_obj_as(HttpValidationError, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)


class AsyncVariantsClient:
    def __init__(self, *, client_wrapper: AsyncClientWrapper):
        self._client_wrapper = client_wrapper

    async def add_variant_from_base_and_config(
        self,
        *,
        base_id: str,
        new_variant_name: str,
        new_config_name: str,
        parameters: typing.Dict[str, typing.Any],
    ) -> AddVariantFromBaseAndConfigResponse:
        """
        Add a new variant based on an existing one.
        Same as POST /config

        Args:
        payload (AddVariantFromBasePayload): Payload containing base variant ID, new variant name, and parameters.
        stoken_session (SessionContainer, optional): Session container. Defaults to result of verify_session().

        Raises:
        HTTPException: Raised if the variant could not be added or accessed.

        Returns:
        Union[AppVariantResponse, Any]: New variant details or exception.

        Parameters:
            - base_id: str.

            - new_variant_name: str.

            - new_config_name: str.

            - parameters: typing.Dict[str, typing.Any].
        """
        _response = await self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_base_url()}/", "variants/from-base"
            ),
            json=jsonable_encoder(
                {
                    "base_id": base_id,
                    "new_variant_name": new_variant_name,
                    "new_config_name": new_config_name,
                    "parameters": parameters,
                }
            ),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(AddVariantFromBaseAndConfigResponse, _response.json())  # type: ignore
        if _response.status_code == 422:
            raise UnprocessableEntityError(pydantic.parse_obj_as(HttpValidationError, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def get_variant(self, variant_id: str) -> AppVariantResponse:
        """
        Parameters:
            - variant_id: str.
        ---
        from agenta.client import AsyncAgentaApi

        client = AsyncAgentaApi(
            api_key="YOUR_API_KEY",
            base_url="https://yourhost.com/path/to/api",
        )
        await client.variants.get_variant(
            variant_id="variant_id",
        )
        """
        _response = await self._client_wrapper.httpx_client.request(
            "GET",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_base_url()}/", f"variants/{variant_id}"
            ),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(AppVariantResponse, _response.json())  # type: ignore
        if _response.status_code == 422:
            raise UnprocessableEntityError(pydantic.parse_obj_as(HttpValidationError, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def start_variant(
        self,
        variant_id: str,
        *,
        action: VariantAction,
        env_vars: typing.Optional[DockerEnvVars] = OMIT,
    ) -> Uri:
        """
        Start a variant of an app.

        Args:
        variant_id (str): The ID of the variant to start.
        action (VariantAction): The action to perform on the variant (start).
        env_vars (Optional[DockerEnvVars], optional): The environment variables to inject to the Docker container. Defaults to None.
        stoken_session (SessionContainer, optional): The session container. Defaults to Depends(verify_session()).

        Returns:
        URI: The URL of the started variant.

        Raises:
        HTTPException: If the app container cannot be started.

        Parameters:
            - variant_id: str.

            - action: VariantAction.

            - env_vars: typing.Optional[DockerEnvVars].
        ---
        from agenta import VariantAction, VariantActionEnum
        from agenta.client import AsyncAgentaApi

        client = AsyncAgentaApi(
            api_key="YOUR_API_KEY",
            base_url="https://yourhost.com/path/to/api",
        )
        await client.variants.start_variant(
            variant_id="variant_id",
            action=VariantAction(
                action=VariantActionEnum.START,
            ),
        )
        """
        _request: typing.Dict[str, typing.Any] = {"action": action}
        if env_vars is not OMIT:
            _request["env_vars"] = env_vars
        _response = await self._client_wrapper.httpx_client.request(
            "PUT",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_base_url()}/", f"variants/{variant_id}"
            ),
            json=jsonable_encoder(_request),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(Uri, _response.json())  # type: ignore
        if _response.status_code == 422:
            raise UnprocessableEntityError(pydantic.parse_obj_as(HttpValidationError, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def remove_variant(self, variant_id: str) -> typing.Any:
        """
        Remove a variant from the server.
        In the case it's the last variant using the image, stop the container and remove the image.

        Arguments:
        app_variant -- AppVariant to remove

        Raises:
        HTTPException: If there is a problem removing the app variant

        Parameters:
            - variant_id: str.
        ---
        from agenta.client import AsyncAgentaApi

        client = AsyncAgentaApi(
            api_key="YOUR_API_KEY",
            base_url="https://yourhost.com/path/to/api",
        )
        await client.variants.remove_variant(
            variant_id="variant_id",
        )
        """
        _response = await self._client_wrapper.httpx_client.request(
            "DELETE",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_base_url()}/", f"variants/{variant_id}"
            ),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(typing.Any, _response.json())  # type: ignore
        if _response.status_code == 422:
            raise UnprocessableEntityError(pydantic.parse_obj_as(HttpValidationError, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def update_variant_parameters(
        self, variant_id: str, *, parameters: typing.Dict[str, typing.Any]
    ) -> typing.Any:
        """
        Updates the parameters for an app variant.

        Args:
        variant_id (str): The ID of the app variant to update.
        payload (UpdateVariantParameterPayload): The payload containing the updated parameters.
        stoken_session (SessionContainer, optional): The session container. Defaults to Depends(verify_session()).

        Raises:
        HTTPException: If there is an error while trying to update the app variant.

        Returns:
        JSONResponse: A JSON response containing the updated app variant parameters.

        Parameters:
            - variant_id: str.

            - parameters: typing.Dict[str, typing.Any].
        ---
        from agenta.client import AsyncAgentaApi

        client = AsyncAgentaApi(
            api_key="YOUR_API_KEY",
            base_url="https://yourhost.com/path/to/api",
        )
        await client.variants.update_variant_parameters(
            variant_id="variant_id",
            parameters={},
        )
        """
        _response = await self._client_wrapper.httpx_client.request(
            "PUT",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_base_url()}/",
                f"variants/{variant_id}/parameters",
            ),
            json=jsonable_encoder({"parameters": parameters}),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(typing.Any, _response.json())  # type: ignore
        if _response.status_code == 422:
            raise UnprocessableEntityError(pydantic.parse_obj_as(HttpValidationError, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def update_variant_image(
        self, variant_id: str, *, request: Image
    ) -> typing.Any:
        """
        Updates the image used in an app variant.

        Args:
        variant_id (str): The ID of the app variant to update.
        image (Image): The image information to update.

        Raises:
        HTTPException: If an error occurs while trying to update the app variant.

        Returns:
        JSONResponse: A JSON response indicating whether the update was successful or not.

        Parameters:
            - variant_id: str.

            - request: Image.
        ---
        from agenta import Image
        from agenta.client import AsyncAgentaApi

        client = AsyncAgentaApi(
            api_key="YOUR_API_KEY",
            base_url="https://yourhost.com/path/to/api",
        )
        await client.variants.update_variant_image(
            variant_id="variant_id",
            request=Image(
                docker_id="docker_id",
                tags="tags",
            ),
        )
        """
        _response = await self._client_wrapper.httpx_client.request(
            "PUT",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_base_url()}/",
                f"variants/{variant_id}/image",
            ),
            json=jsonable_encoder(request),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(typing.Any, _response.json())  # type: ignore
        if _response.status_code == 422:
            raise UnprocessableEntityError(pydantic.parse_obj_as(HttpValidationError, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def update_variant_url(
        self,
        variant_id: str,
        url: str,
    ):
        """
        ...
        """

        _request: typing.Dict[str, typing.Any] = {
            "url": url,
        }

        _response = await self._client_wrapper.httpx_client.request(
            "PUT",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_base_url()}/",
                f"variants/{variant_id}/url",
            ),
            json=jsonable_encoder(_request),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(typing.Any, _response.json())  # type: ignore
        if _response.status_code == 422:
            raise UnprocessableEntityError(pydantic.parse_obj_as(HttpValidationError, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def get_variant_revisions(
        self, variant_id: str
    ) -> typing.List[AppVariantRevision]:
        """
        Parameters:
            - variant_id: str.
        ---
        from agenta.client import AsyncAgentaApi

        client = AsyncAgentaApi(
            api_key="YOUR_API_KEY",
            base_url="https://yourhost.com/path/to/api",
        )
        await client.variants.get_variant_revisions(
            variant_id="variant_id",
        )
        """
        _response = await self._client_wrapper.httpx_client.request(
            "GET",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_base_url()}/",
                f"variants/{variant_id}/revisions",
            ),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(typing.List[AppVariantRevision], _response.json())  # type: ignore
        if _response.status_code == 422:
            raise UnprocessableEntityError(pydantic.parse_obj_as(HttpValidationError, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def get_variant_revision(
        self, variant_id: str, revision_number: int
    ) -> AppVariantRevision:
        """
        Parameters:
            - variant_id: str.

            - revision_number: int.
        ---
        from agenta.client import AsyncAgentaApi

        client = AsyncAgentaApi(
            api_key="YOUR_API_KEY",
            base_url="https://yourhost.com/path/to/api",
        )
        await client.variants.get_variant_revision(
            variant_id="variant_id",
            revision_number=1,
        )
        """
        _response = await self._client_wrapper.httpx_client.request(
            "GET",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_base_url()}/",
                f"variants/{variant_id}/revisions/{revision_number}",
            ),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(AppVariantRevision, _response.json())  # type: ignore
        if _response.status_code == 422:
            raise UnprocessableEntityError(pydantic.parse_obj_as(HttpValidationError, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)
