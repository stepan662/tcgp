"""Parsing Based on Tree-Controled Grammars."""

import parser

# -- coding: utf-8 --
__author__ = 'stepan'

file = open('test1.in', 'r')
automat = parser.parse(file.read())
automat.dropERules().determinate()
print(automat)
if automat.analyzeString("<>"):
    print("String valid")
else:
    print("String invalid")
