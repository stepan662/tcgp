"""Automat."""
from copy import deepcopy
from state import State

# -- coding: utf-8 --
__author__ = 'stepan'


class Automat:
    """Represents automat with all components."""

    def __init__(self):
        """Initialization."""
        self._states = {}
        self._alphabet = {}
        self._start = False
        self._dict = {}

    def addAlpha(self, char):
        """Add character into alphabet."""
        self._alphabet[char] = True

    def addState(self, name):
        """Add state, without duplicites."""
        if name not in self._states:
            self._states[name] = State()

    def addRule(self, state, char, target):
        """
        Add rule.

        check if states exists and if chracter is in alphabet
        """
        try:
            st = self._states[state]
        except:
            raise ValueError("Undefined state '" + state + "'", 5)
        try:
            self._states[target]
        except:
            raise ValueError("Undefined state '" + target + "'", 5)

        if char == '':
            st.addRule(char, target)
        else:
            try:
                self._alphabet[char]
            except:
                raise ValueError("Undefined character '" + char + "'", 5)
            st.addRule(char, target)

    def generateDict(self):
        """Generate dictionary for unknown start state."""
        self._dict = {}
        for symbol in self._alphabet:
            self._dict[symbol] = set()

        for stName in self._states:
            state = self._states[stName]
            for symbol in state._rules:
                newStates = state._rules[symbol]
                self._dict[symbol].update(newStates)

    def setStart(self, name):
        """
        Set start state.

        check, if is not already set
        """
        if not self._start:
            try:
                self._states[name]
                self._start = name
            except:
                raise ValueError("Setting start to undefined state'" +
                                 name + "'", 5)
        else:
            raise ValueError("Double setting start state", 5)

    def getStart(self):
        """"Get start state."""
        return self._start

    def setTerminating(self, name):
        """Set state as terminating, check if state exists."""
        try:
            state = self._states[name]
        except:
            raise ValueError("Undefined terminating state '" + name + "'", 5)

        state.setTerm(True)

    def getEClose(self, state):
        """Get e-closure of state."""
        # stack of e transitions, init with current state
        Q = {state: False}
        # stack of previous iteration
        Qbefore = deepcopy(Q)
        while True:
            # iterate over states from previous iteration
            for st in Qbefore:
                # transition wasn't explored yet
                if Q[st] is False:
                    for tran in self._states[st].getRules(''):
                        if tran not in Q:
                            # add new states to stack
                            # and mark them as unexplored
                            Q[tran] = False
                    # set actual state as explored
                    Q[st] = True

            # finish if there weren't any new states added
            if len(Qbefore) == len(Q):
                break
            else:
                Qbefore = deepcopy(Q)
        return Q

    def dropERules(self):
        """Drop all e rules."""
        for p in self._states:
            for eRule in self.getEClose(p):
                rTrans = self._states[eRule].getAllRules()
                self._states[p].addNonERules(rTrans)
                if self._states[eRule].isTerm():
                    self._states[p].setTerm(True)
            self._states[p].dropERules()
        return self

    def determinate(self):
        """
        Automat determinization.

        (e-rules must be dropped before)
        """
        Qnew = {}
        Qnew[self._start] = True
        aut = Automat()
        aut._alphabet = deepcopy(self._alphabet)
        aut._start = self._start
        aut.addState(self._start)
        if self.isTerm(self._start):
            aut.setTerminating(self._start)

        while True:
            # get first state from queue
            state, value = Qnew.popitem()
            origStates = state.split("_")
            origRules = {}
            for origState in origStates:
                # iterate through states, which is this composed from
                orgChars = self._states[origState].getAllRules()
                for char in orgChars:
                    if char not in origRules:
                        origRules[char] = []
                    for target in orgChars[char]:
                        # getting all rules from original states
                        if target not in origRules[char]:
                            origRules[char].append(target)

            for char in origRules:
                targets = origRules[char]
                # create new state name
                newState = '_'.join(sorted(targets))
                if newState not in aut._states:
                    # add new state to automat and to stack
                    # if it's not there
                    aut.addState(newState)
                    Qnew[newState] = True

                # add rule, which points to new state
                aut.addRule(state, char, newState)
                isTerm = False
                for target in targets:
                    if self._states[target].isTerm():
                        isTerm = True

                if isTerm:
                    # if any state was final then new is final also
                    aut.setTerminating(newState)

            if len(Qnew) == 0:
                # stack is empty, break from cycle
                break

        self._states = aut._states
        return self

    def analyzeString(self, string):
        """Analyze string with this automat."""
        state = self._start

        for char in string:
            rules = self._states[state].getRules(char)
            if len(rules) == 1:
                state = rules[0]
            else:
                if char in self._alphabet:
                    return False
                else:
                    raise ValueError("Character '" + char +
                                     "' is not acceptable", 1)

        return self.isTerm(state)

    def isTerm(self, state):
        """Indicate if state is terminating."""
        if isinstance(state, type(set())):
            # state is set of states - there is more possible states
            # lets try all of them
            for st in state:
                if self._states[st].isTerm():
                    return True
            return False
        if self._states[state].isTerm():
            return True
        else:
            return False

    def applyCharToState(self, char, state):
        """Make one step with given char and state."""
        if state is False:
            # we don't know in which state we are - take all possible
            return self._dict[char]
        elif isinstance(state, type(set())):
            # state is set of states - there is more possible states
            # lets try all of them
            newStates = set()
            for st in state:
                newState = self.applyCharToState(char, st)
                if newState is not False:
                    newStates.add(newState)
            if len(newStates) == 0:
                return False
            return newStates
        else:
            rules = self._states[state].getRules(char)
            if len(rules) == 1:
                return rules[0]
            else:
                return False

    def getAlphabet(self):
        """Get alphabet."""
        return self._alphabet

    def join(self, other):
        """Join two automats."""
        # copy symbols
        for symbol in other._alphabet:
            self.addAlpha(symbol)

        # copy states
        for state in other._states:
            self.addState(state)
            if other._states[state].isTerm():
                self.setTerminating(state)

        for state in other._states:
            symbolsRules = other._states[state].getAllRules()
            for symbol in symbolsRules:
                for state2 in symbolsRules[symbol]:
                    self.addRule(state, symbol, state2)

        # connect start states
        self.addRule(self._start, '', other._start)

    def __str__(self):
        """Convert automat to standard string."""
        ret = '(\n'

        states = sorted(self._states.items(), key=lambda t: t[0])
        alphabet = sorted(self._alphabet.items(), key=lambda t: t[0])

        ret += "  {"
        i = 0

        for st in states:
            if i != 0:
                ret += ", "
            ret += st[0]
            i += 1

        ret += "},\n  {"
        i = 0

        for char in alphabet:
            if i != 0:
                ret += ", "

            if char[0] == "'":
                ch = "''"
            else:
                ch = char[0]

            ret += "'" + ch + "'"
            i += 1

        ret += "},\n  {\n"
        i = 0

        for st in states:
            keys = st[1].getAllRules()
            keys = sorted(keys.items(), key=lambda t: t[0])
            for key in keys:
                rules = sorted(key[1])
                for rule in rules:
                    if key[0] == "'":
                        k = "\\'"
                    else:
                        k = key[0]

                    ret += "    " + st[0] + " '" + k + "' -> " + rule + ";\n"
                    i += 1

        ret += "  },\n  "
        ret += self._start + ",\n"

        ret += "  {"
        i = 0
        for st in states:
            if st[1].isTerm():
                if i != 0:
                    ret += ", "
                ret += st[0]
                i += 1
        ret += "}\n"

        return ret + ")"
