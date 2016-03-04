"""LL Table."""

# -- coding: utf-8 --
__author__ = 'stepan'


class PredictRow:
    """Represents 3 columns (Empty, First, Follow)."""

    def __init__(self):
        """Initialization."""
        self.empty = False
        self.first = set()
        self.follow = set()

    def __str__(self):
        """To string."""
        s = ""
        s += str(self.empty) + " "
        s += str(self.first) + " "
        s += str(self.follow)
        return s


class Symbol(str):
    """Symbol with tree level number."""
    def __new__(cls, str, level):
        """Initialization."""
        obj = str.__new__(cls, str)
        obj.level = level
        return obj

    def toString(self):
        """Print string and level."""
        return "'" + self + "'(" + str(self.level) + ")"


def symbolArr(strArr, level):
    """Turn string array to symbol array."""
    symbols = []
    for str in strArr:
        symbols.append(Symbol(str, level))
    return symbols


def symbolArrPrint(symbols):
    """Print Symbol array with level."""
    s = ""
    for symbol in symbols:
        s += symbol.toString() + ", "
    print(s)


class LLTable:
    """Represents ll table with fill function."""

    def __init__(self, grammar):
        """
        Fill table by rules and symbols.

        Include Empty, First, Follow and Predict algorithms
        """
        # ll table
        self._table = []
        # table of Empty, First and Follow sets
        self._ptable = {}
        # predict sets
        self._rulesPredict = []
        self._grammar = grammar

        self._dictTerms = {}
        self._dictNonTerms = {}

        rulesPredict = self._rulesPredict
        ptable = self._ptable
        grammar = self._grammar

        for nonterminal in grammar.nonterminals:
            # init ptable
            ptable[nonterminal] = PredictRow()

        for terminal in grammar.terminals:
            # init ptable
            ptable[terminal] = PredictRow()
            # first of terminal is it self
            ptable[terminal].first.add(terminal)

        # Empty and First algorithm

        while True:
            change = False      # remember if anything changed
            for rule in grammar.rules:
                ruleRow = ptable[rule.leftSide]
                for i, symbol in enumerate(rule.rightSide):
                    firstLength = len(ruleRow.first)
                    # add first of symbol to rule's first
                    ruleRow.first.update(ptable[symbol].first)
                    if firstLength != len(ruleRow.first):
                        # set is longer then before -> something has changed
                        change = True
                    if not ptable[symbol].empty:
                        # this symbol can't be erased -> stop
                        break
                    elif i == (len(rule.rightSide) - 1):
                        # all symbols can be erased
                        if not ruleRow.empty:
                            ruleRow.empty = True
                            change = True

                if len(rule.rightSide) == 0:
                    # epsilon rule
                    if ruleRow.empty is not True:
                        ruleRow.empty = True
                        change = True

            if not change:
                break

        # Follow algorithm

        # add end symbol ($) to follow of start symbol
        ptable[grammar.start].follow.add('')

        while True:
            change = False
            for rule in grammar.rules:
                ruleSymbols = rule.rightSide
                for i, symbol in enumerate(ruleSymbols):
                    if grammar.isTerm(symbol):
                        continue
                    symbolSet = ptable[symbol].follow
                    length = len(symbolSet)

                    # symbols following this one
                    rightSymbols = ruleSymbols[i + 1:]
                    symbolSet.update(self.first(rightSymbols))
                    if self.empty(rightSymbols):
                        # following symbols can be removed
                        symbolSet.update(
                            ptable[rule.leftSide].follow)

                    if length != len(symbolSet):
                        change = True
            if not change:
                break

        # Predict algorithm

        for rule in grammar.rules:
            pset = set()
            pset.update(self.first(rule.rightSide))
            if self.empty(rule.rightSide):
                pset.update(self.follow(rule.leftSide))
            rulesPredict.append(pset)

        # create dictionaries for fast searching of symbols
        for i, symbol in enumerate(grammar.terminals):
            self._dictTerms[symbol] = i

        # add end symbol to terminals
        self._dictTerms[''] = len(grammar.terminals)

        for i, symbol in enumerate(grammar.nonterminals):
            self._dictNonTerms[symbol] = i

        # init ll table
        for i in range(0, len(grammar.nonterminals)):
            self._table.append([])
            for j in range(0, len(grammar.terminals) + 1):
                self._table[i].append(False)

        # fill ll table
        for i, predict in enumerate(rulesPredict):
            rule = grammar.rules[i]
            nonterminalId = self._dictNonTerms[rule.leftSide]
            for symbol in predict:
                terminalId = self._dictTerms[symbol]
                field = self._table[nonterminalId][terminalId]
                if field is False:
                    self._table[nonterminalId][terminalId] = rule
                else:
                    raise ValueError("This is not ll grammar, " +
                                     "confict rules:\n (" + str(i) + ") " +
                                     str(rule) + "\n" + "(" +
                                     str(grammar.rules.index(field)) + ") " +
                                     str(field), 40)

        # for i, predict in enumerate(rulesPredict):
        #    st = str(i) + ":"
        #    for symbol in predict:
        #        st += " " + symbol + ","
        #    print(st)
        # for row in self._table:
        #    print(row)

    def empty(self, symbols):
        """Get empty of symbols."""
        for symbol in symbols:
            if not self._ptable[symbol].empty:
                return False
        return True

    def first(self, symbols):
        """Get first of symbols."""
        first = set()
        for symbol in symbols:
            first.update(self._ptable[symbol].first)
            if not self.empty([symbol]):
                break
        return first

    def follow(self, symbol):
        """Get follow of symbol."""
        return self._ptable[symbol].follow

    def getRule(self, nonterminal, terminal):
        """Get rule from ll table."""
        nonterminalId = self._dictNonTerms[nonterminal]
        terminalId = self._dictTerms[terminal]
        return self._table[nonterminalId][terminalId]

    def analyzeSymbols(self, getToken):
        """Analyze array of symbols by ll_table."""
        grammar = self._grammar

        # put end symbol on stack
        stack = ['']

        # first symbol
        symbol = grammar.start
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
                                             "' is not valid.")
                else:
                    # symbol and terminal are not same - error
                    raise ValueError("Expecting '" + symbol + "', got '" +
                                     input + "'")
            print([symbol] + stack)
            print(input)

    def _isTerm(self, symbol):
        return symbol in self._dictTerms
