# rewrite of csgo bot
import sys
from threading import Thread
import os
from time import sleep
import telnetlib
from math import *
import re

# local files
from config import settings as cfg
import chat
import info
import connect
import clan
import calculator
import dz


def help():
	if (len(sys.argv) > 1):
		if (sys.argv[1] == "-h" or sys.argv[1] == "--help"):
			print("Run with no arguments to initiate and connect to csgo")
			print("Make sure you set up csgo to receive connections with this launch option: -netconport " + str(cfg.tn_port))


def clear():
	return os.system('cls||clear')
clear()

def run(tn, command):
	try:
		cmd_s = command + "\n"
		tn.write(cmd_s.encode('utf-8'))
	except:
		try:
			tn = telnetlib.Telnet(cfg.tn_host, cfg.tn_port)
		except ConnectionRefusedError:
			pass

def main():
	# Prints the help if program was run with -h or --help
	help()

	print("Trying " + cfg.tn_host + ":" + cfg.tn_port)

	while True:
		try:
			tn = telnetlib.Telnet(cfg.tn_host, cfg.tn_port)
			tn2 = telnetlib.Telnet(cfg.tn_host, cfg.tn_port)
			break
		except ConnectionRefusedError:
			sleep(3)
			pass

	print("Successfully Connected!")
	sleep(1)
	clear()
	print("Listening for commands...")

	chat_queue 			= chat.chat_queue_handler(tn)
	clan_handler 		= clan.clan_handler(tn)
	info_handler 		= info.info_handler(tn)
	connect_handler 	= connect.connect_handler(tn)
	calc_handler 		= calculator.Calc()
	dz_handler 			= dz.dz_handler(tn)

	ban_list = cfg.clear_list

	while True:
		try:
			# Capture console output until we encounter new line
			result = tn.expect([b"\r\n"])
			last_line = result[2].decode("utf-8").splitlines()
			last_line = last_line[len(last_line) - 1]

			# Chat message detected
			# First special character always appears in chat messages
			# Second special character is always in the bot messages so we can ignore them
			if "‎" in last_line and "​" not in last_line:
				whole_line = last_line
				last_line = last_line.split("‎")

				sender = str(last_line[0])
				sender = sender.replace("(Counter-Terrorist) ", "")
				sender = sender.replace("(Terrorist) ", "")
				sender = sender.replace("*DEAD* ", "")
				sender = sender.replace("*DEAD*", "")
				sender = sender.replace("*SPEC* ", "")
				sender = sender.replace("(Spectator) ", "")

				message = str(last_line[1])
				message = re.sub(r'^.*? : ', '', message)
				message = re.sub(r"^\s+", "", message)

				# help
				if "!help" in message.lower():
					msg = "List of commands: !​info <name>, !calc <math>, !​tj, !​ulla, !help, !burn, !dz, !github" + " "
					chat_queue.add_msg(msg)

				# Player info
				elif "!info" in message.lower():
					name = message.lower().replace("!info ", "")
					msg = info_handler.request_info(name)
					if msg != None:
						chat_queue.add_msg(msg)

				# github
				elif "!github" in message.lower():
					chat_queue.add_msg(
						"https://github.com/Mikooboy/csgo-chat-bot_2.0")

				# Danger zone map cycle
				elif "!dz" in message.lower():
					chat_queue.add_msg(dz_handler.get_dz_map_cycle())
					print(dz_handler.get_dz_map_cycle())

				# calc
				elif "!calc" in message.lower():
					calc = message.replace("!calc ", "")
					try:
						answer = calc_handler.evaluate(calc)
						chat_queue.add_msg(str(answer))
					except:
						chat_queue.add_msg("Invalid equation. Example: !calc 5 + (3 - 2) * (5 / 2)")

				# mute
				elif "!mute" in message.lower() and sender == connect_handler.name:
					mute = message.lower().replace("!mute ", "")
					ban_list.append(mute)
					print(ban_list)

				# unmute
				elif "!unmute" in message.lower() and sender == connect_handler.name:
					unmute = message.lower().replace("!unmute ", "")
					ban_list.remove(unmute)
					print(ban_list)

				# clear
				else:
					for i in ban_list:
						if (i.lower() in sender.lower() or i.lower() in message.lower()) and (sender != connect_handler.name):
							t = Thread(target=chat_queue.send_clear_msg, name="chat_queue.send_clear_msg()")
							t.start()

			# Commands received from console and not chat
			elif "​" not in last_line:
				# connected to server
				if connect_handler.name + " connected." in last_line:
					connect_handler.clear_console()
					connect_handler.get_info(info_handler)

				# get player info list manually
				elif "!info" in last_line:
					try:
						info_handler.fetch_info()
					except:
						pass

				# toggle danger zone map notification
				elif "!dz_map" in last_line:
					toggle = dz_handler.auto_notification
					dz_handler.set_dz_map_notification(not toggle)
					toggle = dz_handler.auto_notification
					run(tn, "echo dz auto notification: " + str(toggle))

				# print current and the next danger zone map
				elif "!dz" in last_line:
					run(tn, f"echo {dz_handler.get_dz_map_cycle()}")
					print(dz_handler.get_dz_map_cycle())

				elif "!zeus_shot" in last_line:
					run(tn, "+attack")
					sleep(0.016)
					run(tn, "use weapon_taser")
					sleep(0.025)
					run(tn, "-attack;slot1")

				# mini/low jump
				elif "!lowjump" in last_line:
					run(tn, "+jump;+duck")
					sleep(0.02)
					run(tn, "-jump;-duck")

				# longjump
				elif "!lj" in last_line:
					run(tn, "+jump; +klook; -forward; +duck")
					sleep(0.03)
					run(tn, "-duck; -jump; -klook")

		except Exception as e:
			print(e)
			print("Trying to reconnect telnet...")
			while True:
				try:
					tn = telnetlib.Telnet(cfg.tn_host, cfg.tn_port)
					chat_queue.tn = tn
					clan_handler.tn = tn
					info_handler.tn = tn
					connect_handler.tn = tn
					dz_handler.tn = tn
					break
				except ConnectionRefusedError:
					sleep(3)
					pass
			print("Telnet reconnected")

main()