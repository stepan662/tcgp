"""Grammar."""

from rule import Rule

# -- coding: utf-8 --
__author__ = 'stepan'
__license__ = 'MIT'
__version__ = '1.0'


class Grammar:
    """Represents grammar with all components."""

    def __init__(self):
        """Initialization."""
        self.rules = []
        self.terminals = []
        self.nonterminals = []
        self.start = False

    def addNonTerminal(self, name):
        """Add non-terminal."""
        if name == '':
            raise ValueError("Invalid terminal symbol '" + name +
                             "'", 3)
        if name in self.terminals:
            raise ValueError("Symbol '" + name +
                             "' is already in terminals", 3)
        if name in self.nonterminals:
            raise ValueError("Duplicate symbol '" + name +
                             "' in nonterminals", 3)
        self.nonterminals.append(name)

    def addTerminal(self, name):
        """Add terminal symbol."""
        if name == '':
            raise ValueError("Invalid non-terminal symbol'" + name +
                             "'", 3)
        if name in self.nonterminals:
            raise ValueError("Symbol '" + name +
                             "' is already in non-terminals", 3)
        if name in self.terminals:
            raise ValueError("Duplicate symbol '" + name +
                             "' in terminals", 3)
        self.terminals.append(name)

    def addRule(self, leftSide, rightSide):
        """Add rule to symbol."""
        if self.isTerm(leftSide):
            # left side must be non-terminal
            raise ValueError("Left side of rule can't be terminal", 3)
        for symbol in rightSide:
            # checks if symbol is in grammar
            self.isTerm(symbol)
        # include rule to grammar
        r = Rule(leftSide, rightSide)
        self.rules.append(r)

    def setStartSymbol(self, name):
        """Set start symbol."""
        if not self.isTerm(name):
            self.start = name
        else:
            raise ValueError("Start symbol '" + name +
                             "' can't be terminal.", 3)

    def isTerm(self, name):
        """Decide if symbol is terminal or not."""
        if name in self.terminals:
            return True
        elif name in self.nonterminals:
            return False
        else:
            raise ValueError("Symbol '" + name +
                             "' is not in grammar alphabet", 3)

    def __str__(self):
        """To string."""
        s = "(\n  {"
        s += ", ".join([nonterm for nonterm in self.nonterminals])
        s += "},\n  {"
        s += ", ".join(["'" + term + "'" for term in self.terminals])
        s += "},\n  {\n"
        for rule in self.rules:
            s += "    " + rule.toStringDiff(self.isTerm) + ";\n"
        s += "  },\n"
        s += "  " + str(self.start) + "\n)"
        return s
