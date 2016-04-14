"""Rule."""


# -- coding: utf-8 --
__author__ = 'stepan'


class Rule:
    """New rule with reference to old rule."""

    def __init__(self, leftSide, rightSide):
        """Initialization."""
        self.leftSide = leftSide
        self.rightSide = rightSide

    def __str__(self):
        """To string."""
        s = self.leftSide + " -> "
        s += " ".join([symbol for symbol in self.rightSide])
        return s

    def toStringDiff(self, isTerm):
        """To string."""
        s = self.leftSide + " -> "
        s += " ".join(["'" + symbol + "'" if isTerm(symbol) else symbol
                       for symbol in self.rightSide])
        return s
