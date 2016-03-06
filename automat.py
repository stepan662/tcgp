"""Automat."""
import copy
import state

# -- coding: utf-8 --
__author__ = 'stepan'


class Automat:
    """Represents automat with all components."""

    def __init__(self):
        """Initialization."""
        self._states = {}
        self._alphabet = {}
        self._start = False

    def addAlpha(self, char):
        """Add character into alphabet."""
        self._alphabet[char] = True

    def addState(self, name):
        """Add state, without duplicites."""
        if name not in self._states:
            self._states[name] = state.State()

    def addRule(self, state, char, target):
        """
        Add rule.

        check if states exists and if chracter is in alphabet
        """
        try:
            st = self._states[state]
        except:
            raise ValueError("Undefined state '" + state + "'", 41)
        try:
            self._states[target]
        except:
            raise ValueError("Undefined state '" + target + "'", 41)

        if char == '':
            st.addRule(char, target)
        else:
            try:
                self._alphabet[char]
            except:
                raise ValueError("Undefined character '" + char + "'", 41)
            st.addRule(char, target)

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
                                 name + "'", 41)
        else:
            raise ValueError("Double setting start state", 41)

    def getStart(self):
        """"Get start state."""
        return self._start

    def setTerminating(self, name):
        """Set state as terminating, check if state exists."""
        try:
            state = self._states[name]
        except:
            raise ValueError("Undefined terminating state '" + name + "'", 41)

        state.setTerm(True)

    def getEClose(self, state):
        """Get e-closure of state."""
        # stack of e transitions, init with current state
        Q = {state: False}
        # stack of previous iteration
        Qbefore = copy.deepcopy(Q)
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
                Qbefore = copy.deepcopy(Q)
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
        aut._alphabet = copy.deepcopy(self._alphabet)
        aut._start = self._start
        aut.addState(self._start)

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

        return self.isTerm()

    def isTerm(self, state):
        """Indicate if state is terminating."""
        if self._states[state].isTerm():
            return True
        else:
            return False

    def applyCharToState(self, char, state):
        """Make one step with given char and state."""
        rules = self._states[state].getRules(char)
        if len(rules) == 1:
            return rules[0]
        else:
            if char in self._alphabet:
                raise ValueError("Character '" + char +
                                 "' can't be accepted in state '" +
                                 state + "'")
            else:
                raise ValueError("Character '" + char +
                                 "' is not acceptable", 1)

    def getAlphabet(self):
        """Get alphabet."""
        return self._alphabet

    def __str__(self):
        """Convert automat to standard string."""
        ret = '(\n'

        states = sorted(self._states.items(), key=lambda t: t[0])
        alphabet = sorted(self._alphabet.items(), key=lambda t: t[0])

        ret += "{"
        i = 0

        for st in states:
            if i != 0:
                ret += ", "
            ret += st[0]
            i += 1

        ret += "},\n{"
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

        ret += "},\n{"
        i = 0

        for st in states:
            keys = st[1].getAllRules()
            keys = sorted(keys.items(), key=lambda t: t[0])
            for key in keys:
                rules = sorted(key[1])
                for rule in rules:
                    if i != 0:
                        ret += ",\n"
                    else:
                        ret += "\n"

                    if key[0] == "'":
                        k = "''"
                    else:
                        k = key[0]

                    ret += st[0] + " '" + k + "' -> " + rule
                    i += 1

        ret += "\n},\n"
        ret += self._start + ",\n"

        ret += "{"
        i = 0
        for st in states:
            if st[1].isTerm():
                if i != 0:
                    ret += ", "
                ret += st[0]
                i += 1
        ret += "}\n"

        return ret + ")"
