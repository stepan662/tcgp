"""Grammar."""

from enum import Enum
from operation import Operation

# -- coding: utf-8 --
__author__ = 'stepan'


class Direction(Enum):
    """Asociativity direction."""
    left = 0
    right = 1
    nonassoc = 2


class PrecItem:
    """Precedence table item."""
    def __init__(self, dir, priority):
        """Initialization."""
        self.dir = dir
        self.priority = priority


class PrecedenceTable:
    """Represents Precedence table."""

    def __init__(self):
        """Initialization."""
        self.table = {}
        self.priorityCounter = 0

    def addPrecedence(self, direction, terms):
        """Add precedence rule."""
        directions = ('left', 'right', 'nonassoc')
        if direction not in directions:
            raise ValueError("Undefined Associative property '" +
                             direction + "'", 6)
        for term in terms:
            if term in self.table:
                raise ValueError("Precedence for '" + term +
                                 "' is defined twice.", 3)
            self.table[term] = PrecItem(Direction(directions.index(direction)),
                                        self.priorityCounter)

        self.priorityCounter += 1

    def isDefined(self, symbol):
        """Symbol in precedence table."""
        return symbol in self.table

    def getPrecedence(self, stack, actual):
        """Get operation by precedence table."""
        onStack = self._getFirstPrecedenceSymbol(stack)
        if onStack is False:
            return False
        if onStack not in self.table or actual not in self.table:
            return False
        return self._shiftOrReduce(onStack, actual)

    def _shiftOrReduce(self, onStack, actual):
        onSt = self.table[onStack]
        actu = self.table[actual]
        if onSt.priority == actu.priority:
            if onSt.dir == Direction.right:
                return Operation.shift
            elif onSt.dir == Direction.left:
                return Operation.reduce
            else:
                raise ValueError("Nonassoc precedence token '" + onStack +
                                 "' is on stack.", 1)
        elif onSt.priority < actu.priority:
            return Operation.reduce

        else:
            return Operation.shift

    def _getFirstPrecedenceSymbol(self, stack):
        for symbol in reversed(stack):
            if self.isDefined(symbol):
                return symbol
        return False

    def __str__(self):
        """To string."""
        symbols = self.table.keys()
        s = "s, a\t" + "\t".join([symb if symb != '' else '$'
                                 for symb in symbols]) + '\n'
        for symb1 in symbols:
            s += symb1 if symb1 != '' else '$'
            for symb2 in symbols:
                s += '\t'
                try:
                    op = self._shiftOrReduce(symb1, symb2)
                    if op is not False:
                        s += "s" if op == Operation.shift else "r"
                except ValueError:
                    s += "!"
            s += '\n'

        return s
