"""LR Table."""

from rule import Rule
from operation import Operation
from virtual_tree import VirtualTree
from eff import EFF

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
        """Check if equal."""
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False


class Item:
    """Item - state number and operation."""

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

    def __eq__(self, other):
        """Check if equal."""
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False


class TableItem:
    """Table item array of conflicting Items."""
    def __init__(self, item):
        """Initialization."""
        self.operations = [False, False]
        self.operations[item.operation.value] = item

        self.operation = item
        self.conflict = False

    def getItem(self, operation):
        """Get item."""
        return self.operations[operation.value]

    def addItem(self, item):
        """Add confilcting item."""
        self.conflict = True
        if self.operations[item.operation.value] is False:
            self.operations[item.operation.value] = item
        else:
            ValueError("Non reduce - shift error", 40)

    def __str__(self):
        """To string."""
        s = "("
        s += " ".join([str(op) for op in self.operations if op])
        s += ")"

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


class LRGroup:
    """State group of rules with marker."""
    def __init__(self, rules):
        """Init with init rules and make hash out of it."""
        self.rules = rules

        # create unique id from ids of original rules and markers
        # this is importnant for faster comparing of groups
        self.id = "".join([str(id(rule.r)) + str(rule.marker)
                          for rule in rules])
        self.transitions = {}

    def addTransition(self, symbol, stateId):
        """Add transition to group."""
        self.transitions[symbol] = stateId

    def getMarkedSymbols(self):
        """Get array of symbols after marker in group."""
        markedSymbols = {}
        for rule in self.rules:
            symbol = rule.getMarkedSymbol()
            if symbol is not False:
                if symbol not in markedSymbols:
                    markedSymbols[symbol] = []
                if rule not in markedSymbols[symbol]:
                    markedSymbols[symbol].append(rule)
        return markedSymbols

    def __str__(self):
        """To string."""
        s = ", ".join([str(rule) for rule in self.rules])
        s += "\tT: " + str(self.transitions)
        return s

    def __eq__(self, other):
        """Compare groups by id generated from original rules nad markers."""
        if isinstance(other, self.__class__):
            return self.id == other.id
        else:
            return False


class LRGroups:
    """LR State groups generator and helper."""

    def __init__(self, grammar, firstRule):
        """Create state groups from grammar."""
        self.grammar = grammar
        firstGroup = LRGroup([firstRule])

        self.groups = [firstGroup]

        # create state groups
        for i, group in enumerate(self.groups):
            self._groupClosure(group)
            self.newGroupsFromGroup(group)

    def newGroupsFromGroup(self, group):
        """Get new groups with moved marker."""
        markedSymbols = group.getMarkedSymbols()
        for symbol in markedSymbols:
            rules = markedSymbols[symbol]
            groupRules = []
            for rule in rules:
                groupRules.append(rule.moveMarker())
            newGroup = LRGroup(groupRules)
            if newGroup not in self.groups:
                # group composed from this rules is not in groups
                self.groups.append(newGroup)
            group.addTransition(symbol, self.groups.index(newGroup))

    def _groupClosure(self, group):
        """Get LR closure for rule."""
        while True:
            change = False
            for rule1 in group.rules:
                symbol = rule1.getMarkedSymbol()
                if symbol is not False and not self.grammar.isTerm(symbol):
                    for rule2 in self.grammar.rules:
                        if rule2.leftSide == symbol:
                            markedR = LRRule(rule2, 0)
                            if markedR not in group.rules:
                                change = True
                                group.rules.append(markedR)
            if not change:
                break

    def __str__(self):
        """"To string."""
        s = ""
        s = "\n".join([str(i) + ": " + str(group)
                       for i, group in enumerate(self.groups)])
        return s


