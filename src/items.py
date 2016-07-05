class Action(object):
    """Define basic building block - the action.
    """
    def __init__(self, name, description=''):
        self.name = name
        self.description = description
        self.is_done = False
        self.is_archieved = False
        self.is_deleted = False
        self.due_date = None
        self.tags = []

    def __repr__(self):
        return 'Action() ' + self.name

    def __str__(self):
        return '\t\tAction: ' + self.name + ', [' + self.description + ']'

    def attributes(self):
        return {
            'name': self.name,
            'done': str(self.is_done),
            'archieved': str(self.is_archieved)
        }

    def mark_done(self, undo=False):
        if undo:
            self.is_done = False
        else:
            self.is_done = True

    def mark_archieved(self):
        self.is_archieved = True

    def get(self, attr):
        if attr == 'name':
            return self.name
        elif attr == 'description':
            return self.description
        elif attr == 'done':
            return self.is_done
        elif attr == 'archieved':
            return self.is_archieved
        elif attr == 'due':
            return self.due_date
        elif attr == 'tag':
            return self.tags

    def delete(self):
        self.is_deleted = True
        self.is_archieved = True


class Project(Action):
    """Project derives from Action class and is a collection of actions.
    """
    def __init__(self, name, description=''):
        super(Project, self).__init__(name, description)
        self.actions = []

    def __repr__(self):
        return 'Project() ' + self.name

    def __str__(self):
        return '\tProject: ' + self.name + ', [' + self.description + ']'

    def actions_live(self):
        """Iterate over live actions.
        """
        for action in self.actions:
            if not action.is_done:
                yield action

    def actions_archieved(self):
        """Iterate over archieved actions.
        """
        for action in self.actions:
            if action.is_archieved:
                yield action

    def mark_done(self, undo=False):
        """Mark project and all its actions as done.
        """
        if undo:
            self.is_done = False
        else:
            self.is_done = True

        for action in self.actions:
            action.mark_done(undo=undo)

    def mark_archieved(self):
        """Mark project and all its actions as archieve.
        """
        self.is_archieved = True

        for action in self.actions:
            action.mark_archieved()


class Area(Project):
    """Area is a collection of both projects and actions.
    """
    def __init__(self, name):
        super(Area, self).__init__(name, description='')
        self.projects = []

    def __repr__(self):
        return 'Area() ' + self.name

    def __str__(self):
        return 'Area: ' + self.name

    def attributes(self):
        return {
            'name': self.name
        }

    def mark_done(self, undo=False):
        if undo:
            self.is_done = False
        else:
            self.is_done = True

        for project in self.projects:
            project.mark_done(undo=undo)

        for action in self.actions:
            action.mark_done(undo=undo)

    def mark_archieved(self):
        self.is_archieved = True

        for project in self.projects:
            project.mark_archieved()

        for action in self.actions:
            action.mark_archieved()
