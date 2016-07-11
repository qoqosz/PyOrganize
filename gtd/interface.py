import copy
import datetime
import re
import weakref

import alias
import completer as cpl
import formatter as fmt
import io
import items as it
import options as opt

try:
    import readline
except ImportError:
    print('Module readline not available.')


class Interface:
    def __init__(self, db):
        self.db = db
        self.user_filter = self.default_filter()
        self.alias = alias.Alias('alias.txt')
        self.options = opt.Options('options.txt').get()

        self.commands = [
            {
                'name': 'add proj',
                're': r'^add proj\s+\d+',
                'func': self._add,
                'errmsg': 'Cannot add project',
                'help': 'Create new project'
            }, {
                'name': 'add',
                're': r'^add\s+\d+',
                'func': self._add,
                'errmsg': 'Cannot add action',
                'help': 'Create new action'
            }, {
                'name': 'arch',
                're': r'^arch\s+\d+',
                'func': self._archieve,
                'errmsg': 'Cannot archieve an item',
                'help': 'Move selected item into archieve'
            }, {
                'name': 'clean',
                're': r'^(clean|cl)\s+\d+',
                'func': self._clean,
                'errmsg': 'Cannot clean item attributes',
                'help': 'Clean action attributes: due date or tags'
            }, {
                'name': 'del',
                're': r'^del\s+\d+',
                'func': self._del,
                'errmsg': 'Cannot delete task',
                'help': 'Delete selected task'
            }, {
                'name': 'desc',
                're': r'^desc\s+\d+',
                'func': self._desc,
                'errmsg': 'Cannot add action description',
                'help': 'Add description to an action'
            }, {
                'name': 'done',
                're': r'^done\s+\d+',
                'func': self._mark_done,
                'errmsg': 'Cannot locate an item',
                'help': 'Mark item as done'
            }, {
                'name': 'due',
                're': r'^due\s+\d+',
                'func': self._due,
                'errmsg': 'Cannot assaign due date',
                'help': 'Assign due date to an action'
            }, {
                'name': 'edit',
                're': r'^edit\s+\d+',
                'func': self._edit,
                'errmsg': '',
                'help': 'Edit name of an action'
            }, {
                'name': 'help',
                're': r'^help',
                'func': self._help,
                'errmsg': '',
                'help': 'Print this help'
            }, {
                'name': 'list',
                're': r'^list',
                'func': self._list,
                'errmsg': 'Cannot list all items',
                'help': 'List all items'
            }, {
                'name': 'move',
                're': r'^move\s+\d+\s+to\s+\d+',
                'func': self._move,
                'errmsg': '',
                'help': 'Move an action between projects/areas'
            }, {
                'name': 'save',
                're': r'^save',
                'func': self._save,
                'errmsg': '',
                'help': 'Save list to the file'
            }, {
                'name': 'show',
                're': r'^show',
                'func': self._show,
                'errmsg': '',
                'help': 'Show/hide some of the information'
            }, {
                'name': 'sort',
                're': r'^sort',
                'func': self._sort,
                'errmsg': '',
                'help': 'Sort current list'
            }, {
                'name': 'select, s',
                're': r'^(select|s)',
                'func': self._select,
                'errmsg': '',
                'help': 'Filter items to display'
            }, {
                'name': 'tag',
                're': r'^tag\s+\d+',
                'func': self._tag,
                'errmsg': 'Cannot assaign tag',
                'help': 'Assign tags to an action'
            }, {
                'name': 'undone',
                're': r'^undone\s+\d+',
                'func': self._mark_undone,
                'errmsg': 'Cannot locate an item',
                'help': 'Mark item as not done'
            }, {
                'name': 'view, v',
                're': r'^v\s+',
                'func': self._alias,
                'errmsg': '',
                'help': 'Load pre-defined view'
            }, {
                'name': 'quit',
                're': r'^(q|quit)$',
                'func': None,
                'errmsg': '',
                'help': 'Quit the application'
            }
        ]

    def default_filter(self):
        """Default filter is set to list all non-archieved tasks.
        """
        return {'arch': [False]}

    def default_sort(self):
        self.db._sort_by = lambda x: x.is_done
        self.db._sort_rev = False

    def start(self):
        """Main loop of an interface that reads and parses commands.
        """
        self._show_query(self.user_filter)

        suggestions = [x.get('name') for x in self.commands]
        suggestions.extend(['show_tags', 'show_description', 'show_due_date',
                            'today', 'tomorrow', 'yesterday'])

        completer = cpl.Completer(suggestions)
        readline.set_completer(completer.complete)
        readline.parse_and_bind('tab: complete')

        while True:
            cmd = raw_input('> ')
            cmd = cmd.lstrip().rstrip()

            if cmd == 'quit' or cmd == 'q':
                break

            self._proceed_cmd(cmd)

    def _proceed_cmd(self, cmd, show=True):
        for op in self.commands:
            if re.search(op.get('re'), cmd):
                try:
                    if not op.get('func')(cmd):
                        print(op.get('errmsg'))
                    else:
                        if show:
                            self._show_query(self.user_filter)
                except Exception, e:
                    print('Exception: ' + str(e))
                    print(op.get('name') + ': ' + op.get('errmsg'))
                finally:
                    break

    def _show_query(self, args):
        i = 0
        for node in self.db.query(args):
            i += 1
            print(str(i) + fmt.format_item(node, self.options))
        return True

    def _get_item(self, n):
        """Get an n-th item from the list given a user filter is applied.
        """
        i = 0
        for node in self.db.query(self.user_filter):
            i += 1
            if i == n:
                return weakref.ref(node)
        raise IndexError('Index %d does not exist.' % n)

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
            s = re.search(tags_pattern + '\s*(.*?)$', cmd[pos[i]:pos[i + 1]])
            if s:
                k, v = s.groups()
                v = v.rstrip()

                if k in ['done', 'arch']:
                    v = v not in ['False']
                elif k in ['due']:
                    v = fmt.filter_date(v)
                    if not v:
                        raise ValueError('Incorrect comparison operator')

                if k in args:
                    args[k].append(v)
                else:
                    args[k] = [v]

        if not args:
            return False

        self.user_filter.update(args)

        return True

    def _sort(self, cmd):
        def _sort_by_due(x):
            if x.due_date:
                return datetime.datetime.strptime(x.due_date, '%d-%m-%Y')
            return datetime.datetime.now()

        pattern = '^sort\s+(name|tag|due|name|)\s*(asc|desc|)$'
        match = re.match(pattern, cmd)

        if match:
            print('Sorting')
            by = match.group(1)
            order = match.group(2)

            if by == '' or by is None:
                self.default_sort()

            if order == 'desc':
                self.db._sort_by = None
                self.db._sort_rev = True
            elif order == 'asc':
                self.db._sort_by = None
                self.db._sort_rev = False

            if by == 'due':
                self.db._sort_by = _sort_by_due
            elif by == 'name':
                self.db._sort_by = lambda x: x.name

            return True
        return False

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

    def _add(self, cmd):
        """Add action or project.
        """
        pattern = '(add proj|add)\s+(\d+)\s+(.*?)$'
        match = re.match(pattern, cmd)

        if match:
            item = self._get_item(int(match.group(2)))
            name = match.group(3)
            type_ = match.group(1)

            if type_ == 'add':
                if isinstance(item(), it.Area) or isinstance(item(),
                                                             it.Project):
                    item().actions.append(it.Action(name))
                    return True
            else:
                if isinstance(item(), it.Area):
                    item().projects.append(it.Project(name))
                    return True

        return False

    def _alias(self, cmd):
        match = re.search('v\s+(.*?)(\s.*?)?$', cmd)
        if match:
            cmd = self.alias.get(match.group(1))

            if match.group(2):
                cmd += match.group(2)

            self._proceed_cmd(cmd, show=False)
            return True
        return False

    def _archieve(self, cmd):
        """Move selected item into the archieve.
        """
        match = re.search('arch\s+(\d+)(?:\s*-\s*)?(\d+)?$', cmd)
        if match:
            a = int(match.group((1)))
            b = int(match.group((2))) if match.group(2) else a

            item_list = []

            for i in range(a, b + 1):
                item_list.append(self._get_item(i))

            for item in item_list:
                item().mark_archieved()

            return True

        return False

    def _clean(self, cmd):
        """Clean action's attribues - due date, tags or both.
        """
        match = re.search('(clean|cl)\s+(\d+)', cmd)
        if match:
            item = self._get_item(int(match.group(2)))

            if cmd.find('tag') > -1:
                item().clean_tags()
            if cmd.find('due') > -1:
                item().clean_duedate()

            return True

        return False

    def _edit(self, cmd):
        """Edit an item name.
        """
        match = re.search('edit\s+(\d+)\s+(.*?)$', cmd)
        if match:
            item = self._get_item(int(match.group(1)))
            item().name = match.group(2)
            return True

        return False

    def _del(self, cmd):
        """delete = mark as archieved and set a is_deleted flag to True
        This way, at a program exit an item won't be saved
        """
        pattern = 'del\s+(\d+)$'
        match = re.match(pattern, cmd)

        if match:
            item = self._get_item(int(match.group(1)))
            item().delete()
            return True

        return False

    def _desc(self, cmd):
        """Set a description of an item.
        """
        match = re.search('desc\s+(\d+)\s+(.*?)$', cmd)

        if match:
            item = self._get_item(int(match.group(1)))
            item().description = match.group(2)
            return True

        return False

    def _due(self, cmd):
        """Set a due date for an action or a project.
        """
        pattern = 'due\s+(\d+)\s+(.*?)$'
        match = re.match(pattern, cmd)

        if match:
            item = self._get_item(int(match.group(1)))
            date = fmt.format_date(match.group(2))

            if isinstance(item(), it.Action) or isinstance(item(), it.Project):
                item().due_date = date
                return True

        return False

    def _help(self, cmd):
        """List all available commands.
        """
        print('Full list of available commands:')
        for x in self.commands:
            print(x.get('name') + (' ' *
                                   (15 - len(x['name']))) + ' - ' + x['help'])
        return False

    def _list(self, cmd):
        """Default view - all non-archieved items.
        """
        self.user_filter = self.default_filter()
        return True

    def _mark_done(self, cmd, undo=False):
        """Mark item as done.
        """
        match = re.search('done\s+(\d+)', cmd)

        if match:
            item = self._get_item(int(match.group(1)))
            item().mark_done(undo=undo)
            return True

        return False

    def _mark_undone(self, cmd):
        """Mark item as undone.
        """
        return self._mark_done(cmd, True)

    def _move(self, cmd):
        """Actions only.
        Move action from one project/area to another.
        """
        match = re.search('move\s+(\d+)\s+to\s+(\d+)', cmd)
        if match:
            item = self._get_item(int(match.group(1)))
            dest = self._get_item(int(match.group(2)))

            if isinstance(item(), it.Action):
                if isinstance(dest(), it.Project) or isinstance(dest(),
                                                                it.Area):
                    dest().actions.append(copy.deepcopy(item()))
                    item().delete()
                    return True

        return False

    def _save(self, cmd):
        """Save database to a file.
        """
        print('Saving')
        io.save(self.db)
        return False

    def _tag(self, cmd):
        """Apply tags to an action.
        Tags may be given as a comma-separated list.
        """
        print('Tagging')

        pattern = 'tag\s+(\d+)\s+(.*?)$'
        match = re.match(pattern, cmd)

        if match:
            item = self._get_item(int(match.group(1)))

            if isinstance(item(), it.Action):
                tags = match.group(2)
                tags = tags.split(' ')
                for tag in tags:
                    item().tags.append(tag)
                return True

        return False
