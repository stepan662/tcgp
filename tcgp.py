"""Tree-Controled Grammer parser."""

import getopt
import sys
from parser import parse
from lr_table import LRTable
from ll_table import LLTable
from input_parser import InputParser

# -- coding: utf-8 --
__author__ = 'stepan'

opts, args = getopt.getopt(
    sys.argv[1:],
    "hli:o:g:",
    ["help", "ll", "input=", "output=", "grammar="])
# except getopt.GetoptError as err:
#     print help information and exit:
#    print(err)  # will print something like "option -a not recognized"
#    sys.exit(2)

input = sys.stdin
output = sys.stdout
grammarIn = False
ll = False

for o, a in opts:
    if o in ("-l", "--ll"):
        ll = True
    elif o in ("-h", "--help"):
        sys.exit()
    elif o in ("-i", "--input"):
        input = open(a, 'r')
    elif o in ("-o", "--output"):
        output = open(a, 'w')
    elif o in ("-g", "--grammar"):
        grammarIn = open(a, 'r')
    else:
        assert False, "unhandled option"

try:
    grammar, automat = parse(grammarIn.read())
except ValueError as e:
    print(e.args[0])
    exit(e.args[1])

# Determinate automat
if automat:
    automat.dropERules()
    automat.determinate()

parser = InputParser(input.read())
if ll:
    print(grammar)
    grammar.leftFactorization()
    grammar.removeDeepLeftRecursion()
    print(grammar)
    table = LLTable(grammar)
else:
    table = LRTable(grammar)

table.analyzeSymbols(parser.getToken, automat)
