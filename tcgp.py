"""
Tree-Controled Grammer parser.

python3
tcgp.py
-g tests/test10.in -i tests/input10.in
"""

import sys
from getopt import getopt
from getopt import GetoptError
from parser import Parser
from lr_table import LRTable
from ll_table import LLTable
from input_parser import InputParser
from debug_print import Debug
from debug_print import debug_print

# -- coding: utf-8 --
__author__ = 'stepan'


input = sys.stdin
inputName = "Standard input"
output = sys.stdout
grammarIn = False
grammarInName = ""
ll = False

try:
    opts, args = getopt(
        sys.argv[1:],
        "hldi:o:g:u:",
        ["help", "ll", "debug", "input=", "output=", "grammar="])
except GetoptError as err:
    print(err)  # will print something like "option -a not recognized"
    sys.exit(2)


# program arguments
for o, a in opts:
    if o in ("-l", "--ll"):
        ll = True
    elif o in ("-d", "--debug"):
        Debug.setDebugMode(True)
    elif o in ("-h", "--help"):
        sys.exit()
    elif o in ("-i", "--input"):
        input = open(a, 'r')
        inputName = a
    elif o in ("-o", "--output"):
        output = open(a, 'w')
    elif o in ("-g", "--grammar"):
        grammarIn = open(a, 'r')
        grammarInName = a

if grammarIn is False:
    print('Missing requied argument -g (--grammar)')
    exit(1)

# parse input grammar
grammarParser = Parser()

try:
    grammarParser.parse(grammarIn.read())
except ValueError as e:
    lineNum = grammarParser.getLine()
    charPos = grammarParser.getPos()
    print(e.args[0] + "\n(file: '" + grammarInName + "', line: " +
          str(lineNum) + ", pos: " +
          str(charPos) + ")")
    exit(e.args[1])

grammar = grammarParser.getGrammar()
automat = grammarParser.getAutomat()
precedence = grammarParser.getPrecedence()

# Determinate automat
if automat:
    automat.dropERules()
    automat.determinate()

try:
    if ll:
        table = LLTable(grammar)
    else:
        table = LRTable(grammar, precedence)
        debug_print(table.groups, '\n')
except ValueError as e:
    print(e.args[0])
    exit(e.args[1])

debug_print(table, '\n')

# parse input string
parser = InputParser(input.read())

# analyze input symbols
try:
    if ll:
        table.analyzeSymbols(parser.getToken, automat)
    else:
        tree = table.analyzeSymbols(parser.getToken, automat)
        debug_print(tree, '\n')

except ValueError as e:
    lineNum = parser.getLine()
    charPos = parser.getPos()
    print(e.args[0] + "\n(file: '" + inputName + "', line: " +
          str(lineNum) + ", pos: " +
          str(charPos) + ")")
    exit(e.args[1])

exit(0)
