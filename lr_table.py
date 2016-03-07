"""LR Table."""

from rule import Rule
from enum import Enum

# -- coding: utf-8 --
__author__ = 'stepan'


class LRRule:
    """Rule with position mark."""

    def __init__(self, rule, marker):
        """Initialization."""
        self.r = rule
        if marker > len(rule.rightSide):
            raise ValueError("Mark " + marker + " is out of rule " +
                             str(rule), 40)
        self.marker = marker

    def getMarkedSymbol(self):
        """"Get symbol after marker."""
        if self.marker < len(self.r.rightSide):
            return self.r.rightSide[self.marker]
        else:
            return False

    def moveMarker(self):
        """Get new new LRRule with moved marker."""
        return LRRule(self.r, self.marker + 1)

    def __str__(self):
        """To string."""
        s = self.r.leftSide + " -> "
        for i, symbol in enumerate(self.r.rightSide):
            if self.marker == i:
                s += "●"
            s += symbol
        if self.marker == len(self.r.rightSide):
            s += "●"
        return s

    def __eq__(self, other):
        """Copare equal."""
        return self.__dict__ == other.__dict__


class Operation(Enum):
    """LR operation type."""
    shift = 0
    reduce = 1


class TableItem:
    """Table item - state number and operation."""

    def __init__(self, state, operation):
        """Initialization."""
        self.state = state
        self.operation = operation

    def __str__(self):
        """To string."""
        s = str(self.state)
        if self.operation == Operation.shift:
            s += "s"
        else:
            s += "r"
        return s


class StackItem:
    """Stack item - symbol and state."""

    def __init__(self, symbol, state):
        """Initialization."""
        self.state = state
        self.symbol = symbol

    def __str__(self):
        """To string."""
        s = "<" + self.symbol + ","
        s += str(self.state) + ">"
        return s


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


class LRTable:
    """Create LR table from given grammar."""

    def __init__(self, grammar):
        """Initialization."""
        self.grammar = grammar
        self.lrtable = []

        additionalRule = Rule('S*', [self.grammar.start])
        firstRule = LRRule(additionalRule, 0)
        groups = [self.getClosure([firstRule])]
        groupSymbols = []

        for group in groups:
            newGs, markedS = self.newGroupsFromGroup(group, len(groups))
            for newG in newGs:
                if newG not in groups:
                    groups.append(newG)
            groupSymbols.append(markedS)

        for i, gs in enumerate(groupSymbols):
            print(i, gs)
        for i, group in enumerate(groups):
            print(str(i) + ": ", ", ".join([str(rule) for rule in group]))

        self.constructFollow()

        endRule = LRRule(additionalRule, 1)
        lrtable = self.lrtable
        for i, group in enumerate(groups):
            row = {}
            for rule in group:
                if rule == endRule:
                    row[''] = -1
                    continue
                markedS = rule.getMarkedSymbol()
                if markedS is False:
                    follow = self.follow(rule.r.leftSide)
                    for symbol in follow:
                        row[symbol] = TableItem(
                            self.grammar.rules.index(rule.r), Operation.reduce)
                elif not self.grammar.isTerm(markedS):
                    row[markedS] = groupSymbols[i][markedS]
                else:
                    row[markedS] = TableItem(
                        groupSymbols[i][markedS], Operation.shift)
            lrtable.append(row)

        allSymbols = self.grammar.terminals + [''] + self.grammar.nonterminals
        print("\t".join(["#"] + allSymbols))
        for i, row in enumerate(lrtable):
            s = str(i) + "\t"
            for symbol in allSymbols:
                if symbol in row:
                    s += str(row[symbol]) + "\t"
                else:
                    s += "\t"
            print(s)

    def analyzeSymbols(self, getToken):
        """Analyze symbols by ll_table."""
        grammar = self.grammar
        table = self.lrtable

        # put end symbol and state 0 on stack
        stack = [StackItem('', 0)]

        state = 0
        token = getToken()
        while True:
            print("state: " + str(state))
            print(" ".join([str(item) for item in stack]))
            if token not in table[state]:
                raise ValueError("No rule for token '" + token +
                                 "' in state " + str(state), 40)
            alpha = table[state][token]
            if alpha == -1:
                break
            elif alpha.operation == Operation.shift:
                print(token, "-> shift")
                stack.append(StackItem(token, alpha.state))
                token = getToken()
                state = alpha.state
            else:
                rule = grammar.rules[alpha.state]
                s = "pop: "
                for s1 in reversed(rule.rightSide):
                    s += str(stack.pop())
                print(s)
                q = stack[-1].state
                print("q:", q)
                state = table[q][rule.leftSide]
                stack.append(StackItem(rule.leftSide, state))
                print(rule, "-> reduce")

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

    def constructFollow(self):
        """Construct structures for follow function."""
        self._ptable = {}
        ptable = self._ptable
        grammar = self.grammar

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

    def newGroupsFromGroup(self, group, groupNum):
        """Get new groups with moved marker."""
        markedSymbols = {}
        symbols = []
        for rule in group:
            symbol = rule.getMarkedSymbol()
            if symbol is not False:
                if symbol not in markedSymbols:
                    markedSymbols[symbol] = []
                    symbols.append(symbol)
                if rule not in markedSymbols[symbol]:
                    markedSymbols[symbol].append(rule)
        newGroups = []
        for symbol in symbols:
            rules = markedSymbols[symbol]
            newGroup = []
            for rule in rules:
                newGroup.append(rule.moveMarker())

            markedSymbols[symbol] = groupNum
            newGroups.append(self.getClosure(newGroup))
            groupNum += 1
        return [newGroups, markedSymbols]

    def getClosure(self, rules):
        """Get LR closure for rule."""
        closure = rules
        while True:
            change = False
            for rule1 in closure:
                symbol = rule1.getMarkedSymbol()
                if symbol is not False and not self.grammar.isTerm(symbol):
                    for rule2 in self.grammar.rules:
                        if rule2.leftSide == symbol:
                            markedR = LRRule(rule2, 0)
                            if markedR not in closure:
                                change = True
                                closure.append(markedR)
            if not change:
                break
        return closure
