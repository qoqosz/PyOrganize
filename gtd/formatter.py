import datetime
from os import popen
import re
try:
    import colorama
    io_color = True
    is_color_initialized = False
except ImportError:
    io_color = False
import textwrap

import items as it


def filter_date(line):
    pair = re.search('([<>]?=|[<>]|)\s*(.*?)$', line)

    if pair:
        operator = pair.group(1)
        date = format_date(pair.group(2))

        if operator == '>=':
            return lambda x: x >= date
        elif operator == '<=':
            return lambda x: x <= date
        elif operator == '>':
            return lambda x: x > date
        elif operator == '<':
            return lambda x: x < date
        else:
            return lambda x: x == date

    return None


def format_date(line):
    date = None
    if re.search('(today|td)', line):
        date = datetime.datetime.now()
    elif re.search('(tomorrow|tm)', line):
        date = datetime.date.today() + datetime.timedelta(days=1)
    elif re.search('(yeasterday|yd)', line):
        date = datetime.date.today() - datetime.timedelta(days=1)
    elif re.search('(end-of-week|eow)', line):
        date = datetime.date.today()
        date = date + datetime.timedelta(days=(11 - date.weekday()) % 7)
    elif re.search('(end-of-month|eom)', line):
        date = datetime.date.today()
        date = date - datetime.timedelta(days=date.day - 1)
        date = date + datetime.timedelta(days=31)
        date = date - datetime.timedelta(days=date.day)
    else:
        pattern = '(\d{1,2})[\\\\/:\s\.-](\d{1,2})[\\\\/:\s\.-](\d{4})'
        match = re.search(pattern, line)

        if not match:
            return None
        else:
            day = int(match.group(1))
            month = int(match.group(2))
            year = int(match.group(3))
            date = datetime.datetime(year, month, day)

    return date.strftime('%d-%m-%Y')


def format_description(desc, prefix='\t\t\t'):
    rows, columns = popen('stty size', 'r').read().split()
    if not columns:
        return desc

    sz = int(columns) - len(prefix.expandtabs())

    return textwrap.fill('"' + desc + '"', width=sz, subsequent_indent=prefix)


def format_item(idx, item, options):
    global is_color_initialized

    ret = ''
    proj_indent = 8
    action_indent = 9

    if io_color:
        if not is_color_initialized:
            colorama.init(autoreset=True)
            is_color_initialized = True

    if isinstance(item, it.Area):
        ret = format_area(idx, item)

    elif isinstance(item, it.Project):
        ret = format_project(idx, item, options, indent=proj_indent)

    elif isinstance(item, it.Action):
        ret = format_action(idx, item, options, indent=action_indent)

    return ret


def format_area(idx, item):
    return ('{:d}' + colorama.Fore.CYAN + '*** {} ***').format(idx, item.name)


def format_project(idx, item, options, indent=8):
    if io_color:
        proj = ('{:<' + str(indent) + '}' + colorama.Fore.GREEN + '{}').format(
            idx, item.name)
    else:
        proj = ('{:<' + str(indent) + '}{}').format(idx, item.name)

    if item.due_date and ('show_due_date' in options):
        proj += ' @ ' + item.due_date

    if io_color:
        proj += '\n' + (' ' * indent) + colorama.Style.BRIGHT + \
                ('=' * len(item.name))
    else:
        proj += '\n' + (' ' * indent) + ('=' * len(item.name))

    return proj


def format_action(idx, item, options, indent):
    act = ('{:<' + str(indent) + '}[{}] {}').format(
        idx, 'X' if item.is_done else ' ', item.name)

    if item.description and ('show_description' in options):
        prefix = ' ' * (indent + 6)
        act += '\n' + prefix + \
            format_description(item.description, prefix=prefix)

    if (item.tags or item.due_date) and \
            (('show_tags' in options) or ('show_due_date' in options)):
        act += '\n' + ' ' * indent

        if item.due_date and ('show_due_date' in options):
            act += '@' + item.due_date + ' '
        if item.tags and ('show_tags' in options):
            act += ', '.join(['+' + str(x) for x in item.tags])

    return act
