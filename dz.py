from math import *
import time
import datetime
from threading import Thread
from time import sleep

def run(tn, command):
	try:
		cmd_s = command + "\n"
		tn.write(cmd_s.encode('utf-8'))
	except:
		pass

class dz_handler():
    def __init__(self, tn):
        self.tn = tn
        self.auto_spawn = True
        self.auto_notification = True
        self.maps = ["Vineyard", "Sirocco", "Ember", "Blacksite"]

        self.update()

        t = Thread(target=self.dz_map_cycle_loop, name="dz_handler.dz_map_cycle_loop()")
        t.start()
        
    def update(self):
        self.timestamp = time.time() + 2
        self.current_time = datetime.datetime.fromtimestamp(self.timestamp)

        self.next_map_time = datetime.datetime.fromtimestamp(self.timestamp + 180 - self.timestamp % 180)
        self.next_map_time_seconds = (self.next_map_time.time().hour * 60 + self.next_map_time.time().minute) * 60 + self.next_map_time.time().second
        self.next_map_timedelta = (self.next_map_time - self.current_time).total_seconds()
        self.next_map_datetime = datetime.datetime.fromtimestamp((self.next_map_time - self.current_time).total_seconds())
        self.time_until_next_map = self.next_map_datetime.strftime("%M:%S")

        self.current_map_id = int((((self.next_map_time.timestamp() / 180) % 4) - 1) % 4 - 1)
        self.next_map_id = int((self.next_map_time.timestamp() / 180) % 4 - 1)

        self.current_map = self.maps[self.current_map_id]
        self.next_map = self.maps[self.next_map_id]

    def get_dz_map_cycle(self):
        self.update()
        return f"Map in rotation: {self.current_map}. Next map {self.next_map} in {self.time_until_next_map}"

    def dz_map_cycle_loop(self):
        while (True):
            self.update()
            sleep(self.next_map_timedelta + 0.5)
            self.update()
            if (self.auto_notification):
                run(self.tn, f"playerchatwheel CW.null \" DZ map changed to: {self.current_map} | Next map {self.next_map} in 03:00\"")
                print(f"DZ map changed to: {self.current_map} | Next map {self.next_map} in 03:00")

    def set_dz_map_notification(self, toggle):
        self.auto_notification = toggle