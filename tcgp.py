"""Tree-Controled Grammer parser."""

import parser
import ll_table
import input_parser

# -- coding: utf-8 --
__author__ = 'stepan'

input = open('tests/input5.in', 'r')
gramInput = open('tests/test5.in', 'r')
try:
    grammar, automat = parser.parse(gramInput.read())
except ValueError as e:
    print(e.args[0])
    exit(e.args[1])
print(grammar, "\n")
grammar.removeDeepLeftRecursion()
grammar.leftFactorization()
print(grammar, "\n")

try:
    table = ll_table.LLTable(grammar)
    parser = input_parser.InputParser(input.read())
    if automat is not False:
        automat.dropERules().determinate()
    table.analyzeSymbols(parser.getToken, automat)
except ValueError as e:
    print(e.args[0])
    exit(e.args[1])
exit(0)
