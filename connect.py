import shlex
import re

def run(tn, command):
	try:
		cmd_s = command + "\n"
		tn.write(cmd_s.encode('utf-8'))
	except:
		pass

class connect_handler():
    def __init__(self, tn):
        self.tn = tn

        run(self.tn, "name")
        result = tn.expect([b"- Current user name"])
        last_line = result[2].decode("utf-8").splitlines()
        last_line = last_line[len(last_line) - 1]
        name = fr'{last_line}'
        m = re.search(' = "(.+?)" \( ', name)
        if m:
            name = m.group(1)

        self.name = name

    def get_connect_name(self, line):
        name = line.replace(" connected.", "")
        return name

    def clear_console(self):
        run(self.tn, "clear")

    def get_info(self, info_handler):
        info_handler.fetch_info()
