import re

class Options:
    def __init__(self, options_file):
        self.options = {}
        self.read(options_file)

    def read(self, options_file):
        self.options = {}

        with open(options_file, 'r') as f:
            for line in f:
                a = re.search('^\'(.*?)\': (.*?)$', line)
                if a:
                    opt, val = a.groups()
                    if val.lower() in ['true', 'false']:
                        val = val.lower() in ['true']

                    self.options[opt] = val

    def get(self):
        return self.options
