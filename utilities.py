try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
import xml.dom.minidom # just to prettify the output
import os

_db_file_name = ''
_EMPTY_DB = '<?xml version="1.0" encoding="utf-8"?><data><area name="Inbox"/></data>'

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
        self.is_archieved =  True

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

    def projects_live(self):
        """Iterate over live projects.
        """
        for project in self.projects:
            if not project.is_done:
                yield project

    def projects_archieved(self):
        """Iterate over archieved projects.
        """
        for project in self.projects:
            if project.is_archieved:
                yield project

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


class DataBase:
    """DataBase object stores all the information from the xml file into memory.
    """
    def __init__(self):
        self.areas = []

    def __iter__(self):
        """In fact we should iterate over everything,
        not just areas
        """
        for area in self.areas:
            yield area

    def append(self, area):
        self.areas.append(area)

    def add_area(self, area):
        self.areas.append(area)

    def query_all(self):
        sort_by_done = lambda x: x.is_done

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
                    if not (set([node.due_date]) & set(v)):
                        return False
                elif k == 'done':
                    if not (set([node.is_done]) & set(v)):
                        return False
                elif k == 'arch':
                    if not (set([node.is_archieved]) & set(v)):
                        return False
            return True

        sort_by_done = lambda x: x.is_done

        for area in self.areas:
            if _check_area(area, args):
                yield area

                for project in sorted(area.projects, key=sort_by_done):
                    if _check_proj(project, args):
                        yield project

                        for action in sorted(project.actions, key=sort_by_done):
                            if _check_act(action, args):
                                yield action
                                
                for action in sorted(area.actions, key=sort_by_done):
                    if _check_act(action, args):
                        yield action



def save(db, file_name=None):
    """Add save_are, save_project,...  fncs insidethis one
    """
    if not file_name:
        file_name = _db_file_name

    data = ET.Element('data')

    for area in db:
        if not area.is_deleted:
            area_elem = ET.SubElement(data, 'area', area.attributes())

            for proj in area.projects:
                if not proj.is_deleted:
                    proj_elem = ET.SubElement(area_elem, 'project', proj.attributes())

                    if proj.description:
                        desc = ET.SubElement(proj_elem, 'description')
                        desc.text = proj.description
                    if proj.due_date:
                        due = ET.SubElement(proj_elem, 'due')
                        due.text = proj.due_date

                    for task in proj.actions:
                        if not task.is_deleted:
                            task_elem = ET.SubElement(proj_elem, 'action', task.attributes())

                            if task.description:
                                desc = ET.SubElement(task_elem, 'description')
                                desc.text = task.description
                            if task.tags:
                                for tag_name in task.tags:
                                    tag = ET.SubElement(task_elem, 'tag')
                                    tag.text = tag_name
                            if task.due_date:
                                due = ET.SubElement(task_elem, 'due')
                                due.text = task.due_date

            for task in area.actions:
                if not task.is_deleted:
                    task_elem = ET.SubElement(area_elem, 'action', task.attributes())

                    if task.description:
                        desc = ET.SubElement(task_elem, 'description')
                        desc.text = task.description
                    if task.tags:
                        for tag_name in task.tags:
                            tag = ET.SubElement(task_elem, 'tag')
                            tag.text = tag_name
                    if task.due_date:
                        due = ET.SubElement(task_elem, 'due')
                        due.text = task.due_date

    fOut = open(file_name, 'w')
    fOut.write(_prettify(ET.tostring(data, encoding='utf-8', method='xml')))
    fOut.close()

def load(file_name):
    global _db_file_name
    _db_file_name = file_name

    if not os.path.isfile(file_name):
        fOut = open(file_name, 'w')
        fOut.write(_EMPTY_DB)
        fOut.close()

    tasks_tree = ET.parse(file_name).getroot()
    db = DataBase()
    _eat_data(db, tasks_tree.iter())

    return db

def _prettify(xml_string):
    """Return a pretty-printed XML string for the xml.
    """
    return xml.dom.minidom.parseString(xml_string).toprettyxml(encoding='utf-8')

def _eat_attributes(object, node):
    if 'done' in node.attrib:
        if node.attrib.get('done') == 'True':
            object.mark_done()
    if 'archieved' in node.attrib:
        if node.attrib.get('archieved') == 'True':
            object.mark_archieved()

def _eat_data(db, items):
    for node in items:
        if node.tag == 'area':
            area = Area(node.attrib.get('name'))
            _eat_area(area, node)
            db.append(area)

def _eat_area(area, items):
    for node in items:
        if node.tag == 'project':
            project = Project(node.attrib.get('name'))
            _eat_project(project, node)
            _eat_attributes(project, node)
            area.projects.append(project)

        elif node.tag == 'action':
            _process_action(area, node)

def _eat_project(project, items):
    for node in items:
        if node.tag == 'description':
            project.description = node.text
        elif node.tag == 'action':
            _process_action(project, node)
        elif node.tag == 'due':
            project.due_date = node.text

def _process_action(object, node):
    action = Action(node.attrib.get('name'))
    _eat_action(action, node)
    _eat_attributes(action, node)   
    object.actions.append(action)

def _eat_action(action, items):
     for node in items:
        if node.tag == 'description':
            action.description = node.text
        if node.tag == 'tag':
            action.tags.append(node.text)
        if node.tag == 'due':
            action.due_date = node.text
