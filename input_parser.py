"""Parse grammar and finite state automat from file."""

from automat import Automat

# -- coding: utf-8 --
__author__ = 'stepan'
__license__ = 'MIT'
__version__ = '1.0'


class InputParser:
    """Parser of input file."""

    def __init__(self, input, terminals):
        """Start parsing."""
        self.str = input
        self.index = 0
        self._line = 1
        self._pos = 0
        self._charLine = 1
        self._charPos = 0
        self._finals = {}

        self.aut = Automat()
        start = '*S'
        self.aut.addState(start)
        self.aut.setStart(start)
        for w, symb in enumerate(terminals):
            lastState = start
            for c, char in enumerate(symb):
                newState = str(w) + "-" + str(c)
                if not self.aut.isAlpha(char):
                    self.aut.addAlpha(char)
                self.aut.addState(newState)
                self.aut.addRule(lastState, char, newState)
                lastState = newState
            self.aut.setTerminating(lastState)
            self._finals[lastState] = symb

        self.aut.dropERules()
        self.aut.determinate()

    def getLine(self):
        """Get last token line."""
        return self._line

    def getPos(self):
        """Get last token position."""
        if self._pos == 0:
            return 1
        return self._pos

    def getToken(self):
        """Load next token."""
        ch = self._getChar()
        self._line = self._charLine
        self._pos = self._charPos
        state = 'begin'
        s = ''
        startState = self.aut.getStart()
        while ch is not False:
            # skip white chars
            if state == 'begin':
                self._line = self._charLine
                self._pos = self._charPos
                if ch.isspace():
                    state = 'begin'
                else:
                    state = self.aut.applyCharToState(ch, startState)
                    if state is False:
                        raise ValueError("Input string error on character '" +
                                         ch + "'.", 1)
                    s += ch
            else:
                tmp = self.aut.applyCharToState(ch, state)
                if tmp is False:
                    self._ungetChar()
                    finals = state.split("|")
                    strs = []
                    for final in finals:
                        if final in self._finals:
                            strs.append(self._finals[final])
                    if len(strs) == 1:
                        return strs[0]
                    elif len(strs) == 0:
                        raise ValueError("Symbol '" + s + "' is not "
                                         "in terminals.", 1)
                s += ch
                state = tmp

            ch = self._getChar()

        # return empty token after reading whole file
        return ''

    def _ungetChar(self):
        """Unget one character."""
        if self.index > 0:
            self.index -= 1
            if self.str[self.index] == '\n':
                # line counter
                self._charLine -= 1
                self._charPos = self._lastCharPos
            else:
                self._charPos -= 1
        else:
            raise ValueError("Nothing to unget", 40)

    def _getChar(self):
        """Load one character from input."""
        if self.index < len(self.str):
            ch = self.str[self.index]
            if ch == '\n':
                # line counter
                self._charLine += 1
                self._lastCharPos = self._charPos
                self._charPos = 0
            else:
                self._charPos += 1
            self.index += 1
            return ch
        else:
            return False
