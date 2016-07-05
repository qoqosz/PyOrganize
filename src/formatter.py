import datetime
import re

import items as it


def interpret_date(line):
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


def format_item(item, options):
    ret = ''

    if isinstance(item, it.Area):
        ret = '*** ' + item.name + ' ***'
    elif isinstance(item, it.Project):
        ret = '\t\t' + item.name

        if item.due_date and options.get('show_due_date'):
            ret = ret + ' @ ' + item.due_date
        ret += '\n\t\t' + ('=' * len(item.name))
    elif isinstance(item, it.Action):
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