class LRTable:
    """Create LR table from given grammar."""

    def __init__(self, grammar, precedence):
        """Initialization."""
        self.grammar = grammar
        self.lrtable = []
        self.precendece = precedence

        additionalRule = Rule('S*', [self.grammar.start])
        self.grammar.rules = [additionalRule] + self.grammar.rules
        self.grammar.nonterminals = ['S*'] + self.grammar.nonterminals
        firstRule = LRRule(additionalRule, 0)

        # add priorities to rules by their order
        for i, rule in enumerate(reversed(self.grammar.rules)):
            rule.priority = i

        self.groups = LRGroups(grammar, firstRule)
        groups = self.groups
        # print(groups)

        self.eff = EFF(grammar)

        endRule = LRRule(additionalRule, 1)
        lrtable = self.lrtable
        for i, group in enumerate(groups.groups):
            row = {}
            for rule in group.rules:
                if rule == endRule:
                    row[''] = -1
                    continue
                markedS = rule.getMarkedSymbol()
                if markedS is False:
                    follow = self.eff.follow(rule.r.leftSide)
                    for symbol in follow:
                        row[symbol] = TableItem(Item(
                            self.grammar.rules.index(rule.r),
                            Operation.reduce))
                elif not self.grammar.isTerm(markedS):
                    row[markedS] = group.transitions[markedS]
                else:
                    tIt = Item(group.transitions[markedS],
                               Operation.shift)
                    if markedS in row:
                        row[markedS].addItem(tIt)
                        # shift - reduce conflict
                        # print(i, markedS, ":", row[markedS])
                        # print(row[markedS].getItem(Operation.reduce).state)
                    else:
                        row[markedS] = TableItem(tIt)
            lrtable.append(row)
        print(self)

    def _getFirstPrecedenceSymbol(self, stack):
        for symbol in reversed(stack):
            if symbol.symbol == '':
                raise ValueError("No precedence symbol on stack.", 40)

            if (self.precendece.isDefined(symbol.symbol) or
                    self.grammar.isTerm(symbol.symbol)):
                return symbol.symbol

    def analyzeSymbols(self, getToken, automat):
        """Analyze symbols by ll_table."""
        grammar = self.grammar
        table = self.lrtable

        # put end symbol and state 0 on stack
        stack = [StackItem('', 0)]

        state = 0
        token = getToken()
        rulesArr = []
        while True:
            print(" ".join([str(item) for item in stack]))
            if token not in self.grammar.terminals and token != '':
                raise ValueError("Symbol '" + token +
                                 "' is not in grammar alphabet.", 40)
            if token not in table[state]:
                raise ValueError("No rule for token '" + token +
                                 "' in state " + str(state), 40)
            alpha = table[state][token]
            if alpha == -1:
                break

            item = alpha.operation
            if alpha.conflict:
                operation = self.precendece.getPrecedence(
                    self._getFirstPrecedenceSymbol(stack),
                    token)
                item = alpha.getItem(operation)

            if item.operation == Operation.shift:
                stack.append(StackItem(token, item.state))
                token = getToken()
                state = item.state
            else:
                rule = grammar.rules[item.state]
                for s1 in reversed(rule.rightSide):
                    pSymbol = stack.pop()
                    if pSymbol.symbol != s1:
                        raise ValueError("Expecting '" + str(s1) +
                                         "', got '" + str(pSymbol) +
                                         "' from rule " + str(rule))
                q = stack[-1].state
                state = table[q][rule.leftSide]
                stack.append(StackItem(rule.leftSide, state))
                print(rule)
                rulesArr.append(rule)

        tree = VirtualTree(self.grammar.start)
        tree.applyLR(reversed(rulesArr))
        # check levels of virtual tree
        if automat is not False:
            levels = tree.getFinalStrLR()
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
        else:
            levels = tree.getFinalStrLR()
            for level in levels:
                s = ""
                for symbol in level:
                    s += symbol + " "
                print(s)

    def __str__(self):
        """To string."""
        allSymbols = self.grammar.terminals + [''] + self.grammar.nonterminals
        s = "\t".join(["#"] + allSymbols) + "\n"
        for i, row in enumerate(self.lrtable):
            s += str(i) + "\t"
            for symbol in allSymbols:
                if symbol in row:
                    s += str(row[symbol]) + "\t"
                else:
                    s += "\t"
            s += "\n"
        return s
