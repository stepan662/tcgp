"""Tree-Controled Grammer parser."""

import parser

# -- coding: utf-8 --
__author__ = 'stepan'

file = open('test1.in', 'r')
try:
    grammar, automat = parser.parse(file.read())
    automat.dropERules().determinate()
    print(automat)
    print(grammar._symbols)
    print(grammar._terminals)
    print(grammar._start)
    if automat.analyzeString("aAbBcC"):
        print("String valid")
    else:
        print("String invalid")
except ValueError as e:
    print(e.args[0])
