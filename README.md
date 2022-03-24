# kanban

## Introduction

Minimalistic kanban board application for the console in python.

![Application UI](img/kanban.png?raw=true "Application UI.")

## Requirements

	* Python >= 3.8
	* Colorama

## Manual

The commands:

	* ADD: Adds a new task, task name is prompted.
	* ADVANCE: Passes the task to the next column, prompts for the task id.
	* LIST: Shows the Kanban panel.
	* CLEAR: Clears the last column (Done).
	* REMOVE: Removes a task, prompts for the task id.
	* HELP: Lists the commands available.
	* QUIT: Saves the board and exits.

The tasks that abandon the board are stored in a file, with information about the date it reached each column.

The UI is best visualized in terminals tha support ANSI colors scape codes. Otherwise odd character combinations will be displayed.

## License

This software is distributed under the MIT license.
