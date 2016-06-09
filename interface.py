import re
from utilities import *

class Interface:
	def __init__(self, db):
		self.db = db
		self.user_filter = {}

	def start(self):
		self.show_query(self.user_filter)
	
		while True:
			cmd = raw_input('> ')
			
			if cmd == 'quit':
				break
			elif cmd == 'list':
				self.user_filter = {}
				self.show_query(self.user_filter)
			elif cmd.startswith('done'):
				if not self.mark_done(cmd):
					print 'Cannot locate an item'
				else:
					self.show_query(self.user_filter)
			elif cmd.startswith('undone'):
				if not self.mark_done(cmd, undo=True):
					print 'Cannot locate an item'
				else:
					self.show_query(self.user_filter)
			elif re.search('\d+ add', cmd):
				if not self.add(cmd):
					print 'Cannot add task'
				else:
					sself.show_query(self.user_filter)
			elif re.search('\d+ tag', cmd):
				if not self.tag(cmd):
					print 'Cannot assaign tag'
				else:
					self.show_query(self.user_filter)
			elif re.search('\d+ due', cmd):
				if not self.due(cmd):
					print 'Cannot assaign due date'
				else:
					self.show_query(self.user_filter)
			elif cmd.startswith('select'):
				if not self.select(cmd):
					print 'Wrong syntax'
				else:
					self.show_query(self.user_filter)
			elif cmd == 'save':
				save(self.db)

			elif cmd == 'help':
				print '- list : list all tasks'
				print '- done X : mark item no X as done'
				print '- undone X : mark item no X as undone'
				print '- X add Y : add action with a name Y to X'
				print '- X add proj Y : add project named Y to X'
			
	def select(self, cmd):
		match = re.match(r'select (\w+) (.*?)$', cmd)

		if match:
			self.user_filter = {match.group(1): match.group(2)}
			return True

		return False



	def show_all(self):
		i = 0
		for node in self.db.query(self.user_filter):
			i += 1
			print str(i) + _format_item(node)

	def show_query(self, args):
		i = 0
		for node in self.db.query(args):
			i += 1
			print str(i) + _format_item(node)

	def mark_done(self, cmd, undo=False):
		match = re.search('done (\d+)', cmd)

		if match:
			n = int(match.group(1))

			i = 0
			for node in self.db.query(self.user_filter):
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
			for node in self.db.query(self.user_filter):
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

	def tag(self, cmd):
		pattern = '(\d+) tag (.*?)$'
		match = re.match(pattern, cmd)
		
		if match:
			n = int(match.group(1))
			i = 0
			for node in self.db.query(self.user_filter):
				i += 1
				if i == n:
					if isinstance(node, Action) or isinstance(node, Project):
						t = match.group(2)
						t = t.split(' ')
						for x in t:
							node.tags.append(x)
						return True
		return False

	def due(self, cmd):
		pattern = '(\d+) due (\d{1,2}-\d{1,2}-\d{4}).*?'
		match = re.match(pattern, cmd)
		
		if match:
			n = int(match.group(1))
			date = match.group(2)
			i = 0
			for node in self.db.query(self.user_filter):
				i += 1
				if i == n:
					if isinstance(node, Action) or isinstance(node, Project):
						node.due_date = date
						return True
		return False



def _format_item(item):
	ret = ''

	if isinstance(item, Area):
		ret = '*** ' + item.name + ' ***'
	elif isinstance(item, Project):
		ret = '\t\t' + item.name + '\n\t\t' + ('=' * len(item.name))
	elif isinstance(item, Action):
		ret = '\t\t [' + ('X' if item.is_done else ' ') + '] ' + item.name
		if item.tags or item.due_date:
			ret = ret + '\n\t\t     '
			if item.due_date:
				ret = ret + '@' + item.due_date + '  '
			if item.tags:
				ret = ret + ', '.join(['+' + str(x) for x in item.tags])

	return ret