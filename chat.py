from time import sleep
from threading import Thread

def run(tn, command):
	try:
		cmd_s = command + "\n"
		tn.write(cmd_s.encode('utf-8'))
	except:
		pass

class chat_queue_handler():
    def __init__(self, tn):
        self.tn = tn
        self.queue = []

        thread = Thread(target=self.loop, name="chat_queue_handler.loop()")
        thread.start()

    def loop(self):
        while True:
            if len(self.queue) > 0:
                sleep(0.7)
                self.send_msg()
            else:
                sleep(0.1)

    def send_msg(self):
        run(self.tn, "say \"" + "​" + self.queue[0] + "\"")
        del self.queue[0]

    def send_clear_msg(self):
        sleep(0.01)
        run(self.tn, "say \"" + "​" + (50*" ") + "\"")

    def add_msg(self, msg):
        self.queue.append(msg)