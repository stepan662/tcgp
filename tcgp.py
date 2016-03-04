"""Tree-Controled Grammer parser."""

import parser
import ll_table
import input_parser

# -- coding: utf-8 --
__author__ = 'stepan'

input = open('input4.in', 'r')
gramInput = open('test4.in', 'r')

grammar, automat = parser.parse(gramInput.read())
print(grammar, "\n\n")
# grammar.removeDeepLeftRecursion()
# print(grammar, "\n\n")
grammar.leftFactorization()
print(grammar, "\n\n")

table = ll_table.LLTable(grammar)
parser = input_parser.InputParser(input.read())
table.analyzeSymbols(parser.getToken)
exit(0)
