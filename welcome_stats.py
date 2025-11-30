# This is a plugin for minqlx created by Metal Fan (fan4_metal@mail.ru)
# Copyright (c) 2025 Metal Fan
#
# Version 0.1
#
# Its purpose is to display welcome message and some information about the players.

import minqlx
import requests


class welcome_stats(minqlx.Plugin):
    def __init__(self):
        super().__init__()
        self.add_hook("player_connect", self.handle_player_loaded, priority=minqlx.PRI_LOWEST)

    def handle_player_loaded(self, player):
        # Ignore bots
        if not player or player.steam_id < 10000000000000000:
            return

        sid = player.steam_id
        name = player.clean_name

        # request data from qlstats.net
        @minqlx.thread
        def get_ffa_data():
            try:
                url = f"http://qlstats.net/elo/{sid}"
                r = requests.get(url, timeout=6)
                if r.status_code != 200:
                    msg = f"Welcome, ^5{name}^7! Games tracked: ^1—^7, ELO FFA: ^1—"
                    minqlx.CHAT_CHANNEL.reply(msg)
                    return

                data = r.json()
                player_data = data.get("players", [{}])[0]
                ffa = player_data.get("ffa", {})
                games = ffa.get("games", 0)
                elo = ffa.get("elo", "—")

                msg = f"^7Welcome, ^5{name}^7! Games tracked: ^2{games}^7, ELO FFA: ^3{elo}^7"
                minqlx.CHAT_CHANNEL.reply(msg)

            except Exception:
                # Если ошибка — показываем тире
                msg = f"^7Welcome, ^5{name}^7! Games tracked: ^1—^7, ELO FFA: ^1—"
                minqlx.CHAT_CHANNEL.reply(msg)

        get_ffa_data()
