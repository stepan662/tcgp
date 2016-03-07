"""Tree-Controled Grammer parser."""

from parser import parse
from lr_table import LRTable
from input_parser import InputParser

# -- coding: utf-8 --
__author__ = 'stepan'

input = open('tests/input6.in', 'r')
gramInput = open('tests/test6.in', 'r')
try:
    grammar, automat = parse(gramInput.read())
except ValueError as e:
    print(e.args[0])
    exit(e.args[1])
# print(grammar, "\n")

table = LRTable(grammar)
parser = InputParser(input.read())
# table.analyzeSymbols(parser.getToken)
