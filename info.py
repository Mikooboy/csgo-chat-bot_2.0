import requests
import shlex
from bs4 import BeautifulSoup
from config import settings as cfg
from math import *
import time
from threading import Thread
from texttable import Texttable
from pydicti import dicti
import re
from time import sleep

def run(tn, command):
	try:
		cmd_s = command + "\n"
		tn.write(cmd_s.encode('utf-8'))
	except:
		pass

def get_players_and_map(tn):
    status_start = 0
    player_lines = []

    run(tn, "status")
    lines = []
    line = ""

    while ("#end" not in line):
        if ("Not connected to server" in line):
            raise Exception('Not connected to server')
        result = tn.expect([b"\r\n"])
        line = result[2].decode("utf-8").splitlines()
        line = line[len(line) - 1]
        lines.append(line)

    lines.pop(len(lines) - 1)

    j = 0
    for i in lines:
        if "# userid" in i.lower():
            status_start = j
        j = j + 1

    player_lines = lines[status_start + 1:]

    for i in lines:
        if "map" in i.lower():
            matching_map = i

    for i in player_lines:
        i = i.replace("\\", "")

    mapName = matching_map.split()
    mapName = mapName[2]
    return [player_lines, mapName]
        

def steamid_to_64bit(steamid):
    steam64id = 76561197960265728 # I honestly don't know where
                                    # this came from, but it works...
    id_split = steamid.split(":")
    steam64id += int(id_split[2]) * 2 # again, not sure why multiplying by 2...
    if id_split[1] == "1":
        steam64id += 1
    return steam64id

def parse_status_id(player_line):
    line_split = player_line.split()
    status_id = line_split[2]
    return status_id

def parse_name(player_line):
    line_split = re.sub(r'^.*?"', '"', player_line)
    line_split = line_split[1:]
    line_split = line_split[:line_split.rindex('"')]
    name = line_split
    return name

def parse_steamId(player_line):
    line_split = re.sub(r'^.*? STEAM_', 'STEAM_', player_line)
    line_split = shlex.split(line_split)[0]
    playerId = line_split
    return playerId

def save_steamId(playerId64):
    try:
        file1 = open("SavedSteamIDs64.txt", "a+")
        file1.write(str(playerId64) + "\n")
        file1.close()
        return True
    except:
        pass

def get_saved_steamIDs():
    try:
        file1 = open("SavedSteamIDs64.txt", "r")
        content = file1.read().splitlines()
        return content
    except:
        pass

def get_hours_other_methods(steamId):
    # Try to get hours from favourite game
    try:
        headers = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
        }

        url3 = "http://steamcommunity.com/profiles/" + str(steamId)

        result = requests.get(url3, headers=headers, timeout=1)
        soup = BeautifulSoup(result.content, 'lxml')

        div1 = soup.find('div', {'class' : 'favoritegame_showcase'})
        game = div1.find('a', {'class' : 'whiteLink'}, recursive=True)
        game = game.contents[0].replace("\t", "")
        game = game.strip()

        if (game == "Counter-Strike: Global Offensive"):
            hours = div1.find('div', {'class' : 'value'}, recursive=True)
            hours = hours.text
            return hours
    except:
        pass

    # Try to get hours from review
    try:
        headers = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
        }

        url3 = "http://steamcommunity.com/profiles/" + str(steamId) + "/reviews"

        result = requests.get(url3, headers=headers, timeout=1)
        soup = BeautifulSoup(result.content, 'lxml')

        div1 = soup.find('a', {'href' : 'https://steamcommunity.com/app/730'})
        hours = div1.parent.parent
        hours = hours.find('div', {'class' : 'hours'}, recursive=True)
        hours = hours.text.replace("\t", "")
        hours = hours.strip().split()[0]
        hours = hours.split(".")[0]
        return hours
    except:
        pass

def get_faceit_lvl(i):
    try:
        playerId = parse_steamId(i)
        playerId64 = steamid_to_64bit(playerId)

        level = "N/A"
        mmr = "N/A"

        try:
            headers = {
                'accept': 'application/json',
                'Authorization': cfg.faceit_api_key,
            }

            params = (
                ('game', 'csgo'),
                ('game_player_id', playerId64),
            )

            response = requests.get('https://open.faceit.com/data/v4/players', headers=headers, params=params, timeout=10)
            response = response.json()
            level = response['games']['csgo']['skill_level']
            mmr = response['games']['csgo']['faceit_elo']

            if int(mmr) < 1:
                mmr = "N/A"
        except:
            pass

    except:
        pass

    return level, mmr

