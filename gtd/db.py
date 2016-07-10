from formatter import format_date


class DataBase:
    """DataBase object stores all the information from the xml file into memory.
    """

    def __init__(self):
        self.areas = []
        self._sort_by = lambda x: x.is_done
        self._sort_rev = False

    def __iter__(self):
        """In fact we should iterate over everything,
        not just areas
        """
        for area in self.areas:
            yield area

    def append(self, area):
        self.areas.append(area)

    def query_all(self):
        def sort_by_done(x):
            return x.is_done

        for area in self.areas:
            yield area
            for project in sorted(area.projects, key=sort_by_done):
                yield project
                for action in sorted(project.actions, key=sort_by_done):
                    yield action
            for action in sorted(area.actions, key=sort_by_done):
                yield action

    def query(self, args={}):
        def _check_name(name, name_list):
            x = name.lower()
            y = [z.lower() for z in name_list]

            for i in y:
                if i in x:
                    return True
            return False

        def _check_area(node, filter):
            for k, v in filter.iteritems():
                if k == 'area':
                    if not _check_name(node.name, v):
                        return False
            return True

        def _check_proj(node, filter):
            for k, v in filter.iteritems():
                if k == 'proj':
                    if not _check_name(node.name, v):
                        return False
            return True

        def _check_act(node, filter):
            for k, v in filter.iteritems():
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

        for area in self.areas:
            if _check_area(area, args):
                yield area

                for project in sorted(area.projects,
                                      key=self._sort_by,
                                      reverse=self._sort_rev):
                    if _check_proj(project, args):
                        yield project

                        for action in sorted(project.actions,
                                             key=self._sort_by,
                                             reverse=self._sort_rev):
                            if _check_act(action, args):
                                yield action

                for action in sorted(area.actions,
                                     key=self._sort_by,
                                     reverse=self._sort_rev):
                    if _check_act(action, args):
                        yield action
