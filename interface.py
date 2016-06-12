import re
import copy
import datetime
import weakref
from utilities import *


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


class Interface:
    def __init__(self, db):
        self.db = db
        self.user_filter = {'arch': [False]}
        self.alias = Alias('alias.txt')
        self.options = Options('options.txt').get()

        self.commands = [
            [r'^list', self._list, 'Cannot list all items'],
            [r'^done \d+', self._mark_done, 'Cannote locate an item'],
            [r'^undone \d+', self._mark_undone, 'Cannot locate an item'],
            [r'^add proj \d+', self._add, 'Cannot add project'],
            [r'^add \d+', self._add, 'Cannot add task'],
            [r'^desc \d+', self._desc, 'Cannot add task description'],
            [r'^del \d+', self._del, 'Cannot delete task'],
            [r'^tag \d+', self._tag, 'Cannot assaign tag'],
            [r'^due \d+', self._due, 'Cannot assaign due date'],
            [r'^edit \d+', self._edit, 'Cannot edit an item'],
            [r'^move \d+ to \d+', self._move, 'Cannot move an item'],
            [r'^save', self._save, ''],
            [r'^show', self._show, ''],
            [r'^(select|s)', self._select, 'Wrong query syntax'],
            [r'^v ', self._alias, ''],
            [r'^help', self._help, ''],
            [r'^(q|quit)$', None, None]
        ]

    def default_filter(self):
        """Default filter is set to list all non-archieved tasks.
        """
        return {'arch': [False]}

    def start(self):
        """Main loop of an interface that reads and parses commands.
        """
        self._show_query(self.user_filter)

        while True:
            cmd = raw_input('> ')
            cmd = cmd.lstrip().rstrip()

            if cmd == 'quit' or cmd == 'q':
                break

            self._proceed_cmd(cmd)
            
    def _proceed_cmd(self, cmd, show=True):
        for opt in self.commands:
            if re.search(opt[0], cmd):
                if not opt[1](cmd):
                    print opt[2]
                else:
                    if show:
                        self._show_query(self.user_filter)
                break       

    def _show(self, cmd):
        match = re.search('(show.*?)$', cmd)
        if match:
            option = match.group(1)

            if option in self.options:
                self.options[option] = not self.options[option]
            else:
                self.options[option] = True
            return True

        return False       

    def _get_item(self, n):
        """Get an n-th item from the list given a user filter is applied.
        """
        i = 0
        for node in self.db.query(self.user_filter):
            i += 1
            if i == n:
                return weakref.ref(node)
        return False

    def _alias(self, cmd):
        match = re.search('v (.*?)(\s.*?)?$', cmd)
        if match:
            cmd = self.alias.get(match.group(1))

            if match.group(2):
                cmd += match.group(2)

            self._proceed_cmd(cmd, show=False)
            return True
        return False

    def _move(self, cmd):
        """Actions only.
        Move action from one project/area to another.
        """
        match = re.search('move (\d+) to (\d+)', cmd)
        if match:
            item = self._get_item( int(match.group(1)) )
            dest = self._get_item( int(match.group(2)) )

            if isinstance(item(), Action):
                if isinstance(dest(), Project) or isinstance(dest(), Area):
                    dest().actions.append(copy.deepcopy(item()))
                    item().delete()
                    return True

        return False

    def _edit(self, cmd):
        """Edit an item name.
        """
        match = re.search('edit (\d+) (.*?)$', cmd)
        if match:
            item = self._get_item( int(match.group(1)) )
            item().name = match.group(2)
            return True

        return False

    def _save(self, cmd):
        """Save database to a file.
        """
        print 'Saving'
        save(self.db)
        return False

    def _del(self, cmd):
        """delete = mark as archieved and set a is_deleted flag to True
        This way, at a program exit an item won't be saved
        """
        pattern = 'del (\d+)$'
        match = re.match(pattern, cmd)

        if match:
            item = self._get_item( int(match.group(1)) )
            item().delete()
            return True

        return False       
            
    def _help(self, cmd):
        """List all available commands.
        """
        print 'Full list of available commands'
        for x in self.commands:
            print x[0][1:]
        return False

    def _select(self, cmd):
        """Filter mechanism.
        """
        self.user_filter = self.default_filter()
        tags = ['tag', 'due', 'name', 'done', 'arch', 'act', 'proj', 'area']
        tags_pattern = '(' + '|'.join(tags) + ')'
        pos = [m.start() for m in re.finditer(tags_pattern, cmd)]
        pos.append(None)
        args = {}
        
        for i in range(0, len(pos) - 1):
            s = re.search(tags_pattern + ' (.*?)$', cmd[pos[i]:pos[i+1]])
            if s:
                k, v = s.groups()
                v = v.rstrip()

                if k in ['done', 'arch']:
                    v = v not in ['False']
                elif k in ['due']:
                    v = _interpret_date(v)

                if k in args:
                    args[k].append(v)
                else:
                    args[k] = [v]
        if not args:
            return False
        self.user_filter.update(args)

        return True

    def _list(self, cmd):
        """Default view - all non-archieved items.
        """
        self.user_filter = self.default_filter()
        return True

    def _show_query(self, args):
        i = 0
        for node in self.db.query(args):
            i += 1
            print str(i) + _format_item(node, self.options)
        return True

    def _mark_done(self, cmd, undo=False):
        """Mark item as done.
        """
        match = re.search('done (\d+)', cmd)

        if match:
            item = self._get_item( int(match.group(1)) )
            item().mark_done(undo=undo)
            return True

        return False

    def _desc(self, cmd):
        """Set a description of an item.
        """
        match = re.search('desc (\d+) (.*?)$', cmd)

        if match:
            item = self._get_item( int(match.group(1)) )
            item().description = match.group(2)
            return True

        return False

    def _mark_undone(self, cmd):
        """Mark item as undone.
        """
        return self._mark_done(cmd, True)

    def _add(self, cmd):
        """Add action or project.
        """
        pattern = '(add proj|add) (\d+) (.*?)$'
        match = re.match(pattern, cmd)

        if match:
            item = self._get_item( int(match.group(2)) )
            name = match.group(3)
            type_ = match.group(1)

            if type_ == 'add':
                if isinstance(item(), Area) or isinstance(item(), Project):
                    item().actions.append(Action(name))
                    return True
            else:
                if isinstance(item(), Area):
                    item().projects.append(Project(name))
                    return True

        return False

    def _tag(self, cmd):
        """Apply tags to an action.
        Tags may be given as a comma-separated list.
        """
        pattern = 'tag (\d+) (.*?)$'
        match = re.match(pattern, cmd)
        
        if match:
            item = self._get_item( int(match.group(1)) )

            if isinstance(item(), Action):
                tags = match.group(2)
                tags = tags.split(' ')
                for tag in tags:
                    item().tags.append(tag)
                return True

        return False

    def _due(self, cmd):
        """Set a due date for an action or a project.
        """
        pattern = 'due (\d+) (.*?)$'
        match = re.match(pattern, cmd)
        
        if match:
            item = self._get_item( int(match.group(1)) )
            date = _interpret_date(match.group(2))

            if isinstance(item(), Action) or isinstance(item(), Project):
                item().due_date = date
                return True

        return False

