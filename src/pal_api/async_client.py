from __future__ import annotations

from aiohttp import BasicAuth, ClientSession, ClientConnectionError

from .errors import RequestError, UnAuthorizedError
from .models import PlayerList, ServerInfo, ServerMetrics

try:
    import ujson as json
except ImportError:
    import json


class AsyncPalApiClient:
    def __init__(
        self,
        *,
        host: str = "localhost",
        port: int = 8212,
        username: str = "admin",
        password: str,
        timeout: int | float = 5,
        session: ClientSession | None = None,
    ) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout

        self._base_url = f"http://{self.host}:{self.port}/v1/api"
        self._credentials = BasicAuth(username, password, "utf-8")
        self._session: ClientSession | None = session

    async def __aenter__(self) -> AsyncPalApiClient:
        if self._session is None:
            self._session = ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.close()

    async def _request(self, method: str, path: str, data: dict | None = None) -> dict:
        if self._session is None:
            self._session = ClientSession()

        url = self._base_url + path

        data_encoded = None
        if method == "POST":
            if data is None:
                data_encoded = "".encode()
            else:
                data_encoded = json.dumps(data).encode()
        try:
            async with self._session.request(
                method,
                url,
                auth=self._credentials,
                data=data_encoded,
                timeout=self.timeout,
            ) as response:
                if response.status == 200:
                    res = await response.text()
                    if res == "OK":
                        return {}
                    return json.loads(res)
                elif response.status == 401:
                    raise UnAuthorizedError("Unauthorized")
                elif response.status == 400:
                    raise RequestError("Bad request")
                else:
                    raise RequestError(f"Unexpected response code: {response.status}")
        except ClientConnectionError as e:
            raise RequestError(f"Failed to connect to {url}") from e

    async def close(self) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()

    async def get_server_info(self) -> ServerInfo:
        PATH = "/info"
        res = await self._request("GET", PATH)
        return ServerInfo.from_dict(res)

    async def get_player_list(self) -> PlayerList:
        PATH = "/players"
        res = await self._request("GET", PATH)
        return PlayerList.from_dict(res)

    async def get_server_settings(self) -> dict:
        PATH = "/settings"
        return await self._request("GET", PATH)

    async def get_server_metrics(self) -> ServerMetrics:
        PATH = "/metrics"
        res = await self._request("GET", PATH)
        return ServerMetrics.from_dict(res)

    async def announce_message(self, message: str) -> None:
        PATH = "/announce"
        data = {"message": message}
        await self._request("POST", PATH, data)

    async def kick_player(self, userid: str, message: str = "") -> None:
        PATH = "/kick"
        data = {"userid": userid, "message": message}
        await self._request("POST", PATH, data)

    async def ban_player(self, userid: str, message: str = "") -> None:
        PATH = "/ban"
        data = {"userid": userid, "message": message}
        await self._request("POST", PATH, data)

    async def unban_player(self, userid: str) -> None:
        PATH = "/unban"
        data = {"userid": userid}
        await self._request("POST", PATH, data)

    async def save_world(self) -> None:
        PATH = "/save"
        await self._request("POST", PATH)

    async def shutdown_server(
        self, waittime: int = 10, message: str | None = None, force: bool = False
    ) -> None:
        if force:
            PATH = "/stop"
            await self._request("POST", PATH)
            return
        PATH = "/shutdown"
        if message is None:
            message = f"Server will shutdown in {waittime} seconds."
        data = {"waittime": waittime, "message": message}
        await self._request("POST", PATH, data)
