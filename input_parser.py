"""Parse grammar and finite state automat from file."""

# -- coding: utf-8 --
__author__ = 'stepan'


class Symbol:
    """Symbol with line and position."""
    def __init__(self, str, line, position):
        """Initialization."""
        self.str = str
        self.line = line
        self.position = position

    def add(self, char):
        """Add char to string of symbol."""
        self.str += char


class InputParser:
    """Parser of input file."""

    def __init__(self, input):
        """Initialization."""
        state = 'out'
        symbol = False
        self.arr = []
        self.line = 1
        self.position = 0
        lineNum = 1
        charNum = 0
        for char in input:
            if char == '\n':
                lineNum += 1
                charNum = 0
            else:
                charNum += 1

            if state == 'out':
                if not char.isspace():
                    symbol = Symbol(char, lineNum, charNum)
                    state = 'in'

            elif state == 'in':
                if not char.isspace():
                    symbol.add(char)
                else:
                    self.arr.append(symbol)
                    state = 'out'

        self.arr.append(Symbol('', lineNum, charNum + 1))

    def getToken(self):
        """Finite state machine parser."""
        if len(self.arr) == 1:
            symbol = self.arr[0]
        else:
            symbol = self.arr.pop(0)
        self.line = symbol.line
        self.position = symbol.position
        return symbol.str

    def getLine(self):
        """Get line of last symbol."""
        return self.line

    def getPos(self):
        """Get position of last symbol."""
        if self.position == 0:
            return 1
        else:
            return self.position