def get_acc_value(id):
    try:
        headers = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
        }

        url3 = "https://steamid.pro/lookup/" + str(id)

        result = requests.get(url3, headers=headers, timeout=3)
        soup = BeautifulSoup(result.content, 'lxml')

        span = soup.find('span', {'class' : 'number-price'})
        acc_value = span.text
        acc_value = "~" + acc_value

        if (acc_value == "~$1"):
            acc_value = "N/A"

        return acc_value
    except:
        return "N/A"

def get_steam_stats(i, mapName, index):
    kdratio 	= "N/A" # Kill Death Ratio
    timeplayed 	= "N/A" # time played
    server_t    = "N/A"
    rounds 		= "N/A"
    hs 			= "N/A"
    seen        = ""

    info 		= "N/A"
    acc_value   = "N/A"
    components  = []
    game_info 	= True
    hour_info 	= True
    hours       = 0

    try:
        status_id = parse_status_id(i)
        name = parse_name(i)
        playerId = parse_steamId(i)
        playerId64 = steamid_to_64bit(playerId)

        t = ThreadWithReturnValue(target=get_acc_value, args=(playerId64, ))
        t.start()

        try:
            if (str(playerId64) in get_saved_steamIDs()):
                seen = "Yes"
            else:
                save_steamId(playerId64)
        except:
            pass

        key = cfg.steam_api_key

        url 	= 'https://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid=730&key=' + key + '&steamid='
        url2 	= 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=' + key + '&steamid='
        final_url 	= url + str(playerId64)
        final_url2 	= url2 + str(playerId64)

        try:
            r = requests.get(final_url, timeout=2).json()
            stats = {
                'total_kills' 	: "N/A",
                'total_deaths' 	: "N/A",
                'headshots' 	: "N/A",
                'map_rounds'	: "N/A",
            }

            for j in (r['playerstats']['stats']):
                id = j['name']
                if (id == "total_kills"):
                    stats['total_kills'] = j['value']

            for j in (r['playerstats']['stats']):
                id = j['name']
                if (id == "total_deaths"):
                    stats['total_deaths'] = j['value']
            
            for j in (r['playerstats']['stats']):
                id = j['name']
                if (id == "total_kills_headshot"):
                    stats['headshots'] = j['value']

            for j in (r['playerstats']['stats']):
                id = j['name']
                if ("rounds" in id) and (mapName in id):
                    stats['map_rounds'] = j['value']

            for j in (r['playerstats']['stats']):
                id = j['name']
                if (id == "total_time_played"):
                    server_t = j['value']

            kd = stats['total_kills']/stats['total_deaths']
            hs = (stats['headshots']/stats['total_kills'])*100

            server_t = (server_t / 60) / 60
            server_t = floor(server_t)

            if (server_t <= 1):
                server_t = "N/A"
            else:
                server_t = f"{server_t:,}"

            rounds 	= stats['map_rounds']
            kdratio = str("{:.2f}".format(kd))
            hs 		= str(floor(hs))
        except:
            game_info = False
            
        try:
            r2 = requests.get(final_url2, timeout=2).json()
            games = r2['response']['games'] #total time played

            for j in games:
                id = j['appid']
                if (id == 730):
                    time_played = j['playtime_forever']

            hours = time_played/60
        except:
            hour_info = False
        
        try:
            timeplayed = "N/A"
            if (hours >= 1):
                hour_info = True
                timeplayed = floor(hours)
                timeplayed = f"{timeplayed:,}"
            else:
                hours = get_hours_other_methods(playerId64)
                if (hours != None):
                    hour_info = True
                    timeplayed = hours
        except:
            pass

        try:
            rounds = f"{rounds:,}"
        except:
            pass

        # get account value from the thread
        acc_value = t.join()
    except:
        pass

    return [str(status_id), str(name), str(timeplayed), str(server_t), str(kdratio), str(hs), str(mapName), str(rounds), str(seen), str(acc_value)]



class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return



