"""LL Table."""

from virtual_tree import VirtualTree
from eff import EFF

# -- coding: utf-8 --
__author__ = 'stepan'


class LLTable:
    """Represents ll table with fill function."""

    def __init__(self, grammar):
        """
        Fill table by rules and symbols.

        Include Predict algorithms
        """
        # ll table
        self._table = {}
        # predict sets
        self._rulesPredict = []
        self._grammar = grammar

        eff = EFF(grammar)

        self._dictTerms = {}
        self._dictNonTerms = {}

        rulesPredict = self._rulesPredict

        # Predict algorithm

        for rule in grammar.rules:
            pset = set()
            pset.update(eff.first(rule.rightSide))
            if eff.empty(rule.rightSide):
                pset.update(eff.follow(rule.leftSide))
            rulesPredict.append(pset)

        # create dictionaries for fast searching of symbols
        for i, symbol in enumerate(grammar.terminals):
            self._dictTerms[symbol] = i

        # add end symbol to terminals
        self._dictTerms[''] = len(grammar.terminals)

        for i, symbol in enumerate(grammar.nonterminals):
            self._dictNonTerms[symbol] = i

        # init ll table
        for nonterm in grammar.nonterminals:
            self._table[nonterm] = {}

        # fill ll table
        for i, predict in enumerate(rulesPredict):
            rule = grammar.rules[i]
            nonterminal = rule.leftSide
            for symbol in predict:
                terminal = symbol
                row = self._table[nonterminal]
                if nonterminal not in row:
                    row[terminal] = rule
                else:
                    raise ValueError("This is not ll grammar, " +
                                     "confict rules:\n(" + str(i) + ") " +
                                     str(rule) + "\n" + "(" +
                                     str(grammar.rules.index(row[terminal])) +
                                     ") " +
                                     str(row[terminal]), 40)

    def getRule(self, nonterminal, terminal):
        """Get rule from ll table."""
        return self._table[nonterminal][terminal]

    def analyzeSymbols(self, getToken, automat):
        """Analyze array of symbols by ll_table."""
        grammar = self._grammar

        # put end symbol on stack
        stack = ['']

        # first symbol set as symbol and give it to virtual tree
        symbol = grammar.start
        virtTree = VirtualTree(symbol)
        # first input token
        input = getToken()
        # check input
        grammar.isTerm(input)

        while True:
            if not self._isTerm(symbol):
                # symbol is nonterminal - apply rule
                rule = self.getRule(symbol, input)

                if rule is False:
                    # no rule for this symbol and input
                    raise ValueError("No rule for '" + symbol + "', '" +
                                     input + "'")

                # put rule on stack and take first symbol
                stack = rule.rightSide + stack
                # apply orignal rules to virtual tree
                virtTree.applyLL(rule)
                symbol = stack.pop(0)

            else:
                # symbol is terminal, compare with input
                if input == symbol:
                    # symbol and terminal are same - ok
                    if input == '':
                        # end of file
                        break
                    else:
                        # move to the next input
                        symbol = stack.pop(0)
                        input = getToken()

                        if not self._isTerm(input):
                            # input symbol is not in terminals
                            raise ValueError("Symbol '" + input +
                                             "' is not valid.", 40)
                else:
                    # symbol and terminal are not same - error
                    raise ValueError("Expecting '" + symbol + "', got '" +
                                     input + "'", 40)
            print([symbol] + stack)
            print(input)

        # check levels of virtual tree
        if automat is not False:
            levels = virtTree.getFinalStrLL()
            bug = False
            index = -1
            for level in levels[:-1]:
                s = ""
                state = automat.getStart()
                for symbol in level:
                    s += symbol + " "
                    if not bug:
                        try:
                            state = automat.applyCharToState(symbol, state)
                        except ValueError as e:
                            index = len(s) - len(symbol)
                            bug = str(e)

                print(s)
                if not bug:
                    if not automat.isTerm(state):
                        index = len(s)
                        bug = "Automat is not in final state"

                if index != -1:
                    print("^".rjust(index))
                    index = -1

            print(" ".join([char for char in levels[-1]]))
            if bug:
                print(bug)

    def _isTerm(self, symbol):
        return symbol in self._dictTerms

    def __str__(self):
        """To string."""
        s = "\t".join([symbol for symbol in
                       ["#"] + self._grammar.terminals + ['$']])
        s += "\n"
        for nonterm in self._grammar.nonterminals:
            s += nonterm + "\t"
            row = self._table[nonterm]
            for term in self._grammar.terminals + ['']:
                if term in row:
                    s += str(self._grammar.rules.index(row[term]))
                s += "\t"
            s += "\n"
        return s
