"""Finite machine state module."""

import copy

# -- coding: utf-8 --
__author__ = 'stepan'


class State:
    """
    Represent one state.

    contains links to other rules and sign if state is terminating
    """

    def __init__(self):
        """Initialization."""
        self._term = False
        self._rules = {}

    def addRule(self, char, state):
        """Add transition to other state."""
        if char in self._rules:
            if state not in self._rules[char]:
                self._rules[char].append(state)
        else:
            self._rules[char] = [state]

    def setTerm(self, value):
        """Set state as terminating."""
        self._term = value
        return self

    def isTerm(self):
        """State is/isn't terminating."""
        return self._term

    def getAllRules(self):
        """Get all rules."""
        return self._rules

    def getRules(self, char):
        """Get all rules for specific character."""
        if char in self._rules:
            return self._rules[char]
        else:
            return []

    def addNonERules(self, rules):
        """Add non epsilon rules."""
        rules = copy.deepcopy(rules)
        for char in rules:
            if char != '':
                for target in rules[char]:
                    self.addRule(char, target)

    def dropERules(self):
        """Remove epsilon rules."""
        if '' in self._rules:
            del self._rules['']
