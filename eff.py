"""Empty, first and follow."""

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


class EFF:
    """Empty, first and follow object."""
    def __init__(self, grammar):
        """Initialization."""
        self._ptable = {}
        # predict sets

        ptable = self._ptable

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
