"""Parse tree controlled grammar from file."""

import automat
import grammar
from precedence_table import PrecedenceTable

# -- coding: utf-8 --
__author__ = 'stepan'


class Token:
    """Object token."""

    def __init__(self, type, string):
        """Initialization."""
        self.type = type
        self.string = string


class Parser:
    """Finite state machine parser."""

    def __init__(self):
        """Start parsing."""
        self.grammar = False
        self.aut = False
        self.prec = False
        self.automaton = False
        self.levels = False

    def getLine(self):
        """Get last token line."""
        return self._line

    def getPos(self):
        """Get last token position."""
        if self._pos == 0:
            return 1
        return self._pos

    def parse(self, input):
        """Read and parse automat."""
        self.index = 0
        self.str = input
        self._line = 1
        self._pos = 0
        self._charLine = 1
        self._charPos = 0

        while True:
            # wait for keyword
            token = self._getToken()
            self._tShould(token, ['id', ''])
            keyword = token.string

            if token.type == '':
                break

            token = self._getToken()
            self._tShould(token, ['='])
            if keyword == 'grammar':
                if self.grammar is not False:
                    raise ValueError("Grammar is defined twice in this file.",
                                     3)

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
                self._loadCharArr(self.grammar.addTerminal)

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

            elif keyword == 'automaton':
                if self.grammar is False:
                    raise ValueError("Automaton must " +
                                     " be defined after grammar.", 3)
                if self.automaton is not False:
                    raise ValueError("Automaton is defined twice.", 3)
                self.automaton = True

                # new empty automat
                aut = automat.Automat()

                # automat alphabet are terminals and nonterminals from grammar
                for symbol in self.grammar.nonterminals:
                    aut.addAlpha(symbol)
                for symbol in self.grammar.terminals:
                    aut.addAlpha(symbol)

                # wait for opening brackets
                token = self._getToken()
                self._tShould(token, ['('])
                token = self._getToken()
                self._tShould(token, ['{'])

                # load states
                self._loadIdsArr(aut.addState)

                # comma and opening bracket
                token = self._getToken()
                self._tShould(token, [','])
                token = self._getToken()
                self._tShould(token, ['{'])

                # load rules
                self._loadAutomatRules(aut)

                # comma and start state
                token = self._getToken()
                self._tShould(token, [','])
                token = self._getToken()
                if token.type != 'id':
                    raise ValueError("Missing automat start state", 3)
                else:
                    aut.setStart(token.string)

                # comma and opening bracket
                token = self._getToken()
                self._tShould(token, [','])
                token = self._getToken()
                self._tShould(token, ['{'])

                self._loadIdsArr(aut.setTerminating)

                # closing bracket and nothing
                token = self._getToken()
                self._tShould(token, [')'])
                if not self.aut:
                    self.aut = aut
                else:
                    aut.join(self.aut)
                    self.aut = aut
            elif keyword == 'precedence':
                if self.grammar is False:
                    raise ValueError("Precedence must be defined after" +
                                     " grammar.", 3)
                if self.prec is not False:
                    raise ValueError("Precedence is defined twice.", 3)

                self.prec = PrecedenceTable()
                token = self._getToken()
                self._tShould(token, ['('])
                while self.loadPrecedenceRules():
                    pass

            elif keyword == 'levels':
                if self.grammar is False:
                    raise ValueError("Levels must be defined after" +
                                     " grammar.", 3)
                if self.levels is not False:
                    raise ValueError("Levels are defined twice.", 3)
                self.levels = True

                token = self._getToken()
                self._tShould(token, ['{'])

                aut = automat.Automat()

                # automat alphabet are terminals and nonterminals from grammar
                for symbol in self.grammar.nonterminals:
                    aut.addAlpha(symbol)
                for symbol in self.grammar.terminals:
                    aut.addAlpha(symbol)

                start = '0'
                aut.addState(start)
                aut.setStart(start)
                stringNum = 0
                charNum = 0
                while True:
                    lastState = start
                    token = self._getToken()
                    self._tShould(token, ['}', ';', 'str'])
                    if token.type == '}':
                        break
                    else:
                        while True:
                            if token.type == ';':
                                aut.setTerminating(lastState)
                                break

                            newState = str(stringNum) + "-" + str(charNum)
                            aut.addState(newState)
                            aut.addRule(lastState, token.string, newState)
                            lastState = newState

                            token = self._getToken()
                            self._tShould(token, ['str', ';'])

                            charNum += 1
                    stringNum += 1
                if not self.aut:
                    self.aut = aut
                else:
                    self.aut.join(aut)

            else:
                raise ValueError("Undefined keyword '" + keyword + "'", 3)
        if self.grammar is False:
            raise ValueError("No grammar specified in grammar input file.", 3)

    def getGrammar(self):
        """Return created grammar."""
        return self.grammar

    def getAutomat(self):
        """Return created automat."""
        return self.aut

    def getPrecedence(self):
        """Return created precedence."""
        return self.prec

    def _loadCharArr(self, callback):
        token = self._getToken()
        if token.type == '}':
            return  # states are empty
        while token.type != '':
            self._tShould(token, ['str'])
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

    def grammarRuleBody(self):
        """Load symbols in rule."""
        token = self._getToken()
        symbols = []
        if token.type == '}':
            return []
        while token.type != '':
            self._tShould(token, ['str', 'id', ';'])
            if token.type == 'str':
                if not self.grammar.isTerm(token.string):
                    raise ValueError("Nonterminal '" + token.string +
                                     "' musn't be bounded by ''", 3)
                symbols.append(token.string)
                token = self._getToken()
            elif token.type == 'id':
                if self.grammar.isTerm(token.string):
                    raise ValueError("Terminal '" + token.string +
                                     "' must be bounded by ''", 3)
                self.grammar.isTerm(token.string)
                symbols.append(token.string)
                token = self._getToken()
            else:
                return symbols

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

            # load symbols in rule
            rightSide = self.grammarRuleBody()
            leftSide = nonterminal

            self.grammar.addRule(leftSide, rightSide)

            # expecting comma or closing bracket
            token = self._getToken()
            self._tShould(token, ['id', '}'])
            if token.type != 'id':
                return

    def _loadAutomatRules(self, aut):
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

            aut.addRule(state, char, target)

            # expecting comma or closing bracket
            token = self._getToken()
            self._tShould(token, [';'])

            token = self._getToken()
            self._tShould(token, ['id', '}'])
            if token.type != 'id':
                return

    def loadPrecedenceRules(self):
        """Load precedence rules."""
        token = self._getToken()
        self._tShould(token, ['id', ')'])

        if token.type == ')':
            return False

        leftSide = token.string
        rightSide = []

        token = self._getToken()
        self._tShould(token, [':'])

        while True:
            token = self._getToken()
            self._tShould(token, ['str', 'id', '$'])
            if token.type == 'str':
                if not self.grammar.isTerm(token.string):
                    raise ValueError("Nonterminal '" + token.string +
                                     "' musn't be bounded by ''", 3)
            elif token.type == 'id':
                if self.grammar.isTerm(token.string):
                    raise ValueError("Terminal '" + token.string +
                                     "' must be bounded by ''", 3)
            rightSide.append(token.string)

            token = self._getToken()
            self._tShould(token, [',', ';'])
            if token.type == ';':
                break
        self.prec.addPrecedence(leftSide, rightSide)
        return True

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
        tokStr = "token type '" + token.type + "'"
        if token.type == '':
            tokStr = 'end of file'
        raise ValueError("Unexpected " + tokStr +
                         ", expecting one of " + types.__str__(), 3)

    def _getToken(self):
        """Load next token."""
        ch = self._getChar()
        self._line = self._charLine
        self._pos = self._charPos
        state = 'begin'
        str = ''
        while ch is not False:
            # skip white chars
            if state == 'begin':
                self._line = self._charLine
                self._pos = self._charPos
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
                elif ch == '$':
                    return Token('$', '')
                elif ch == '}':
                    return Token('}', '')
                elif ch == ';':
                    return Token(';', '')
                elif ch == ':':
                    return Token(':', '')
                elif ch == '=':
                    return Token('=', '')
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
                    raise ValueError("Unexpected character '" + ch + "'", 3)

            # expecting second char of arrow (>)
            elif state == 'arrow':
                if ch == '>':
                    return Token('->', '')
                else:
                    raise ValueError("Unexpected character '" + ch + "'", 3)

            # expecting string chars, breaked by apostrof
            elif state == 'string':
                if ch != "'":
                    str += ch
                else:
                    state = 'gotApostrof'

            # apostrof in the midle of the string
            elif state == 'gotApostrof':
                if ch not in ("'", "\\"):
                    self._ungetChar()
                    return Token('str', str)
                else:
                    str += ch
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
