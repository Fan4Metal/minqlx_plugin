"""
This is a plugin for minqlx created by Metal Fan (fan4_metal@mail.ru)
Copyright (c) 2025 Metal Fan

Version 0.2

Its purpose is to display welcome message and some information about the players.
"""

import minqlx
import requests
import re


class welcome_stats(minqlx.Plugin):
    def __init__(self):
        super().__init__()

        # Правильная регистрация команды!
        self.add_command(("info", "stats"), self.cmd_info, usage="<id | steam_id>")

        self.add_hook("player_connect", self.handle_player_connect, priority=minqlx.PRI_LOWEST)

    def handle_player_connect(self, player):
        if not player or player.steam_id < 10000000000000000:
            return

        sid = player.steam_id
        name = player.clean_name

        @minqlx.thread
        def fetch():
            data = self.get_ffa_data(sid)
            if not data:
                msg = f"^7Welcome, ^5{name}^7! Tracked games: ^1—^7, FFA ELO: ^1—"
            else:
                games = data["games"]
                elo = data["elo"]
                elo_str = f"^3{elo:^4}^7" if elo != "—" else "^1—^7"
                msg = f"^7Welcome, ^5{name}^7! Tracked games: ^2{games}^7, FFA ELO: {elo_str}"
            minqlx.CHAT_CHANNEL.reply(msg)

        fetch()

    def cmd_info(self, player, msg, channel):
        if len(msg) < 2:
            player.tell("^7Usage: ^2!info <id | steam_id>")
            return minqlx.RET_STOP_EVENT

        query = " ".join(msg[1:]).strip()

        # 1. Short ID (0-63)
        if re.fullmatch(r"\d{1,2}", query):
            cid = int(query)
            target = minqlx.Player(cid) if 0 <= cid < 64 else None
            if target and target.steam_id >= 10000000000000000:
                self.show_stats(target.steam_id, target.clean_name)
                return minqlx.RET_STOP_EVENT
            player.tell(f"^3Player ^7{cid} ^3not found or is a bot.")
            return minqlx.RET_STOP_EVENT

        # 2. Full SteamID
        if re.fullmatch(r"\d{17}", query):
            sid = int(query)
            name = next((p.clean_name for p in minqlx.Player.iter_players() if p.steam_id == sid), f"Player {sid}")
            self.show_stats(sid, name)
            return minqlx.RET_STOP_EVENT

        player.tell("^3Invalid input. Use short ID (0-63) or full 17-digit SteamID.")
        return minqlx.RET_STOP_EVENT

    def show_stats(self, steam_id, name):
        @minqlx.thread
        def fetch():
            data = self.get_ffa_data(steam_id)
            if not data:
                msg = f"^5{name}^7 (^3{steam_id}^7) — ^1no FFA data on qlstats.net"
            else:
                games = data["games"]
                elo = data["elo"]
                elo_str = f"^3{elo:^4}^7" if elo != "—" else "^1—^7"
                msg = f"^5{name}^7 => Tracked games: ^2{games}^7, FFA ELO: {elo_str}"
            minqlx.CHAT_CHANNEL.reply(msg)

        fetch()

    def get_ffa_data(self, steam_id):
        try:
            r = requests.get(f"http://qlstats.net/elo/{steam_id}", timeout=6)
            if r.status_code != 200:
                return None
            player = r.json().get("players", [{}])[0]
            ffa = player.get("ffa", {})
            return {"games": ffa.get("games", 0), "elo": ffa.get("elo", "—")}
        except:
            return None
