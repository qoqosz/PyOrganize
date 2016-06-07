import re
from utilities import *

class Interface:
	def __init__(self, db):
		self.db = db

	def start(self):
		self.show_all()
	
		while True:
			cmd = raw_input('> ')
			
			if cmd == 'quit':
				break
			elif cmd == 'list':
				self.show_all()
			elif cmd.startswith('done'):
				if not self.mark_done(cmd):
					print 'Cannot locate an item'
				else:
					self.show_all()
			elif cmd.startswith('undone'):
				if not self.mark_done(cmd, undo=True):
					print 'Cannot locate an item'
				else:
					self.show_all()
			elif re.search('\d+ add', cmd):
				if not self.add(cmd):
					print 'Cannot add task'
				else:
					self.show_all()
			elif cmd == 'save':
				save(self.db)

			elif cmd == 'help':
				print '- list : list all tasks'
				print '- done X : mark item no X as done'
				print '- undone X : mark item no X as undone'
				print '- X add Y : add action with a name Y to X'
				print '- X add proj Y : add project named Y to X'
			

	def show_all(self):
		i = 0
		for node in self.db.query_all():
			i += 1
			print str(i) + _format_item(node)

	def mark_done(self, cmd, undo=False):
		match = re.search('done (\d+)', cmd)

		if match:
			n = int(match.group(1))

			i = 0
			for node in self.db.query_all():
				i += 1
				if i == n:
					node.mark_done(undo=undo)
					return True
		return False

	def add(self, cmd):
		pattern = '(\d+) (add proj|add) (.*?)$'
		match = re.match(pattern, cmd)

		if match:
			n = int(match.group(1))
			name = match.group(3)
			type_ = match.group(2)

			i = 0
			for node in self.db.query_all():
				i += 1
				if i == n:
					if type_ == 'add':
						if isinstance(node, Area) or isinstance(node, Project):
							node.actions.append(Action(name))
							return True
					elif type_ == 'add proj':
						if isinstance(node, Area):
							node.projects.append(Project(name))
							return True
		return False


def _format_item(item):
	ret = ''

	if isinstance(item, Area):
		ret = '*** ' + item.name + ' ***'
	elif isinstance(item, Project):
		ret = '\t\t' + item.name + '\n\t\t' + ('=' * len(item.name))
	elif isinstance(item, Action):
		ret = '\t\t\t [' + ('X' if item.is_done else ' ') + '] ' + item.name

	return ret