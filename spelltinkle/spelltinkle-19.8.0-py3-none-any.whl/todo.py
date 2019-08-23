import sys
from pathlib import Path
from string import ascii_letters

categories = ['done', 'now', 'tomorrow', 'next week', 'some day maybe']


def read():
    cat2id = {cat: n for n, cat in enumerate(categories)}
    todo = {}
    i = 0
    with open(Path.home() / 'cloud/todo.rst') as f:
        for line in f:
            cat = line.strip().lower()
            if cat in cat2id:
                todo[cat] = []
                line = f.readline().strip()
                assert line == '=' * len(cat)
                line = f.readline().strip()
                assert line.strip() == ''
                for line in f:
                    if line.startswith('* '):
                        todo[cat].append((i, line[2:-1]))
                        i += 1
                    else:
                        break
                if cat == 'some day maybe':
                    break
        remainder = f.read()
    return todo, remainder


def write(todo, remainder):
    with open(Path.home() / 'cloud/todo.rst2', 'w') as f:
        f.write('====\nTODO\n====\n\n')
        for cat in categories[1:]:
            f.write(cat.title() + '\n' + '=' * len(cat) + '\n\n')
            for n, task in todo[cat]:
                f.write('* ' + task + '\n')
            f.write('\n\n')
        f.write(remainder)


def main():
    args = sys.argv[1:]
    todo, remainder = read()
    n = len(args)
    if n == 0:
        args = ['1']
        n = 1
    if args[0].isdigit():
        if n == 1:
            for i in (int(c) for c in args[0]):
                cat = categories[i]
                print(cat.title() + ':')
                for n, task in todo[cat]:
                    print(f'  {ascii_letters[n]}: {task}')
            return
        i = int(args[0])
        cat = categories[i]
        todo[cat].append((-1, ' '.join(args[1:])))

    else:
        i = ascii_letters.index(args[0])
        for cat, tasks in todo.items():
            for j, task in tasks:
                if j == i:
                    break
            else:
                continue
            break
        todo[cat].remove((i, task))
        if args[1] != '0':
            todo[categories[int(args[1])]].insert(0, (-1, task))

    write(todo, remainder)


if __name__ == '__main__':
    main()
