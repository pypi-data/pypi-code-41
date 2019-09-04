# pylint: disable=W0104

import os
import sys
from argparse import ArgumentParser

import todo

FILE_NAME = sys.argv[0].split('/')[-1]
STORAGE = {
    'active_path': f'{os.environ.get("HOME")}/.todo-list-active',
    'completed_path': f'{os.environ.get("HOME")}/.todo-list-completed',
}
HELPS = {
    'command': f'{FILE_NAME} add | list | complete | completed',
    'add': f"{FILE_NAME} add 'My new task' 'Other task' 'more' or single item",
    'complete': f'{FILE_NAME} complete 1',
    'params': 'can be a task (string) or index (int)',
}


def read_list(storage=STORAGE['active_path']):
    try:
        with open(storage, 'r') as file_pointer:
            lines = file_pointer.readlines()
        return [line.strip() for line in lines]
    except FileNotFoundError:
        return []


def update_file(data, storage=STORAGE['active_path']):  # pylint: disable=W0613
    if not data:
        with open(storage, 'w') as file_pointer:
            pass

    mode = 'w'
    if not os.path.exists(storage):
        mode = 'a'

    with open(storage, mode) as file_pointer:
        for line in data:
            file_pointer.write(line + '\n')


def main(argv=None):
    if argv is None:
        argv = sys.argv

    command_choices = ['list', 'add', 'complete', 'completed']

    parser = ArgumentParser(prog=FILE_NAME)
    parser.add_argument(
        'command', choices=command_choices, type=str, nargs='?', help=HELPS['command']
    )
    parser.add_argument('params', type=str, nargs='*', help=HELPS['params'])
    parser.add_argument('-v', '--version', action='version', version=todo.VERSION)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == 'add':
        if not args.params:
            sys.stdout.write(f"please enter your task.\n\t{HELPS['add']}\n")
            return 1
        todo.Todo.items = read_list()
        messages = []
        for task in args.params:
            status, message = todo.Todo.add(task)
            messages.append(message)
            if status:
                update_file(todo.Todo.items)
        if messages:
            for message in messages:
                sys.stdout.write(f'{message}\n')
            todo.Todo.list_todos
        return 0

    if args.command == 'list':
        sys.stdout.write('Current Tasks:\n')
        todo.Todo.items = read_list()
        todo.Todo.list_todos
        return 0

    if args.command == 'completed':
        todo.Todo.completed = read_list((STORAGE['completed_path']))
        todo.Todo.completed_list
        return 0

    if args.command == 'complete':
        if not args.params:
            sys.stdout.write(f"Please enter index. \n\t{HELPS['complete']}\n")
            return 1
        todo.Todo.items = read_list()
        todo.Todo.completed = read_list(STORAGE['completed_path'])

        status, message = todo.Todo.complete(int(args.params[0]))
        sys.stdout.write(f'{message}\n')

        if status:
            update_file(todo.Todo.items)
            update_file(todo.Todo.completed, STORAGE['completed_path'])
            todo.Todo.list_todos
        return 0

    return 0


if __name__ == '__main__':
    sys.exit(main())
