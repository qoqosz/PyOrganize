# PyOrganize
Simple command-line todo app written in Python.

![PyOrganize Main Screen](http://f.cl.ly/items/1a0x2Q3a2c0l0J1v232a/pyorganize.png)

The application is designed to provide simple command line tool that helps users oragnize their tasks. However, PyOrganize is by no means a minimalistic app. It's focus is to provide simple interface to help user manage a list of reasonable number of tasks. This objective is met by means of simple query syntax.

## The design
There are three main types of items that are building blocks of a whole todo list.

1. Area
2. Project
3. Action

### Area
Area is a collection of projects and actions that have some common factors.
### Project
Project is a collection of actions that define one major goal to acomplish.
### Action
Is a physical action one need to take.

## Commands
### Creating items
At the moment, only Actions and Projects may be created from inside the application. Areas need to be specified manually in the tasks.xml file.
Creating an item is done by the following command:
```
add <id> <name of a task>
add proj <id> <name of a project>
```
where <id> is an id of a parent node (project or action), in which a new item will be created. At the creation user may specify only the name of an item.
Further details may be specified by using various commands with an id of an action:

```done <id>``` - mark item as done,<br/>
```undone <id>``` - reverts the above,<br/>
```desc <id>``` - set a description for an action,<br/>
```tag <id> tag1 tag2``` - assign tags to an action; multple tags may be assigned at ones when separated by a space,<br/>
```due <id> date``` - add a due date to an action; the most general date format is: dd-mm-yyyy, though some abbreviations may be used instead: today, td, tomorrow, tm, yesterday, yd, end-of-week, eow, end-of-month, eom,<br/>
```edit <id> New action name``` - rename an existing action.

### Filtering the list
soon
