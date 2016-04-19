"""Virtual tree."""

# -- coding: utf-8 --
__author__ = 'stepan'


class SymbTreeIterator:
    """Symbol tree iterator."""

    def __init__(self, symb):
        """Initialization."""
        self.symb = symb

    def __next__(self):
        """Iterate over level."""
        if not self.symb:
            raise StopIteration
        else:
            symb = self.symb
            self.symb = self.symb.next
            return symb


class SymbolTree(str):
    """Symbol with tree level number."""

    def __init__(self, str):
        """Initialization."""
        self.str = str
        self.children = []
        self.next = False

    def getLastOnLevel(self):
        """Get last symbol on level."""
        symbol = self
        while symbol.next:
            symbol = symbol.next
        return symbol

    def getFirstSymbols(self):
        """Get first symbol on each level."""
        symbols = [self]
        symbol = self
        while True:
            if len(symbol.children) != 0:
                # got children
                symbol = symbol.children[0]
                symbols.append(symbol)
            elif symbol.next:
                # got next
                symbol = symbol.next
            else:
                # finish
                break
        return symbols

    def getLastSymbols(self):
        """Get last symbol on each level."""
        symbols = self.getFirstSymbols()
        # get first symbols
        for i, symbol in enumerate(symbols):
            # on each level move to last symbol
            symbols[i] = symbol.getLastOnLevel()
        return symbols

    def toLevels(self):
        """Get str levels of subtree."""
        levels = []
        width = 0
        lastW = 0
        for child in self.children:
            subLevels, w = child.toLevels()
            width += w + 1
            for i, level in enumerate(levels):
                if len(subLevels) > 0:
                    subLevel = subLevels.pop(0)
                    levels[i] = level.ljust(lastW) + subLevel
                else:
                    break
            for subLevel in subLevels:
                levels.append("".rjust(lastW) + subLevel)
            lastW = width

        if len(self.children) == 0:
            width = len(self.str)
        else:
            width -= 1
        levels = [self.str.rjust((width + 1) // 2)] + levels
        return levels, width

    def __eq__(self, other):
        """Check if equal."""
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __iter__(self):
        """Iterate over level."""
        return SymbTreeIterator(self)

    def eqStr(self, other):
        """Compare with string."""
        if isinstance(other, str):
            return self.str == other
        else:
            return False

    def __str__(self):
        """To string."""
        return self.str


class Tree:
    """Composing of virtual tree from original rules."""
    def __init__(self, aut, grammar):
        """Initialization."""
        self.aut = aut
        self.grammar = grammar
        self.stack = []
        self.autStates = []
        if self.aut:
            self._generateDict()

    def _ruleSymbols(self, rule):
        # take symbols, that are in rule, from stack
        if len(rule.rightSide) > 0:
            children = self.stack[-len(rule.rightSide):]
        else:
            children = []
        return children

    def applyRule(self, rule, autStates=False):
        """Apply rule to tree."""
        sNew = SymbolTree(rule.leftSide)
        # take symbols, that are in rule, from stack
        children = self._ruleSymbols(rule)
        treeIndex = len(self.stack) - len(rule.rightSide)

        if self.aut:
            if autStates is False:
                if self.aut is not False:
                    autStates = self.tryApplyRule(rule)
                    if autStates is False:
                        return False

            self.autStates = self.autStates[:treeIndex]
            self.autStates.append(autStates)

        sNew.children = self.mergeTrees(children)

        if len(rule.rightSide) > 0:
            # remove symbols from stack
            self.stack = self.stack[:-len(rule.rightSide)]

        self.stack.append(sNew)
        return True

    def pushSymbol(self, symbol):
        """Push new symbol."""
        if self.aut:
            if len(self.stack) == 0 and self.aut:
                startSymbol = self.aut.getStart()
            else:
                startSymbol = False

            newState = self.applyCharToState(symbol, startSymbol)
            self.autStates.append([newState])
            if newState is False:
                raise ValueError("Pushed symbol '" + symbol + "' is not " +
                                 "accepted by automat.", 1)

        self.stack.append(SymbolTree(symbol))

    def tryApplyRule(self, rule):
        """Try to merge trees."""
        # copy automat states

        if not self.aut:
            raise ValueError("Can't check tree, when there is no automat.", 99)

        treeIndex = len(self.stack) - len(rule.rightSide)

        firstState = False

        if treeIndex == 0:
            # we are working with leftmost tree
            firstState = self.aut.getStart()

        trees = self._ruleSymbols(rule)[1:]
        if treeIndex == len(self.stack):
            # epsilon rule
            autStates = []
        else:
            autStates = list(self.autStates[treeIndex])
        # check levels by automat
        for child in trees:
            levels = child.getFirstSymbols()
            for i, symbol in enumerate(levels):
                while i >= len(autStates):
                    autStates.append(firstState)
                # s = str(i) + ": " + str(autStates[i])
                while symbol:
                    # s += "'" + symbol.str + "' -> "
                    autStates[i] =\
                        self.applyCharToState(
                            symbol.str, autStates[i])
                    if autStates[i] is False:
                        return False
                    # s += str(autStates[i])
                    symbol = symbol.next
                # print(autStates)
                # print(s)
        # success
        # new autStates are ok
        newState = self.applyCharToState(rule.leftSide, firstState)
        if newState is False:
            return False
        autStates = [newState] + autStates
        return autStates

    def applyCharToState(self, char, state):
        """Apply char to state(s) by automaton."""
        if state is False:
            # we don't know in which state we are - take all possible
            return self._dict[char]
        elif isinstance(state, type(set())):
            # state is set of states - there is more possible states
            # lets try all of them
            newStates = set()
            for st in state:
                newState = self.aut.applyCharToState(char, st)
                if newState is not False:
                    newStates.add(newState)
            if len(newStates) == 0:
                return False
            return newStates
        else:
            return self.aut.applyCharToState(char, state)

    def _generateDict(self):
        """Generate dictionary for unknown start state."""
        self._dict = {}
        for symbol in self.aut._alphabet:
            self._dict[symbol] = set()

        for stName in self.aut._states:
            state = self.aut._states[stName]
            for symbol in state._rules:
                newStates = state._rules[symbol]
                self._dict[symbol].update(newStates)

    def mergeTrees(self, children):
        """Connect children trees."""
        if not children:
            # empty array
            return []

        myChildren = []
        myChildren.append(children[0])
        lastSymbols = children[0].getLastSymbols()
        for child in children[1:]:
            # add child to my children
            myChildren.append(child)
            # connect trees levels
            for i, newSymbol in enumerate(child.getFirstSymbols()):
                # connect last symbols with first
                if i < len(lastSymbols):
                    lastSymbols[i].next = newSymbol
                else:
                    lastSymbols.append(newSymbol)

            for i, symbol in enumerate(lastSymbols):
                # move to last symbols on each level
                lastSymbols[i] = symbol.getLastOnLevel()
        return myChildren

    def checkTree(self):
        """Check if all levels states are in terminating state."""
        if self.aut and self.autStates:
            for i, state in enumerate(self.autStates[0]):
                if not self.aut.isTerm(state):
                    raise ValueError('Level ' + str(i) +
                                     ' is not in final state.', 1)
        return True

    def __str__(self):
        """To string."""
        levels = []
        lastW = 0
        for symbol in self.stack:
            subLevels, w = symbol.toLevels()
            for i, subLev in enumerate(subLevels):
                if i >= len(levels):
                    levels.append("")
                levels[i] = levels[i].ljust(lastW) + subLev
            lastW += w + 2

        return "\n".join([level for level in levels])

    def strWithBug(self, bug):
        """To string with printed bug from check tree function."""
        pass
