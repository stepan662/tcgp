"""Parse finite state automat from file."""
import automat


def parse(input):
    """Parse input and return automat."""
    return Parser(input).getAutomat()


class Token:
    """Object token."""
    def __init__(self, type, string):
        """Inicializace."""
        self.type = type
        self.string = string


class Parser:
    """Finite state machine parser."""
    def __init__(self, input):
        """Read and parse automat."""
        self.index = 0
        self.str = input
        self.line = 1

        # new empty automat
        self.aut = automat.Automat()

        # wait for opening brackets
        token = self._getToken()
        self._tShould(token, ['('])
        token = self._getToken()
        self._tShould(token, ['{'])

        # load states
        self._states()

        # comma and opening bracket
        token = self._getToken()
        self._tShould(token, [','])
        token = self._getToken()
        self._tShould(token, ['{'])

        # load alphabet
        self._alphabet()

        # comma and opening bracket
        token = self._getToken()
        self._tShould(token, [','])
        token = self._getToken()
        self._tShould(token, ['{'])

        # load rules
        self._rules()

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

    def getAutomat(self):
        """Return created automat."""
        return self.aut

    def _states(self):
        token = self._getToken()
        if token.type == '}':
            return  # states are empty
        while token.type != '':
            self._tShould(token, ['id'])
            self.aut.addState(token.string)
            token = self._getToken()
            self._tShould(token, [',', '}'])
            if token.type == ',':
                token = self._getToken()
            else:
                return

    def _alphabet(self):
        """Load alphebet into automat."""
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

    def _rules(self):
        """Load all rules into automat."""
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
        raise ValueError("Syntax error: unexpected token type: '" +
                         token.type +
                         "', expecting " + types.__str__() +
                         " on line " + self.line.__str__(), 40)

    def _getToken(self):
        """Load next token."""
        ch = self._getChar()
        state = 'begin'
        str = ''
        while ch is not False:

            # skip white chars
            if state == 'begin':
                if ch.isspace():
                    if ch == '\n':
                        # line counter
                        self.line += 1
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
                    raise ValueError("Unexpected character '" + ch +
                                     "' (line " + self.line.__str__() + ")",
                                     40)

            # expecting second char of arrow (>)
            elif state == 'arrow':
                if ch == '>':
                    return Token('->', '')
                else:
                    raise ValueError("Unexpected character '" + ch +
                                     "' (line " + self.line.__str__() + ")",
                                     40)

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
                if self._isIdBegin(ch) or (ord('0') <= ord(ch) <= ord('9')):
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
        else:
            raise ValueError("Nothing to unget", 40)

    def _getChar(self):
        """Load one character from input."""
        if self.index < len(self.str):
            ch = self.str[self.index]
            self.index += 1
            return ch
        else:
            return False

    def _isIdBegin(self, ch):
        """Check first character in c like id."""
        if ord('a') <= ord(ch) <= ord('z'):
            return True
        elif ord('A') <= ord(ch) <= ord('Z'):
            return True
        else:
            return False
