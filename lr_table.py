"""LR Table."""

from rule import Rule
from operation import Operation
from virtual_tree import VirtualTree
from eff import EFF
from debug_print import debug_print
from debug_print import Debug

# -- coding: utf-8 --
__author__ = 'stepan'


class LRRule:
    """Rule with position mark."""

    def __init__(self, rule, marker):
        """Initialization."""
        self.r = rule
        if marker > len(rule.rightSide):
            raise ValueError("Mark " + marker + " is out of rule " +
                             str(rule), 99)
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
                s += "•"
            elif i != 0:
                s += " "
            s += symbol
        if self.marker == len(self.r.rightSide):
            s += "•"
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

    shiftReduceAllow = False
    reduceReduceAllow = False

    @classmethod
    def setConflicts(cls, sr, rr):
        """Set up allowed conflicts."""
        cls.shiftReduceAllow = sr
        cls.reduceReduceAllow = rr

    def __init__(self, item):
        """Initialization."""
        self.reduce = []
        self.shift = False
        self.addItem(item)
        self.isShiftReduce = False
        self.isReduceReduce = False

    def getReduce(self):
        """Get reduce array."""
        return self.reduce

    def getItem(self, operation=False):
        """Get item."""
        if operation is False:
            if self.shift:
                return self.shift
            else:
                return self.reduce[0]
        elif operation == Operation.shift:
            return self.shift
        else:
            return self.reduce[0]

    def checkConflicts(self):
        """Check shift-reduce and reduce-reduce conflict."""
        cls = type(self)
        if self.shift is not False and len(self.reduce) == 1:
            self.isShiftReduce = True
            if not cls.shiftReduceAllow:
                return False

        if self.shift is False and len(self.reduce) >= 2:
            self.isReduceReduce = True
            if not cls.reduceReduceAllow:
                return False
        return True

    def addItem(self, item):
        """Add item to table item."""
        if item.operation == Operation.shift:
            if self.shift is not False and self.shift != item:
                # shift-shift conflict
                return False
            elif self.shift is False:
                # shift-reduce or no conflict - ok
                self.shift = item
        else:
            if item not in self.reduce:
                self.reduce.append(item)

        return self.checkConflicts()

    def __str__(self):
        """To string."""
        s = "("
        s += " ".join([str(op) for op in self.reduce + [self.shift] if op])
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
        return ", ".join([str(rule) for rule in self.rules])

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

    def __init__(self, grammar, precedence, automat):
        """Initialization."""
        self.grammar = grammar
        self.automat = automat
        self.lrtable = []
        self.precendece = precedence

        # setup table item for allowing conflicts
        # based on what instruments (automat, precedence) are available
        TableItem.setConflicts(
            self.automat is not False or self.precendece is not False,
            self.automat is not False
        )

        additionalRule = Rule('S*', [self.grammar.start])
        self.grammar.rules = [additionalRule] + self.grammar.rules
        self.grammar.nonterminals = ['S*'] + self.grammar.nonterminals
        firstRule = LRRule(additionalRule, 0)

        # add priorities to rules by their order
        for i, rule in enumerate(reversed(self.grammar.rules)):
            rule.priority = i

        self.groups = LRGroups(grammar, firstRule)
        debug_print('groups', self.groups, '\n')
        groups = self.groups

        self.eff = EFF(grammar)
        debug_print('eff', self.eff, '\n')

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
        debug_print('table', self)

    def _addToTable(self, group, symbol, item):
        row = self.lrtable[group]
        if symbol in row:
            # there is conflict in lr table
            if type(row[symbol]) == TableItem and type(item) == Item:
                # probably shift - reduce conflict - no problem now
                if not row[symbol].addItem(item):
                    conflict = "Reduce-reduce"\
                        if row[symbol].isReduceReduce\
                        else "Shift-reduce"
                    debug_print('table', self)
                    raise ValueError(conflict + " conflict in lr table on " +
                                     "position [" +
                                     str(group) + ", " + str(symbol) + "]", 4)

            elif row[symbol] != item:
                # two numbers can't be on same place in table
                raise ValueError("Conflict in lr table:\n[" +
                                 str(group) + ", " + str(symbol) + "] " +
                                 "can be " + str(row[symbol]) +
                                 " or " +
                                 str(item), 4)
        else:
            # no conflict
            if type(item) == Item:
                # create table item object
                row[symbol] = TableItem(item)
            else:
                # simple number
                row[symbol] = item

    def analyzeSymbols(self, getToken):
        """Analyze symbols by ll_table."""
        grammar = self.grammar
        table = self.lrtable
        automat = self.automat

        # put end symbol and state 0 on stack
        stack = [StackItem('', 0)]

        state = 0
        token = getToken()
        tree = VirtualTree(automat, self.grammar, False)
        err = False
        self.exit_code = 1
        try:
            while True:
                if Debug.isActivated('stack'):
                    debug_print('stack', state,
                                "".join([str(item) for item in stack]))

                if token not in self.grammar.terminals and token != '':
                    # input symbol is not in grammar alphabet
                    # no matter what this string doesn't bellow to grammar
                    self.exit_code = 1
                    raise ValueError("Symbol '" + token +
                                     "' is not in grammar alphabet.")
                if token not in table[state]:
                    # no rule for this symbol and state
                    raise ValueError("No rule for token '" + token +
                                     "' in state " + str(state))
                # get item from table
                alpha = table[state][token]
                if alpha == -1:
                    # we are at the end
                    break

                # get item (solve conflicts)
                item = self._getItem(
                    stack, alpha, state, token, tree)

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
                debug_print('trees', tree, '\n')

            tree.checkTree()
        except ValueError as e:
            err = ValueError(e.args[0], self.exit_code)

        if err:
            debug_print('tree', tree)
            raise err

        return tree

    def _getItem(self, stack, alpha, state, token, tree):
        grammar = self.grammar
        item = False
        if alpha.isShiftReduce:
            # shift-reduce conflict
            if self.precendece is not False:
                # try to decide conflict by precedence table
                operation = self.precendece.getPrecedence(
                    stack, token)
                if operation is not False:
                    item = alpha.getItem(operation)
                    if operation == Operation.reduce:
                        if not tree.applyRule(grammar.rules[item.state]):
                            raise\
                                ValueError("Rule " +
                                           str(grammar.rules[item.state]) +
                                           " can't be used, because " +
                                           "of tree conflict.")

                        debug_print('rules', grammar.rules[item.state])
                    else:
                        tree.pushSymbol(token)
                        debug_print('rules', "shift", token)

            if item is False and self.automat is not False:
                # no precedence help, try to solve it by tree conflict
                item = alpha.getItem(Operation.reduce)
                states = tree.tryApplyRule(grammar.rules[item.state])
                if states is False:
                    # if there is conflict, just shift
                    debug_print('rules', "try",
                                grammar.rules[item.state],
                                "no - shift", token)
                    item = alpha.getItem(Operation.shift)
                    tree.pushSymbol(token)
                else:
                    debug_print('rules', "try",
                                grammar.rules[item.state],
                                "success")
                    # we are just guessing - if there
                    # gonna be fail in future that doesn't
                    # mean, that string can't be in grammar
                    self.exit_code = 2
                    tree.applyRule(grammar.rules[item.state], states)
            elif item is False:
                # we don't know what to do - shift-reduce conflict
                self.exit_code = 2
                raise ValueError("Unhandled shift-reduce " +
                                 "conflict in lr table on position [" +
                                 str(state) + "," + token + "], ")

        elif alpha.isReduceReduce:
            # reduce-reduce conflict
            possibleRules = []
            for it in alpha.getReduce():
                rule = grammar.rules[it.state]
                states = tree.tryApplyRule(rule)
                if states is not False:
                    possibleRules.append((it, rule, states))

            if len(possibleRules) > 1:
                # multiple options
                # we don't know what rule use - it is possible
                # that some way leads to success
                self.exit_code = 2
                options = "\n".join([str(pos[1])
                                     for pos in possibleRules])
                raise ValueError("Unhandled reduce-reduce " +
                                 "conflict in lr table on position [" +
                                 str(state) + "," + token + "], " +
                                 "got theese options:\n" + options)
            elif len(possibleRules) == 1:
                # got only one option
                pos = possibleRules[0]
                tree.applyRule(pos[1], pos[2])
                item = pos[0]
            else:
                raise ValueError("No rule fits to tree for " +
                                 "reduce-reduce conflict in lr " +
                                 "table, on position [" +
                                 str(state) + "," + token + "]")
        else:
            # no conflict, get operation
            item = alpha.getItem()
            if item.operation == Operation.shift:
                tree.pushSymbol(token)
                debug_print('rules', "shift", token)
            else:
                if not tree.applyRule(grammar.rules[item.state]):
                    raise ValueError("Rule " +
                                     str(grammar.rules[item.state]) +
                                     " can't be used, because " +
                                     "of tree conflict.")
                else:
                    debug_print('rules', grammar.rules[item.state])
        return item

    def __str__(self):
        """To string."""
        allSymbols = self.grammar.terminals + [''] + self.grammar.nonterminals
        s = "\t".join([symbol if symbol != '' else '$'
                       for symbol in ["#"] + allSymbols]) + "\n"
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
