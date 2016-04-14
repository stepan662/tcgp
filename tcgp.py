"""
Tree-Controled Grammer parser.

python3
tcgp.py
-g tests/test10.in -i tests/input10.in
"""

import sys
import traceback
import argparse
from parser import Parser
from lr_table import LRTable
from input_parser import InputParser
from debug_print import Debug
from debug_print import debug_print
from debug_print import err_print

# -- coding: utf-8 --
__author__ = 'stepan'


class ArgumentParser(argparse.ArgumentParser):
    """Redefinition of argument parser."""
    def error(self, message):
        """Print err message."""
        err_print(10, message)


def closeFiles(opened_files):
    """Close all opened files."""
    for f in opened_files:
        f.close()


def main():
    """Main function."""
    # arguments parsing
    argp = ArgumentParser(description='Tree controlled grammar parser',
                          formatter_class=argparse.RawTextHelpFormatter)

    argp.add_argument('-g', '--grammar',
                      action='store',
                      required=True,
                      type=argparse.FileType('r'),
                      help='Input grammar file'
                      )
    argp.add_argument('-p', '--print',
                      default=False,
                      nargs='+',
                      action='store',
                      metavar='CHOICE',
                      choices=['tree', 'trees', 'stack', 'rules', 'groups',
                               'table', 'eff', 'automat', 'precedence',
                               'grammar', 'all'],
                      help="Decide what to print from these CHOICES:\n" +
                      " - tree:       final derivation tree\n" +
                      " - trees:      derivation tree development\n" +
                      " - stack:      continuously print stack of symbols\n" +
                      " - rules:      continuously print applied rules\n" +
                      " - groups:     lr groups generated from rules\n" +
                      " - table:      lr table\n" +
                      " - eff:        empty, first and follow sets\n" +
                      " - automat:    print final state machine\n" +
                      " - precedence: print precedence table\n" +
                      " - grammar:    print input grammar\n" +
                      " - all:        print all\n"
                      )
    argp.add_argument('-i', '--input',
                      default=sys.stdin,
                      action='store',
                      type=argparse.FileType('r'),
                      help='Input string file, tokens separated by white space'
                      )
    argp.add_argument('-o', '--output',
                      default=sys.stdout,
                      action='store',
                      type=argparse.FileType('w'),
                      help='Output file'
                      )
    argp.add_argument('-u')

    args = argp.parse_args()

    # setup debug_print function to correspond with args
    if args.print:
        for category in args.print:
            Debug.addCategory(category)
            if category == 'trees':
                Debug.addCategory('tree')
            if category == 'all':
                Debug.setDebugMode(True)

    opened_files = [args.input, args.output, args.grammar]

    # set output to output file
    sys.stdout = args.output

    # parse input grammar
    grammarParser = Parser()

    try:
        grammarParser.parse(args.grammar.read())
    except ValueError as e:
        # there is an syntax error in input grammar
        # print with line number and filename
        lineNum = grammarParser.getLine()
        charPos = grammarParser.getPos()
        closeFiles(opened_files)
        err_print(e.args[1], e.args[0] +
                  "\n(file: '" + args.grammar.name + "', line: " +
                  str(lineNum) + ", pos: " +
                  str(charPos) + ")")

    # get grammar, automat and precednece table from parser
    grammar = grammarParser.getGrammar()
    debug_print('grammar', grammar, '\n')
    automat = grammarParser.getAutomat()
    precedence = grammarParser.getPrecedence()

    if precedence is not False:
        debug_print('precedence', precedence)

    # Prepare automat
    if automat:
        # add new state for lowest level of the tree
        # there can be all terminals
        startState = automat.getStart()
        newState = "t*"
        automat.addState(newState)
        automat.setTerminating(newState)
        for term in grammar.terminals:
            automat.addRule(startState, term, newState)
            automat.addRule(newState, term, newState)

        # determinate automat
        automat.dropERules()
        automat.determinate()

        # generate dictionary for jumping for checking substrings
        automat.generateDict()
        debug_print('automat', automat)

    # lltable = ll_table.LLTable(grammar)
    # print(lltable)
    # exit(0)

    try:
        # build lr table
        table = LRTable(grammar, precedence, automat)
    except ValueError as e:
        # error in grammar
        closeFiles(opened_files)
        err_print(e.args[1], e.args[0])

    # parse input string
    parser = InputParser(args.input.read())

    # analyze input symbols
    try:
        tree = table.analyzeSymbols(parser.getToken)
        debug_print('tree', tree, '\n')

    except ValueError as e:
        # error in input string
        lineNum = parser.getLine()
        charPos = parser.getPos()
        closeFiles(opened_files)
        err_print(e.args[1], e.args[0] +
                  "\n(file: '" + args.input.name + "', line: " +
                  str(lineNum) + ", pos: " + str(charPos) + ")")

    closeFiles(opened_files)
    sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception:
        err_print(99, traceback.format_exc())
