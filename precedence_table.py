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
                             direction + "'", 40)
        for term in terms:
            if term in self.table:
                raise ValueError("Precedence for '" + term +
                                 "' is defined twice.", 40)
            self.table[term] = PrecItem(Direction(directions.index(direction)),
                                        self.priorityCounter)

        self.priorityCounter += 1

    def isDefined(self, symbol):
        """Symbol in precedence table."""
        return symbol in self.table

    def getPrecedence(self, onStack, actual):
        """Get operation by precedence table."""
        if onStack not in self.table or actual not in self.table:
            raise ValueError("No precedence rule for symbol '" + onStack +
                             "' and '" + actual + "'.", 40)
        onSt = self.table[onStack]
        actu = self.table[actual]
        if onSt.priority == actu.priority:
            if onSt.dir == Direction.right:
                return Operation.shift
            elif onSt.dir == Direction.left:
                print("reduce")
                return Operation.reduce
            else:
                raise ValueError("Noassoc precedence token '" + onStack +
                                 "' is on stack.", 40)
        elif onSt.priority < actu.priority:
            return Operation.reduce

        else:
            return Operation.shift

    def __str__(self):
        """To string."""
        s = ""
        for line in self.table:
            s += str(line) + ": " + str(self.table[line].priority) + ", " +\
                             str(self.table[line].dir) + "\n"
        return s
