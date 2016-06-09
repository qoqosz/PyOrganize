import interface
from utilities import *

if __name__ == '__main__':
	db = load('tasks.xml')
	ui = interface.Interface(db)
	ui.start()
	save(db)
