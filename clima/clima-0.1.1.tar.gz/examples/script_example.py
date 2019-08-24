#!/usr/bin/env python
from clima import c, Schema


@c
class C(Schema):
    name: str = 'Klimenko'  # Your first name
    surname: str = 'Ma'  # Surname
    age: int = '132'  # Age is just a number


c: C = c


@c
class Something:
    def print_name(self):
        """This command prints name"""
        print(f'{c.name} {c.surname}')

    def print_age(self):
        """This here, prints my age"""
        print(c.age)

# $ ./script_example.py
#
# Usage:       script_example.py -
#              script_example.py - print-age
#              script_example.py - print-name
#
# Process finished with exit code 0

# $ ./script_example.py print-name
#
# Klimenko Ma

# $ ./script_example.py print-name --name YoYo
#
# YoYo Ma

# $ ./script_example.py print-age
#
# 132
