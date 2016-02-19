"""Grammar."""

# -- coding: utf-8 --
__author__ = 'stepan'


class Grammar:
    """Represents grammar with all components."""

    def __init__(self):
        """Initialization."""
        self._symbols = {}
        self._terminals = {}
        self._start = False

    def addSymbol(self, char):
        """Add symbol symbol."""
        if len(char) != 1:
            raise ValueError("String '" + char + "' is not character", 40)

        if char not in self._symbols:
            self._symbols[char] = []
        else:
            raise ValueError("Duplicate non-terminating symbol '" +
                             char + "'", 40)

    def setTerminal(self, char):
        """Add terminating symbol."""
        if len(char) != 1:
            raise ValueError("String '" + char + "' is not character", 40)

        if char in self._terminals:
            raise ValueError("Duplicate terminating symbol '" +
                             char + "'", 40)

        if char not in self._symbols:
            raise ValueError("Selecting undefinded symbol '" +
                             char + "' as terminating", 40)
        self._symbols.pop(char)
        self._terminals[char] = True

    def addRule(self, symbol, target):
        """Add rule to symbol."""
        self._symbols[symbol].append(target)

    def setStartSymbol(self, char):
        """Set start symbol."""
        if len(char) != 1:
            raise ValueError("String '" + char + "' is not character", 40)
        self._start = char