def _interpret_date(line):

    date = None
    if re.search('(today|td)', line):
        date = datetime.datetime.now()
    elif re.search('(tomorrow|tm)', line):
        date = datetime.date.today() + datetime.timedelta(days=1)
    elif re.search('(yeasterday|yd)', line):
        date = datetime.date.today() - datetime.timedelta(days=1)
    elif re.search('(end-of-week|eow)', line):
        date = datetime.date.today()
        date = date + datetime.timedelta(days=(11 - date.weekday())%7)
    elif re.search('(end-of-month|eom)', line):
        date = datetime.date.today()
        date = date - datetime.timedelta(days=date.day - 1)
        date = date + datetime.timedelta(days=31)
        date = date - datetime.timedelta(days=date.day)
    else:
        pattern = '(\d{1,2})[\\\\/:\s\.](\d{1,2})[\\\\/:\s\.](\d{4})'
        match = re.search(pattern, line)

        if not match:
            return None
        else:
            print match.groups()
            day = int( match.group(1) )
            month = int( match.group(2) )
            year = int( match.group(3) )
            date = datetime.datetime(year, month, day)
            
    return date.strftime('%d-%m-%Y')

def _format_item(item, options):
    ret = ''

    if isinstance(item, Area):
        ret = '*** ' + item.name + ' ***'

    elif isinstance(item, Project):
        ret = '\t\t' + item.name
        if item.due_date and options.get('show_due_date'):
            ret = ret + ' @ ' + item.due_date
        ret += '\n\t\t' + ('=' * len(item.name))

    elif isinstance(item, Action):
        ret = '\t\t [' + ('X' if item.is_done else ' ') + '] ' + item.name
        if item.description and options.get('show_description'):
            ret = ret + '\n\t\t\t"' + item.description + '"'
        if (item.tags or item.due_date) and \
            (options.get('show_tags') or options.get('show_due_date')):
            ret = ret + '\n\t\t     '
            if item.due_date and options.get('show_due_date'):
                ret = ret + '@' + item.due_date + '  '
            if item.tags and options.get('show_tags'):
                ret = ret + ', '.join(['+' + str(x) for x in item.tags])

    return ret
