import difflib
from time import sleep


class CommandController:

    def __init__(self, interface):
        self.buy = interface
        self.commands = {}
        self.parse()

    def find_match(self, cmd):
        matches = difflib.get_close_matches(cmd, list(self.commands.keys()))
        return matches

    def parse(self):
        with open("commands/commands.txt") as file:
            data = file.read().split("\n")
            data = list(filter(lambda d: not d.startswith("#") and d.strip() != "", data))

            for _ in range(data.count(".")):
                cmd = {data[0]: data[1:data.index(".")]}
                self.commands.update(cmd)
                data = data[data.index(".") + 1:]

    def run(self, cmd):
        script = self.commands.get(cmd)
        if script is None:
            print("Unknown command!")
            return

        for s in script:
            if s.startswith("BUY"):
                item = s.replace("BUY ", "", 1)[1:-1]
                self.buy.buy(item)
            elif s.startswith("DROP"):
                slot = int(s.split(" ")[1])
                self.buy.drop(slot)
            elif s.startswith("LOOK"):
                direc = s.split(" ")[1]
                pass
            elif s == "RANDOM":
                self.buy.random_buy()
