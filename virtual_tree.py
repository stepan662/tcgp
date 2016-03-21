"""Virtual tree."""

from rule import Command

# -- coding: utf-8 --
__author__ = 'stepan'


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
    return s


class VirtualTree:
    """Composing of virtual tree from original rules."""

    def __init__(self, firstSymbol):
        """Initialization."""
        self.stack = [Symbol('', 0), Symbol(firstSymbol, 0)]
        self.blocked = []
        self.states = []

    def charOnLevelEnd(self, char, level):
        """Add char to end of tree level."""
        if level > len(self.states) - 1:
            self.states.append([])
        self.states[level].append(char)

    def addLevel(self, level):
        """Add empty level to tree."""
        if level > len(self.states) - 1:
            self.states.append([])

    def charOnLevelBegin(self, char, level):
        """Add char to begining of tree level."""
        if level > len(self.states) - 1:
            self.states.append([])
        self.states[level].insert(0, char)

    def applyLR(self, rules):
        """Apply array of rules."""
        for rule in rules:
            while True:
                # skip nonterminals
                symbol = self.stack.pop()
                if symbol == '':
                    return
                self.charOnLevelBegin(str(symbol), symbol.level)
                if symbol == rule.leftSide:
                    break
            # apply rule
            for s in rule.rightSide:
                self.stack.append(Symbol(s, symbol.level + 1))

            if len(rule.rightSide) == 0:
                # epsilon rule - we must add tree level
                self.addLevel(symbol.level + 1)

            print("stack:   ", symbolArrPrint(self.stack))

    def applyLL(self, origs):
        """Apply original rules to tree."""
        for orig in origs:
            # print("blocked: ",
            #      ", ".join([" ".join([str(oR) for oR in oRs])
            #                 for oRs in self.blocked]))
            # print("stack:   ", symbolArrPrint(self.stack))
            if orig.cmd == Command.push:
                # just push rule on blocked stack, do nothing
                self.blocked.append(orig.rules)
                # print(orig.cmd, ": ", " ,".join([str(rule)
                #                                 for rule in orig.rules]))
            else:
                # apply rules
                if orig.cmd == Command.apply:
                    # rules are simply present
                    rules = orig.rules
                elif orig.cmd == Command.pop:
                    # rules are on stack
                    rules = self.blocked.pop()
                # print(orig.cmd, ": ", " ,".join([str(rule)
                #                            for rule in rules]))

                for rule in rules:

                    while True:
                        # skip nonterminals
                        symbol = self.stack.pop()
                        if symbol == '':
                            return
                        self.charOnLevelEnd(str(symbol), symbol.level)
                        if symbol == rule.leftSide:
                            break

                    # apply rule
                    for s in reversed(rule.rightSide):
                        self.stack.append(Symbol(s, symbol.level + 1))

                    if len(rule.rightSide) == 0:
                        # epsilon rule - we must add tree level
                        self.addLevel(symbol.level + 1)

            # print("stack:   ", symbolArrPrint(self.stack))
            # print("")

    def getFinalStrLR(self):
        """Finish reading symbols from stack."""
        while True:
            # skip rest of symbols
            symbol = self.stack.pop()
            if symbol == '':
                break
            else:
                self.charOnLevelBegin(str(symbol), symbol.level)
        return self.states

    def getFinalStrLL(self):
        """Finish reading symbols from stack."""
        while True:
            # skip nonterminals
            symbol = self.stack.pop()
            if symbol == '':
                break
            else:
                self.charOnLevelEnd(str(symbol), symbol.level)
        return self.states
