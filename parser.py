"""Parse grammar and finite state automat from file."""

import automat
import grammar

# -- coding: utf-8 --
__author__ = 'stepan'


def parse(input):
    """Parse input and return grammar and automat."""
    parser = Parser(input)
    return [parser.getGrammar(), parser.getAutomat()]


class Token:
    """Object token."""

    def __init__(self, type, string):
        """Initialization."""
        self.type = type
        self.string = string


class Parser:
    """Finite state machine parser."""

    def __init__(self, input):
        """Start parsing."""
        try:
            self._parse(input)
        except ValueError as e:
            # print exception with line number
            raise ValueError(e.args[0] +
                             " (line: " + self._line.__str__() + ")",
                             e.args[1])

    def _parse(self, input):
        """Read and parse automat."""
        self.index = 0
        self.str = input
        self._line = 1
        self._charLine = 1

        # new empty grammar
        self.grammar = grammar.Grammar()

        # wait for opening brackets
        token = self._getToken()
        self._tShould(token, ['('])
        token = self._getToken()
        self._tShould(token, ['{'])

        # load non-terminals
        self._loadIdsArr(self.grammar.addNonTerminal)

        # comma and opening bracket
        token = self._getToken()
        self._tShould(token, [','])
        token = self._getToken()
        self._tShould(token, ['{'])

        # load terminals
        self._symbols(self.grammar.addTerminal)

        # comma and opening bracket
        token = self._getToken()
        self._tShould(token, [','])
        token = self._getToken()
        self._tShould(token, ['{'])

        # load rules
        self._loadGrammarRules()

        # comma and one character
        token = self._getToken()
        self._tShould(token, [','])
        token = self._getToken()
        self._tShould(token, ['id'])
        self.grammar.setStartSymbol(token.string)

        # closing bracket and comma - end of grammar
        token = self._getToken()
        self._tShould(token, [')'])
        token = self._getToken()
        self._tShould(token, [',', ''])

        if token.type == '':
            self.aut = False
            return

        # new empty automat
        self.aut = automat.Automat()

        # automat alphabet are terminals and nonterminals from grammar
        for symbol in self.grammar.nonterminals:
            self.aut.addAlpha(symbol)
        for symbol in self.grammar.terminals:
            self.aut.addAlpha(symbol)

        # wait for opening brackets
        token = self._getToken()
        self._tShould(token, ['('])
        token = self._getToken()
        self._tShould(token, ['{'])

        # load states
        self._loadIdsArr(self.aut.addState)

        # comma and opening bracket
        token = self._getToken()
        self._tShould(token, [','])
        token = self._getToken()
        self._tShould(token, ['{'])

        # load rules
        self._loadAutomatRules()

        # comma and start state
        token = self._getToken()
        self._tShould(token, [','])
        token = self._getToken()
        if token.type != 'id':
            raise ValueError("Missing start state", 40)
        else:
            self.aut.setStart(token.string)

        # comma and opening bracket
        token = self._getToken()
        self._tShould(token, [','])
        token = self._getToken()
        self._tShould(token, ['{'])

        self._terminating()

        # closing bracket and nothing
        token = self._getToken()
        self._tShould(token, [')'])
        token = self._getToken()
        self._tShould(token, [''])

    def getGrammar(self):
        """Return created grammar."""
        return self.grammar

    def getAutomat(self):
        """Return created automat."""
        return self.aut

    def _loadCharArr(self, callback):
        token = self._getToken()
        if token.type == '}':
            return  # states are empty
        while token.type != '':
            self._tShould(token, ['id'])
            if(len(token.string) > 1):
                raise ValueError("Expecting single character instead of '" +
                                 token.string + "'", 40)
            callback(token.string)
            token = self._getToken()
            self._tShould(token, [',', '}'])
            if token.type == ',':
                token = self._getToken()
            else:
                return

    def _loadIdsArr(self, callback):
        token = self._getToken()
        if token.type == '}':
            return  # states are empty
        while token.type != '':
            self._tShould(token, ['id'])
            callback(token.string)
            token = self._getToken()
            self._tShould(token, [',', '}'])
            if token.type == ',':
                token = self._getToken()
            else:
                return

    def _symbols(self, callback):
        """Load alphabet into grammar."""
        token = self._getToken()
        if token.type == '}':
            return  # states are empty
        while token.type != '':
            self._tShould(token, ['str', 'id'])
            callback(token.string)
            token = self._getToken()
            self._tShould(token, [',', '}'])
            if token.type == ',':
                token = self._getToken()
            else:
                return

    def _symbols2(self):
        """Load symbols in rule."""
        token = self._getToken()
        symbols = []
        if token.type == '}':
            return []   # states are empty
        while token.type != '':
            self._tShould(token, ['str', 'id'])
            symbols.append(token.string)
            token = self._getToken()
            self._tShould(token, [',', '}'])
            if token.type == ',':
                token = self._getToken()
            else:
                return symbols

    def _alphabet(self):
        """Load alphabet into automat."""
        token = self._getToken()
        if token.type == '}':
            return  # alphabet is empty
        while token.type != '':
            self._tShould(token, ['str'])
            self.aut.addAlpha(token.string)
            token = self._getToken()
            self._tShould(token, [',', '}'])
            if token.type == ',':
                token = self._getToken()
            else:
                return

    def _loadGrammarRules(self):
        token = self._getToken()
        if token.type == '}':
            return  # rules are empty

        while token.type != '':
            # expecting id of target state
            self._tShould(token, ['id'])
            nonterminal = token.string

            # expecting arrow
            token = self._getToken()
            self._tShould(token, ['->'])

            # expecting {
            token = self._getToken()
            self._tShould(token, ['{'])

            # load symbols in rule
            rightSide = self._symbols2()
            leftSide = nonterminal

            self.grammar.addRule(leftSide, rightSide)

            # expecting comma or closing bracket
            token = self._getToken()
            self._tShould(token, [',', '}'])
            if token.type == ',':
                token = self._getToken()
            else:
                return

    def _loadAutomatRules(self):
        token = self._getToken()
        if token.type == '}':
            return  # rules are empty

        while token.type != '':
            # expecting id of target state
            self._tShould(token, ['id'])
            state = token.string

            # expecting character
            token = self._getToken()
            self._tShould(token, ['str'])
            char = token.string

            # expecting arrow
            token = self._getToken()
            self._tShould(token, ['->'])

            # expecting id of target state
            token = self._getToken()
            self._tShould(token, ['id'])
            target = token.string

            self.aut.addRule(state, char, target)

            # expecting comma or closing bracket
            token = self._getToken()
            self._tShould(token, [',', '}'])
            if token.type == ',':
                token = self._getToken()
            else:
                return

    def _terminating(self):
        """Load all final states."""
        token = self._getToken()
        if token.type == '}':
            return
        while token.type != '':
            self._tShould(token, ['id'])
            self.aut.setTerminating(token.string)
            token = self._getToken()
            self._tShould(token, [',', '}'])
            if token.type == ',':
                token = self._getToken()
            else:
                return

    def _tShould(self, token, types):
        """
        Check if token is one of given types.

        if not, raise error
        """
        for ch in types:
            if ch == token.type:
                return
            if ch == 'char' and token.type == 'id' and len(token.string) == 1:
                return

        raise ValueError("Syntax error: unexpected token type: '" +
                         token.type +
                         "', expecting " + types.__str__(), 40)

    def _getToken(self):
        """Load next token."""
        ch = self._getChar()
        self._line = self._charLine
        state = 'begin'
        str = ''
        while ch is not False:
            # skip white chars
            if state == 'begin':
                if ch.isspace():
                    state = 'begin'
                elif ch == '#':
                    state = 'comment'
                elif ch == '-':
                    state = 'arrow'
                elif ch == "'":
                    state = 'string'
                elif ch == '{':
                    return Token('{', '')
                elif ch == '}':
                    return Token('}', '')
                elif ch == '(':
                    return Token('(', '')
                elif ch == ')':
                    return Token(')', '')
                elif ch == ',':
                    return Token(',', '')
                elif self._isIdBegin(ch):
                    str += ch
                    state = 'id'
                else:
                    raise ValueError("Unexpected character '" + ch, 40)

            # expecting second char of arrow (>)
            elif state == 'arrow':
                if ch == '>':
                    return Token('->', '')
                else:
                    raise ValueError("Unexpected character '" + ch, 40)

            # expecting string chars, breaked by apostrof
            elif state == 'string':
                if ch != "'":
                    str += ch
                else:
                    state = 'gotApostrof'

            # apostrof in the midle of the string
            elif state == 'gotApostrof':
                if ch != "'":
                    self._ungetChar()
                    return Token('str', str)
                else:
                    str += "'"
                    state = 'string'

            # expecting "c like" id
            elif state == 'id':
                if self._isIdInside(ch):
                    str += ch
                else:
                    self._ungetChar()
                    return Token('id', str)

            # comment
            elif state == 'comment':
                if ch == '\n':
                    state = 'begin'

            ch = self._getChar()

        # return empty token after reading whole file
        return Token('', '')

    def _ungetChar(self):
        """Unget one character."""
        if self.index > 0:
            self.index -= 1
            if self.str[self.index] == '\n':
                # line counter
                self._charLine -= 1
        else:
            raise ValueError("Nothing to unget", 40)

    def _getChar(self):
        """Load one character from input."""
        if self.index < len(self.str):
            ch = self.str[self.index]
            if ch == '\n':
                # line counter
                self._charLine += 1
            self.index += 1
            return ch
        else:
            return False

    def _isIdInside(self, ch):
        """Check inside character in c like id."""
        if ord('a') <= ord(ch) <= ord('z'):
            return True
        elif ord('A') <= ord(ch) <= ord('Z'):
            return True
        elif ord('0') <= ord(ch) <= ord('9'):
            return True
        elif ch == "_":
            return True
        else:
            return False

    def _isIdBegin(self, ch):
        """Check first character in c like id."""
        if ord('a') <= ord(ch) <= ord('z'):
            return True
        elif ord('A') <= ord(ch) <= ord('Z'):
            return True
        elif ch == "_":
            return True
        else:
            return False
