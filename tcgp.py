"""Tree-Controled Grammer parser."""

import parser
import ll_table
import input_parser

# -- coding: utf-8 --
__author__ = 'stepan'

input = open('tests/input5.in', 'r')
gramInput = open('tests/test5.in', 'r')

grammar, automat = parser.parse(gramInput.read())
print(grammar, "\n")
grammar.removeDeepLeftRecursion()
print(grammar, "\n")
grammar.leftFactorization()
print(grammar, "\n")

table = ll_table.LLTable(grammar)
parser = input_parser.InputParser(input.read())
automat.dropERules().determinate()
table.analyzeSymbols(parser.getToken, automat)
exit(0)
