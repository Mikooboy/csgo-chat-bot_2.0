from threading import Thread
from config import settings as cfg
from time import sleep

def run(tn, command):
	try:
		cmd_s = command + "\n"
		tn.write(cmd_s.encode('utf-8'))
	except:
		pass

class clan_handler():
    def __init__(self, tn):
        self.tn = tn
        self.id_list = cfg.clan_id_list

        t = Thread(target=self.change_clan_loop, name="clan_handler.change_clan_loop()")
        t.start()

    def change_clan_loop(self):
        i = 0
        while (True):
            try:
                run(self.tn, "cl_clanid \"" + str(self.id_list[i]) + "\"")
                #print(str(self.id_list[i]))
                if (i == (len(self.id_list) - 1)):
                    i = 0
                else:
                    i += 1
            except:
                pass
            sleep(0.4)