from __future__ import annotations

import base64
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .errors import RequestError, UnAuthorizedError
from .models import PlayerList, ServerInfo, ServerMetrics

try:
    import ujson as json
except ImportError:
    import json


class PalApiClient:
    def __init__(
        self,
        *,
        host: str = "localhost",
        port: int = 8212,
        username: str = "admin",
        password: str,
        timeout: int | float = 5,
    ):
        self.host = host
        self.port = port
        self.timeout = timeout

        self._baseurl = f"http://{self.host}:{self.port}/v1/api"
        self._credentials = base64.b64encode(f"{username}:{password}".encode()).decode()

    def __enter__(self) -> PalApiClient:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        pass

    def _request(self, method: str, path: str, data: dict | None = None) -> dict:
        url = self._baseurl + path
        headers = {"Authorization": f"Basic {self._credentials}"}

        data_encoded = None
        if method == "POST":
            if data is None:
                data_encoded = "".encode()
            else:
                data_encoded = json.dumps(data).encode()
                headers["Content-Type"] = "application/json"

        request = Request(url, data=data_encoded, headers=headers, method=method)

        try:
            with urlopen(request, timeout=self.timeout) as response:
                res = response.read()
                if res == b"OK":
                    return {}
                return json.loads(res)
        except HTTPError as e:
            if e.code == 400:
                raise RequestError("Bad request") from e
            elif e.code == 401:
                raise UnAuthorizedError("Unauthorized") from e
            else:
                raise RequestError(f"Unexpected response code: {e.code}") from e
        except URLError as e:
            raise RequestError(f"Failed to connect to {url}") from e

    def get_server_info(self) -> ServerInfo:
        PATH = "/info"
        res = self._request("GET", PATH)
        return ServerInfo.from_dict(res)

    def get_player_list(self) -> PlayerList:
        PATH = "/players"
        res = self._request("GET", PATH)
        return PlayerList.from_dict(res)

    def get_server_settings(self) -> dict:
        PATH = "/settings"
        return self._request("GET", PATH)

    def get_server_metrics(self) -> ServerMetrics:
        PATH = "/metrics"
        res = self._request("GET", PATH)
        return ServerMetrics.from_dict(res)

    def announce_message(self, message: str) -> None:
        PATH = "/announce"
        data = {"message": message}
        self._request("POST", PATH, data)

    def kick_player(self, userid: str, message: str = "") -> None:
        PATH = "/kick"
        data = {"userid": userid, "message": message}
        self._request("POST", PATH, data)

    def ban_player(self, userid: str, message: str = "") -> None:
        PATH = "/ban"
        data = {"userid": userid, "message": message}
        self._request("POST", PATH, data)

    def unban_player(self, userid: str) -> None:
        PATH = "/unban"
        data = {"userid": userid}
        self._request("POST", PATH, data)

    def save_world(self) -> None:
        PATH = "/save"
        self._request("POST", PATH)

    def shutdown_server(
        self, waittime: int = 10, message: str | None = None, force: bool = False
    ) -> None:
        if force:
            PATH = "/stop"
            self._request("POST", PATH)
            return
        PATH = "/shutdown"
        if message is None:
            message = f"Server will shutdown in {waittime} seconds."
        data = {"waittime": waittime, "message": message}
        self._request("POST", PATH, data)
