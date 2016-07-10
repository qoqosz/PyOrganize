import re


class Alias:
    def __init__(self, alias_file):
        self.alias = {}
        self.read(alias_file)

    def read(self, alias_file):
        self.alias = {}
        with open(alias_file, 'r') as f:
            for line in f:
                a = re.search(r'"(.*?)":"(.*?)"', line)
                if a:
                    short, long = a.groups()
                    self.alias[short] = long

    def get(self, name):
        return self.alias.get(name)
