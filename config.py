#!/usr/bin/env python

class settings():
    steam_api_key = ''      # Steam api key for fetching game data for players
    faceit_api_key = ''     # faceit api key for fecting faceit lvl and elo for players
    clan_id_list = []       # list of clan ids to cycle
    tn_host = "127.0.0.1"   # CSGO host ip
    tn_port = "2121"        # CSGO telnet socket port
    clear_list = ["ez", ]   # Sends the chat clear message automatically when one of these is detected in the sender name or message