import ipdb
"""Virtual tree."""

# -- coding: utf-8 --
__author__ = 'stepan'


class SymbTreeIterator:
    """Symbol tree iterator."""

    def __init__(self, symb):
        """Init."""
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


class VirtualTree:
    """Composing of virtual tree from original rules."""
    def __init__(self, aut, grammar, ll):
        """Initialization."""
        self.aut = aut
        self.grammar = grammar
        if not ll:
            self.ll = False
            self.symbols = []
            self.autStates = []
        else:
            self.ll = True

    def applyRule(self, rule):
        """Apply rule to tree."""
        print("reduce", rule)
        sNew = SymbolTree(rule.leftSide)
        # take symbols, that are in rule, from stack
        if len(rule.rightSide) > 0:
            children = self.symbols[-len(rule.rightSide):]
        else:
            children = []
        check = False

        if len(self.symbols) == len(rule.rightSide) and self.aut:
            # we are working with leftmost tree, we gonna check
            check = True
            if not self.tryMerge(children[1:]):
                # children can't be merged
                print("check failed")
                return False
            print("check ok")

        sNew.children = self.mergeTrees(children)
        if check:
            # new nonterminal must be checked by automat
            # and state added to states
            newState = self.aut.applyCharToState(
                rule.leftSide, self.aut.getStart())
            self.autStates = [newState] + self.autStates

        if len(rule.rightSide) > 0:
            self.symbols = self.symbols[:-len(rule.rightSide)]

        self.symbols.append(sNew)
        print(self)
        return True

    def pushSymbol(self, symbol):
        """Push new symbol."""
        print("shift", symbol)
        if len(self.symbols) == 0 and self.aut:
            # first push must add first state into automat states
            newState = self.aut.applyCharToState(symbol, self.aut.getStart())
            self.autStates.append(newState)
        self.symbols.append(SymbolTree(symbol))
        print(self)

    def tryMerge(self, trees):
        """Try to merge trees."""
        # copy automat states
        print(trees)
        autStates = list(self.autStates)
        # check levels by automat
        for child in trees:
            levels = child.getFirstSymbols()
            for i, symbol in enumerate(levels):
                while i >= len(autStates):
                    autStates.append(self.aut.getStart())
                # s = str(i) + ": " + autStates[i]
                while symbol:
                    # s += "'" + symbol.str + "' -> "
                    try:
                        autStates[i] =\
                            self.aut.applyCharToState(
                                symbol.str, autStates[i])
                    except ValueError:
                        return False
                    # s += autStates[i]
                    symbol = symbol.next
                # print(autStates)
                # print(s)
        # success
        # new autStates are ok
        self.autStates = autStates
        return True

    def mergeTrees(self, children):
        """Connect children trees."""
        if not children:
            # empty array
            return []

        print(children)

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

    def __str__(self):
        """To string."""
        s = ""
        for symbol in self.symbols:
            levels, w = symbol.toLevels()
            # s += str(levels)
            s += "\n".join([level for level in levels]) + '\n\n'
        return s

    def strWithBug(self, bug):
        """To string with printed bug from check tree function."""
        pass
