from .formatter import format_date
from .items import Area


class DataBase:
    """DataBase object stores all the information from the xml file into memory.
    """

    def __init__(self):
        self.areas = []
        self._sort_by = lambda x: x.is_done
        self._sort_rev = False

    def __iter__(self):
        for area in self.areas:
            yield area

    def append(self, area):
        self.areas.append(area)

    def query(self, args=None):
        """List all items in a database. Result may be filtered by applying
        extra conditions in form of an 'args' dictionary.
        """
        if args is None:
            args = {}

        def _default_adjusted_args(filter):
            """Remove default arguments from filter."""
            f = dict(filter)
            arch = f.get('arch', None)

            if arch == [True]:
                f.pop('arch')

            return f

        def _check_name(name, name_list):
            x = name.lower()
            y = [z.lower() for z in name_list]

            for i in y:
                if i in x:
                    return True
            return False

        def _check_area(node, filter):
            for k, v in filter.items():
                if k == 'area':
                    if not _check_name(node.name, v):
                        return False
            return True

        def _check_proj(node, filter):
            for k, v in filter.items():
                if k == 'proj':
                    if not _check_name(node.name, v):
                        return False
            return True

        def _check_act(node, filter):
            for k, v in filter.items():
                if k == 'act':
                    if not _check_name(node.name, v):
                        return False
                elif k == 'tag':
                    if not (set(node.tags) & set(v)):
                        return False
                elif k == 'due':
                    if not node.due_date:
                        return False
                    for due in v:
                        if due(format_date(node.due_date)):
                            return True
                    return False
                elif k == 'done':
                    if not (set([node.is_done]) & set(v)):
                        return False
                elif k == 'arch':
                    if not (set([node.is_archieved]) & set(v)):
                        return False
            return True

        def _get_actions(node, filter):
            if isinstance(node, Area) and 'proj' in filter:
                return []

            return [action
                    for action
                    in sorted(node.actions, key=self._sort_by,
                              reverse=self._sort_rev)
                    if _check_act(action, filter)]

        def _get_projects(node, filter):
            def has_elem(project):
                fargs = dict(filter)
                fargs.pop('arch', None)

                if fargs:
                    return any(_get_actions(project, fargs))
                return True

            return [project
                    for project
                    in sorted(node.projects, key=self._sort_by,
                              reverse=self._sort_rev)
                    if _check_proj(project, filter) and has_elem(project)]

        def _get_areas(filter):
            def has_elem(area):
                fargs = dict(filter)
                fargs.pop('arch', None)

                if fargs:
                    return (any(_get_actions(area, fargs)) or
                            any(_get_projects(area, fargs)))
                return True

            return [area
                    for area
                    in self.areas
                    if _check_area(area, filter) and has_elem(area)]

        for area in _get_areas(args):
            yield area

            for action in _get_actions(area, args):
                yield action

            for project in _get_projects(area, args):
                yield project

                for action in _get_actions(project, args):
                    yield action
