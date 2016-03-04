"""Rule."""

from enum import Enum

# -- coding: utf-8 --
__author__ = 'stepan'


class RRole(Enum):
    """Rule role enumeration."""
    original = 0
    push = 1
    wait = 2


class Rule:
    """Represents grammar rule with symbols."""

    def __init__(self, leftSide, rightSide):
        """Initialization."""
        self.leftSide = leftSide
        self.rightSide = rightSide
        self.origRule = self

    def __str__(self):
        """To string."""
        s = self.leftSide + " -> "
        s += " ".join([symbol for symbol in self.rightSide])
        s += "   \t("
        if self.origRule is not False:
            s += self.origRule.leftSide + " -> " + \
                " ".join([symbol for symbol in self.origRule.rightSide])
        s += ")"
        return s
