# pal_api
API Wrapper for Palworld Dedicated Server  
### Usage
_Install_  
```sh
pip install pal_api
### Option ###
pip install ujson
```
_Sync_
```python
from pal_api import PalApiClient
client = PalApiClient(password="password")
print(client.get_server_info())

# with Context Manager
with PalApiClient(password="password") as client:
    print(client.get_server_info())
```
_Async_
```python
import asyncio
from pal_api import AsyncPalApiClient

async def main():
    client = AsyncPalApiClient(password="password")
    print(await client.get_server_info())
    await client.close()

asyncio.run(main())

# with Context Manager
async def main():
    async with AsyncPalApiClient(password="password") as client:
        print(await client.get_server_info())

asyncio.run(main())
```
_Options and Default Values for the Class_
|name|class|default|
|---|---|---|
|host|str|"localhost"|
|port|int|8212|
|username|str|"admin"|
|password|str||
|timeout|int|5|
|session(async only)|aiohttp.ClientSession|None|

_method_
```python
get_server_info() -> ServerInfo
get_player_list() -> PlayerList
get_server_settings() -> dict
get_server_metrics() -> ServerMetrics
announce_message(message: str) -> None
kick_player(userid: str, message: str = "") -> None
ban_player(userid: str, message: str = "") -> None
unban_player(userid: str) -> None
save_world() -> None
shutdown_server(waittime: int = 10, message: str | None = None, force: bool = False) -> None
```

### やってること・その他
- playerIdが負の数が返ってくることがある -> とりあえず正の数に直してます
- ログイン中にSteamの名前が返ってくる -> playerIdがNoneのものは除外しています
- BanするとbanlistにはIDが乗るが、効いてなさそう(コミュニティサーバー未確認)
- また、間違ったIDを送ってもとりあえずリストには乗る
- Banするときにメッセージを送れるが、どこに表示されているのか不明

License MIT ©[Charahiro-tan](https://twitter.com/__Charahiro)
