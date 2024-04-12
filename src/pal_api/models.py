from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ServerInfo:
    version: str
    server_name: str
    description: str

    @classmethod
    def from_dict(cls, data: dict) -> ServerInfo:
        data["server_name"] = data.pop("servername")
        return cls(**data)


@dataclass
class Player:
    name: str
    player_id: int
    user_id: str
    ip: str
    ping: float
    location_x: float
    location_y: float
    level: int


@dataclass
class PlayerList:
    players: list[Player] = field(default_factory=list)

    def __iter__(self):
        return iter(self.players)

    @classmethod
    def from_dict(cls, data: dict) -> PlayerList:
        players = []
        for player in data["players"]:
            player["player_id"] = player.pop("playerId")
            if player["player_id"] == "None":
                continue
            player["player_id"] = abs(int(player["player_id"]))
            player["user_id"] = player.pop("userId")
            player["location_x"] = player.pop("location_x")
            player["location_y"] = player.pop("location_y")
            players.append(Player(**player))
        return cls(players=players)


@dataclass
class ServerMetrics:
    server_fps: int
    current_player_num: int
    server_frame_time: float
    max_player_num: int
    uptime: int

    @classmethod
    def from_dict(cls, data: dict) -> ServerMetrics:
        data["server_fps"] = data.pop("serverfps")
        data["current_player_num"] = data.pop("currentplayernum")
        data["server_frame_time"] = data.pop("serverframetime")
        data["max_player_num"] = data.pop("maxplayernum")
        return cls(**data)
