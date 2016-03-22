"""Virtual tree."""

# -- coding: utf-8 --
__author__ = 'stepan'


class Symbol(str):
    """Symbol with tree level number."""
    id = 0

    def __new__(cls, str, level):
        """Initialization."""
        obj = str.__new__(cls, str)
        obj.level = level
        obj.id = "g_0"
        return obj

    def toString(self):
        """Print string and level."""
        return "'" + self + "'(" + str(self.level) + ")"

    @classmethod
    def getId(cls):
        """Unique id of object."""
        cls.id += 1
        return "s_" + str(cls.id)


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
        self.dotNames = False
        self.lrRuleFunc = self.applyLRRule

    def getDotStr(self):
        """Get string for dot."""
        s = "digraph program {\n"
        s += self.dot[0]
        for key in self.dot[1]:
            arr = self.dot[1][key]
            for item in arr:
                s += key + " -> " + item + "\n"
        s += "}\n"
        return s

    def setDotRecord(self, dotRec):
        """Function to apply rule."""
        if dotRec:
            self.dot = ["", {}]
            self.lrRuleFunc = self.applyLRDotOutput
        else:
            self.dot = False
            self.lrRuleFunc = self.applyLRRule

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

    def applyLRRule(self, symbol, rule):
        """Apply LR Rule."""
        for s in rule.rightSide:
            self.stack.append(Symbol(s, symbol.level + 1))

        if len(rule.rightSide) == 0:
            # epsilon rule - we must add tree level
            self.addLevel(symbol.level + 1)

    def applyLRDotOutput(self, symbol, rule):
        """Apply LR Rule and add DOT output."""
        dotStr = " ".join([str(newS) for newS in rule.rightSide])
        dotId = Symbol.getId()
        for s in rule.rightSide:
            newS = Symbol(s, symbol.level + 1)
            newS.id = dotId
            self.stack.append(newS)

        self.dot[0] += dotId + " [label=\"" +\
            dotStr + "\"];\n"
        if symbol.id not in self.dot[1]:
            self.dot[1][symbol.id] = []
        self.dot[1][symbol.id] = [dotId] + self.dot[1][symbol.id]

        if len(rule.rightSide) == 0:
            # epsilon rule - we must add tree level
            self.addLevel(symbol.level + 1)

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
            self.lrRuleFunc(symbol, rule)

            print("stack:   ", symbolArrPrint(self.stack))

    def applyLL(self, rule):
        """Apply original rules to tree."""
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
