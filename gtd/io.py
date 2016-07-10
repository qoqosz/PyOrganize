try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
import xml.dom.minidom  # just to prettify the output
import os
import db
import items as it

_db_file_name = ''
_EMPTY_DB = """<?xml version="1.0" encoding="utf-8"?>
<data>
    <area name="Inbox"/>
</data>"""


def save(database, file_name=None):
    """Add save_are, save_project,...  fncs insidethis one
    """
    if not file_name:
        file_name = _db_file_name

    data = ET.Element('data')

    for area in database:
        if not area.is_deleted:
            area_elem = ET.SubElement(data, 'area', area.attributes())

            for proj in area.projects:
                if not proj.is_deleted:
                    proj_elem = ET.SubElement(area_elem, 'project',
                                              proj.attributes())

                    if proj.description:
                        desc = ET.SubElement(proj_elem, 'description')
                        desc.text = proj.description
                    if proj.due_date:
                        due = ET.SubElement(proj_elem, 'due')
                        due.text = proj.due_date

                    for task in proj.actions:
                        if not task.is_deleted:
                            task_elem = ET.SubElement(proj_elem, 'action',
                                                      task.attributes())

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
                    task_elem = ET.SubElement(area_elem, 'action',
                                              task.attributes())

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
    database = db.DataBase()
    _eat_data(database, tasks_tree.iter())

    return database


def _prettify(xml_string):
    """Return a pretty-printed XML string for the xml.
    """
    return xml.dom.minidom.parseString(xml_string).toprettyxml(
        encoding='utf-8')


def _eat_attributes(object, node):
    if 'done' in node.attrib:
        if node.attrib.get('done') == 'True':
            object.mark_done()
    if 'archieved' in node.attrib:
        if node.attrib.get('archieved') == 'True':
            object.mark_archieved()


def _eat_data(database, items):
    for node in items:
        if node.tag == 'area':
            area = it.Area(node.attrib.get('name'))
            _eat_area(area, node)
            database.append(area)


def _eat_area(area, items):
    for node in items:
        if node.tag == 'project':
            project = it.Project(node.attrib.get('name'))
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
    action = it.Action(node.attrib.get('name'))
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
