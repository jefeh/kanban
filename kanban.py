#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Created By  : Gonzalo Fernández Hernández
# Created Date: 20220322
# version = '0.1'
# license = 'MIT'
# ---------------------------------------------------------------------------
""" Minimalistic kanban board """
# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

from collections import ChainMap
from typing import List, Set, Dict, Tuple, Optional
import pickle
import os
from colorama import init, Fore, Back, Style
import datetime

ColumnID = int
TaskID = int

class Task:
    LAST_TASK_ID: TaskID = 0
    def __init__(self, name: str):
        self.m_id : TaskID = Task.LAST_TASK_ID
        self.m_name : str = name
        self.m_messages : List[str] = []
        Task.LAST_TASK_ID += 1

    def get_id(self) -> TaskID:
        return self.m_id

    def add_message(self, msg: str):
        self.m_messages.append(msg)

    def get_messages(self) -> List[str]:
        return self.m_messages

    def __str__(self):
        return f"{self.m_id}. {self.m_name}"
        
        
class Column:
    def __init__(self, name: str):
        self.m_name : str = name
        self.m_tasks : List[Task] = []

    def add_task(self, task: Task) -> bool:
        if not task in self.m_tasks:
            self.m_tasks.append(task)
            task.add_message(f'> {self.m_name} : {datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")}')
            return True
        else:
            return False

    def remove_task(self, task_id: TaskID) -> Task:
        selected_tasks = [task for task in self.m_tasks if task.get_id() == task_id]
        if selected_tasks:
            self.m_tasks = [t for t in self.m_tasks if not t in selected_tasks]
            return selected_tasks[0]
        else:
            return None

    def contains(self, task_id: TaskID) -> bool:
        return len([task for task in self.m_tasks if task.get_id() == task_id]) > 0

    def get_contents(self) -> Dict[str, List[str]]:
        return {self.m_name: [str(k) for k in self.m_tasks]}

class Board:
    def __init__(self):
        self.m_columns : List[Column] = []

    def add_column(self, name: str) -> ColumnID:
        new_column = Column(name)
        self.m_columns.append(new_column)
        return len(self.m_columns) - 1

    def add_task(self, column_id: ColumnID, task: Task) -> bool:
        if column_id < len(self.m_columns):
            self.m_columns[column_id].add_task(task)
            return True
        else:
            return False

    def move_task(self, column_id: ColumnID, task_id: Task) -> bool:
        if column_id < len(self.m_columns):
            moving_tasks = list(filter(None, [col.remove_task(task_id) for col in self.m_columns]))
            if moving_tasks:
                assert(len(moving_tasks) == 1)
                self.m_columns[column_id].add_task(moving_tasks[0])
                return True
        return False

    def advance(self, task_id: TaskID) -> bool:
        selected_column = list(filter(lambda i: i[1].contains(task_id), enumerate(self.m_columns)))
        if selected_column:
            assert(len(selected_column) == 1)
            col_id, col = selected_column[0]
            new_col = col_id + 1
            task = col.remove_task(task_id)
            assert(task and new_col <= len(self.m_columns))
            if new_col < len(self.m_columns):
                self.m_columns[new_col].add_task(task)
            else:
                with open('finished_tasks.txt', 'a') as file:
                    file.write(f'{str(task)}\n')
                    for msg in task.get_messages():
                        file.write(f'\t{msg}\n')
            return True
        return False

    def clean_completed(self) -> int:
        last_column_ids = [k.get_id() for k in self.m_columns[-1].m_tasks]
        for task_id in last_column_ids:
            self.advance(task_id)
        return len(last_column_ids)
            
    def get_contents(self) -> Dict[str, List[str]]:
        return dict(ChainMap(*[col.get_contents() for col in self.m_columns]))


class Kanban:
    
    def __init__(self, columns: List[str]):
        self.m_board = Board()
        for col in columns:
            self.m_board.add_column(col)

    def load(self, filename: str) -> bool:
        if os.path.exists(filename):
            with open( filename, 'rb' ) as file:
                Task.LAST_TASK_ID = pickle.load( file )
                self.m_board = pickle.load( file )
            return True
        else:
            return False
    
    def save(self, filename: str) -> bool:
        with open( filename, 'wb' ) as file:
            pickle.dump(Task.LAST_TASK_ID , file)
            pickle.dump(self.m_board , file)
        return True

    def run(self):
        finish = False
        while not finish:
            print(Fore.BLUE + '> ' + Fore.WHITE, end='')
            cmd = input('').strip()
            if (cmd_upper := cmd.upper()) in Kanban.COMMANDS:
                finish = Kanban.COMMANDS[cmd_upper](self)
            else:
                print(Fore.RED + f'Error: Cannot understand "{cmd}". Type HELP.')

    def _show_menu(self) -> bool:
        for cmd, _ in Kanban.COMMANDS.items():
            print(Fore.BLUE + f'\t* {cmd}')
        return False

    def _list_tasks(self) -> bool:
        colors = dict(Fore.__dict__.items())
        for color_name, (col_name, tasks_descriptions) in zip(colors.keys(), self.m_board.get_contents().items()):
            print(colors[color_name] + f'\t*** { col_name }')
            for desc in tasks_descriptions:
                print(colors[color_name] + f'\t\t- { desc }')
        return False

    def _new_task(self) -> bool:
        print(Fore.BLUE + '\tName: ' + Fore.WHITE, end='')
        task_name = input('').strip()
        task = Task(task_name)
        self.m_board.add_task(0, task)
        print(Fore.BLUE + f'\tTask created with id {task.get_id()}.')
        return False

    def _advance_task(self) -> bool:
        print(Fore.BLUE + '\tTask ID: ' + Fore.WHITE, end='')
        task_id_str = input('').strip()
        try:
            task_id = int(task_id_str)
            self.m_board.advance(task_id)
        except ValueError:
            print(Fore.RED + f'\tError: Number expected.')
        return False

    def _clean_completed(self) -> bool:
        num_tasks = self.m_board.clean_completed()
        print(Fore.BLUE + f'{num_tasks} tasks cleaned.' + Fore.WHITE) if num_tasks else print(Fore.BLUE + 'No tasks to be cleaned.')
        return False
    
    def _quit(self) -> bool:
        print(Fore.BLUE + f'Goodbye.\n')
        return True
    
    COMMANDS = {
        'HELP': _show_menu,
        'LIST': _list_tasks,
        'ADD': _new_task,
        'ADVANCE': _advance_task,
        'CLEAN': _clean_completed,
        'QUIT': _quit,
        }

if __name__ == '__main__':
    init()
    print(Style.BRIGHT + Fore.BLUE + "Welcome to Kanban!")
    columns = ['New', 'Analysis', 'Development', 'Test', 'Done']
    kanban = Kanban(columns)

    filename = 'kanban.dat'
    if os.path.exists(filename):
        kanban.load(filename)

    kanban.run()

    kanban.save(filename)
    print(Fore.RESET+ Style.RESET_ALL)