class player_info():
    def __init__(self, id, name, hours, server_t, kd, hs, map, rounds, seen, acc_val, faceit, mmr):
        self.id = id
        self.name = name
        self.hours = hours
        self.server_t = server_t
        self.kd = kd
        self.hs = hs
        self.map = map
        self.rounds = rounds
        self.seen = seen
        self.acc_val = acc_val
        self.faceit = faceit
        self.mmr = mmr

    def to_string(self):
        hour_info = True
        game_info = True

        strings = {
            'name'        : f"{self.name}",
            'hours'       : f" | Hours: {self.hours}",
            'server_t'    : f" | Active hours: {self.server_t}",
            'kd'          : f" | K/D: {self.kd}",
            'hs'          : f" | HS: {self.hs}%",
            'faceit'      : f" | Faceit lvl: {self.faceit}",
            'mmr'         : f" | Faceit elo: {self.mmr}",
            'rounds'      : f" | {self.map}: {self.rounds} rounds",
            'acc_value'   : f" | Acc value: {self.acc_val}",
        }
        
        index = 0
        for i in strings:
            if "N/A" in strings[i] and index != 5 and index != 8:
                if index == 1:
                    hour_info = False
                if index == 2 or index == 3 or index == 4:
                    game_info = False
                strings[i] = ""
            index += 1

        if hour_info == False and game_info == False:
            string = strings['name'] + " | Game and Hour info private" + strings['faceit'] + strings['mmr'] + strings['acc_value']
        elif game_info == False:
            string = strings['name'] + strings['hours'] + " | Game info private" + strings['faceit'] + strings['mmr'] + strings['acc_value']
        else:
            string = strings['name'] + strings['hours'] + strings['server_t'] + strings['kd'] + strings['hs'] + strings['faceit'] + strings['mmr'] + strings['rounds'] + strings['acc_value']

        return string

    # returns everything but self.map
    def get_list(self, i):
        list = [i, self.id, self.name, self.hours + "h", self.server_t + "h", self.kd, self.hs + "%", self.rounds, self.seen, self.acc_val, self.faceit, self.mmr]

        for i in list:
            if "N/A" in str(i):
                list[list.index(i)] = ""

        return list



class info_handler():
    def __init__(self, tn):
        self.tn = tn
        self.player_list = {}
        self.table_list = dicti()
        self.map = "N/A"

    def request_info(self, name):
        try:
            name = name.replace("\\", "")

            for i in self.player_list:
                if name.lower() == i.lower():
                    name = i
                    break
                elif name.lower() in i.lower():
                    name = i

            if (name != "*all*") & (name in self.player_list):
                player = self.player_list[name]
                msg = player.to_string()
                msg = msg.replace("\"", "")
                return msg
            elif (name == "*all*"):
                self.fetch_info()
                return None
            else:
                return "Error: Invalid name"
        except:
            print("Error: Couldn't retrieve info")
            return None

    def threaded_fetch(self, i, mapName, index):
        t1 = ThreadWithReturnValue(target=get_steam_stats, args=(i, mapName, index))
        t1.start()
        t2 = ThreadWithReturnValue(target=get_faceit_lvl, args=(i,))
        t2.start()

        stats = t1.join()
        faceit = t2.join()
        level = faceit[0]
        mmr = faceit[1]

        stats.append(str(level))
        stats.append(str(mmr))
        return stats

    def fetch_info(self):
        self.remove_all_players()

        PlayersAndMap = get_players_and_map(self.tn)
        players = PlayersAndMap[0]
        mapName = PlayersAndMap[1]
        self.map = mapName

        threads = []

        index = 0
        print("Fetching info from APIs...")
        for i in players:
            if not "STEAM_" in i:
                continue
            index += 1
            
            t = ThreadWithReturnValue(target=self.threaded_fetch, args=(i, mapName, index))
            threads.append(t)

        [ t.start() for t in threads]

        for t in threads:
            stats = t.join()  
            self.add_player(*stats)
        
        self.draw_table()

    def remove_all_players(self):
        self.player_list = {}
        self.table_list = dicti()

    def add_player(self, id, name, hours, server_t, kd, hs, map, rounds, seen, acc_val, faceit, mmr):
        info = player_info(id, name, hours, server_t, kd, hs, map, rounds, seen, acc_val, faceit, mmr)
        self.player_list[name] = info

    def draw_table(self):
        table = Texttable()
        table.set_max_width(250)
        table.header([" ", "id", "Name", "Hours", "Active", "K/D", "HS%", "Rounds", "Seen?", "Acc Value", "Faceit", "elo"])
        table.set_cols_dtype(['t', 't', 't', 't', 't', 't', 't', 't', 't', 't', 't', 't'])

        j = 0
        for i in self.player_list:
            j += 1
            self.table_list[i] = self.player_list[i].get_list(j)
        
        self.table_list = dicti(sorted(self.table_list.items(), key=lambda item: item[1]))

        for i in self.table_list:
            table.add_row(self.table_list[i])

        print(table.draw())
