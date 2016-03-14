"""Rule."""

from enum import Enum

# -- coding: utf-8 --
__author__ = 'stepan'


class Command(Enum):
    """Original rule command."""
    apply = 0
    push = 1
    pop = 2


class RuleRaw:
    """Represents grammar rule with symbols."""

    def __init__(self, leftSide, rightSide):
        """Initialization."""
        self.leftSide = leftSide
        self.rightSide = rightSide

    def __str__(self):
        """To string."""
        s = self.leftSide + " -> "
        s += " ".join([symbol for symbol in self.rightSide])
        return s


class Rule(RuleRaw):
    """New rule with reference to old rule."""

    def __init__(self, leftSide, rightSide):
        """Initialization."""
        super().__init__(leftSide, rightSide)
        self.orig = [OrigRules(Command.apply, [RuleRaw(leftSide, rightSide)])]

    def __str__(self):
        """To string."""
        s = self.leftSide + " -> "
        s += " ".join([symbol for symbol in self.rightSide])
        s = s.ljust(25)
        s += "("
        s += ", ".join([str(orig) for orig in self.orig])
        s += ")"
        return s


class OrigRules:
    """Original rule with other marks."""

    def __init__(self, cmd, rules):
        """Initialization."""
        self.rules = rules
        self.cmd = cmd

    def __str__(self):
        """To string."""
        return str(self.cmd) + " " +\
            ", ".join([str(rule) for rule in self.rules])
