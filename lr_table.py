"""LR Table."""

from rule import Rule
from operation import Operation
from virtual_tree import VirtualTree
from eff import EFF
from debug_print import debug_print

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
            elif i != 0:
                s += " "
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
        s = ""
        if self.operation == Operation.shift:
            s += "s"
        else:
            s += "r"
        s += str(self.state)
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
        if self.operations[item.operation.value] is False:
            # there is conflict shift - reduce conflict
            self.conflict = True
            self.operations[item.operation.value] = item
        else:
            if self.operations[item.operation.value] != item:
                # there is other conflict - table item is not the same
                return False
        return True

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
            lrtable.append({})
            for rule in group.rules:
                if rule == endRule:
                    # end point marked as -1
                    self._addToTable(i, '', -1)
                    continue
                markedS = rule.getMarkedSymbol()
                if markedS is False:
                    # marked symbol on last position - reduce operation
                    follow = self.eff.follow(rule.r.leftSide)
                    for symbol in follow:
                        item = Item(self.grammar.rules.index(rule.r),
                                    Operation.reduce)
                        self._addToTable(i, symbol, item)

                elif not self.grammar.isTerm(markedS):
                    # marked symbol is non-terminal - beta part of table
                    self._addToTable(i, markedS, group.transitions[markedS])

                else:
                    # marked symbol is terminal - shift operation
                    tIt = Item(group.transitions[markedS],
                               Operation.shift)
                    self._addToTable(i, markedS, tIt)

    def _addToTable(self, group, symbol, item):
        row = self.lrtable[group]
        if symbol in row:
            # there is conflict in lr table
            if type(row[symbol]) == TableItem and type(item) == Item:
                # probably shift - reduce conflict - no problem now
                if not row[symbol].addItem(item):
                    raise ValueError(
                        str(self) +
                        "Non shift - reduce conlict in lr table:\n[" +
                        str(group) + ", " + str(symbol) + "] " +
                        "can be " + str(row[symbol]) +
                        " or " +
                        str(item), 40)

            elif row[symbol] != item:
                # two numbers can't be on same place in table
                raise ValueError("Conflict in lr table:\n[" +
                                 str(group) + ", " + str(symbol) + "] " +
                                 "can be " + str(row[symbol]) +
                                 " or " +
                                 str(item), 40)
        else:
            # no conflict
            if type(item) == Item:
                # create table item object
                row[symbol] = TableItem(item)
            else:
                # simple number
                row[symbol] = item

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
        tree = VirtualTree(automat, self.grammar, False)
        while True:
            debug_print(state,
                        "".join([str(item) for item in reversed(stack)]))

            if token not in self.grammar.terminals and token != '':
                # input symbol is not in grammar alphabet
                raise ValueError("Symbol '" + token +
                                 "' is not in grammar alphabet.", 40)
            if token not in table[state]:
                # no rule for this symbol and state
                raise ValueError("No rule for token '" + token +
                                 "' in state " + str(state), 40)
            # get item from table
            alpha = table[state][token]
            if alpha == -1:
                # we are at the end
                break

            if alpha.conflict:
                # we have two possibilities - there is shift - reduce conflict
                # decide conflict by precedence table
                if self.precendece is False:
                    # no precedence, try to solve it by tree conflict
                    item = alpha.getItem(Operation.reduce)
                    print("here")
                    if not tree.applyRule(grammar.rules[item.state]):
                        print("conflict: reduce failed - shift instead")
                        # try to reduce virtual tree
                        # if there is conflict, just shift
                        item = alpha.getItem(Operation.shift)
                        tree.pushSymbol(token)
                else:
                    operation = self.precendece.getPrecedence(
                        self._getFirstPrecedenceSymbol(stack),
                        token)
                    item = alpha.getItem(operation)
            else:
                # no conflict, get operation
                item = alpha.operation
                if item.operation == Operation.shift:
                    tree.pushSymbol(token)
                else:
                    if not tree.applyRule(grammar.rules[item.state]):
                        raise ValueError("Tree can't be constructed.", 40)

            if item.operation == Operation.shift:
                # shift - add symbol to stack
                stack.append(StackItem(token, item.state))
                token = getToken()
                state = item.state
            else:
                # reduce - apply rule

                rule = grammar.rules[item.state]
                for s1 in reversed(rule.rightSide):
                    # check, that symbols on stack are same with right side
                    # of the rule
                    pSymbol = stack.pop()
                    if pSymbol.symbol != s1:
                        raise ValueError("Expecting '" + str(s1) +
                                         "', got '" + str(pSymbol) +
                                         "' from rule " + str(rule))
                # get state of last symbol on stack
                symbolState = stack[-1].state
                # get new state from beta table
                state = table[symbolState][rule.leftSide]
                # add rule left side to stack
                stack.append(StackItem(rule.leftSide, state))

        debug_print()
        return tree

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
            if i != len(self.lrtable) - 1:
                s += "\n"
        return s
