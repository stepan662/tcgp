"""Grammar."""

from rule import Rule

# -- coding: utf-8 --
__author__ = 'stepan'


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
                             "'", 40)
        if name in self.terminals:
            raise ValueError("Symbol '" + name +
                             "' is already in terminals", 40)
        if name not in self.nonterminals:
            self.nonterminals.append(name)

    def addTerminal(self, name):
        """Add terminal symbol."""
        if name == '':
            raise ValueError("Invalid non-terminal symbol'" + name +
                             "'", 40)
        if name in self.nonterminals:
            raise ValueError("Symbol '" + name +
                             "' is already in non-terminals", 40)
        if name not in self.terminals:
            self.terminals.append(name)

    def addRule(self, leftSide, rightSide):
        """Add rule to symbol."""
        if self.isTerm(leftSide):
            # left side must be non-terminal
            raise ValueError("Left side of rule can't be terminal", 40)
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
                             "' can't be terminal.", 40)

    def isTerm(self, name):
        """Decide if symbol is terminal or not."""
        if name in self.terminals:
            return True
        elif name in self.nonterminals:
            return False
        else:
            raise ValueError("Symbol '" + name +
                             "' is not in grammar alphabet", 40)

    def __str__(self):
        """To string."""
        s = "(\n{"
        s += ", ".join([nonterm for nonterm in self.nonterminals])
        s += "},\n{"
        s += ", ".join([term for term in self.terminals])
        s += "},\n{\n"
        for rule in self.rules:
            s += str(rule) + "\n"
        s += "},\n"
        s += str(self.start) + "\n)\n"
        return s

#    def _getNewNontermName(self, name):
#        while name in self.nonterminals:
#            name += "*"
#        return name
#
#    def removeDeepLeftRecursion(self):
#        """Remove deep Left recursion."""
#        for nonTermIndex, nonterm in enumerate(self.nonterminals):
#            while True:
#                rulesRemove = set()
#                change = False
#                for rule in self.rules:
#                    if (nonterm != rule.leftSide or
#                            len(rule.rightSide) == 0 or
#                            self.isTerm(rule.rightSide[0]) or
#                            nonTermIndex <=
#                            self.nonterminals.index(rule.rightSide[0])):
#                        # skip no related rules epsilon rules
#                        # and rules with terminal first
#                        # and nonterminal after this one
#                        continue
#                    # recursive nonterminal
#                    rercursiveNonTerm = rule.rightSide[0]
#                    # get rest of the rule, without recursion
#                    nonRecursionPart = rule.rightSide[1:]
#                    change = True
#                    rulesRemove.add(rule)
#                    for rul in self.rules:
#                        if rul.leftSide == rercursiveNonTerm:
#                            # go through all rules with recursive nonterm
#                            # on left side
#                            newR = Rule(nonterm, rul.rightSide +
#                                        nonRecursionPart)
#                            newR.orig = rule.orig + rul.orig
#                            self.rules.append(newR)
#                for rule in rulesRemove:
#                    self.rules.remove(rule)
#
#                # remove direct recursion
#                if self.removeDirectLeftRecursion(nonterm):
#                    change = True
#
#                if change is False:
#                    break
#
#    def removeDirectLeftRecursion(self, nonterminal):
#        """Direct Left recursion remove algorithm."""
#        change = False
#        removeRules = set()
#
#        recursive = set()
#        nonrecursive = set()
#        remove = set()
#        for rule in self.rules:
#            if (rule.leftSide != nonterminal or
#                    len(rule.rightSide) == 0):
#                continue
#            # all rules with selected nonterminal on left side
#            if rule.rightSide[0] == rule.leftSide:
#                # direct recursive rule
#                if len(rule.rightSide) == 1:
#                    # remove R -> R rules
#                    removeRules.add(rule)
#                else:
#                    recursive.add(rule)
#            else:
#                nonrecursive.add(rule)
#            remove.add(rule)
#        if len(recursive) != 0:
#            # change grammar if there is recursive rule
#            newName = self._getNewNontermName(nonterminal + "*")
#            self.nonterminals.append(newName)
#            removeRules.update(remove)
#            emptyRule = Rule(newName, [])
#            emptyRule.orig = [OrigRules(Command.pop, [])]
#            self.rules.append(emptyRule)
#
#            for rule in nonrecursive:
#                newR = Rule(nonterminal, rule.rightSide + [newName])
#                newR.orig = rule.orig
#                for orig in newR.orig:
#                    orig.cmd = Command.push
#                # newR.orig.cmd = Command.push
#                self.rules.append(newR)
#
#            for rule in recursive:
#                newR = Rule(newName, rule.rightSide[1:] + [newName])
#                newR.orig = rule.orig
#                self.rules.append(newR)
#
#        for rule in removeRules:
#            change = True
#            self.rules.remove(rule)
#
#        return change
#
#    def leftFactorization(self):
#        """Left factorization algorithm."""
#        while True:
#            change = False
#            newNonTerms = set()
#            newRules = set()
#            removeRules = set()
#            for nonterminal in self.nonterminals:
#                rulesTable = {}
#                for rule in self.rules:
#                    if (rule.leftSide != nonterminal or
#                            len(rule.rightSide) == 0):
#                        continue
#                    # all rules with selected nonterminal on left side
#                    if rule.rightSide[0] not in rulesTable:
#                        rulesTable[rule.rightSide[0]] = [rule]
#                    else:
#                        rulesTable[rule.rightSide[0]].append(rule)
#
#                for firstTerm in rulesTable:
#                    rules = rulesTable[firstTerm]
#                    if len(rules) > 1:
#                        change = True
#                        # change grammar if there same first terminal
#                        # in two rules
#                        newName = self._getNewNontermName(nonterminal + "*")
#                        newNonTerms.add(newName)
#                        # add old rule with new non-terminal (A -> aA*)
#                        newR = Rule(nonterminal, [firstTerm, newName])
#                        newR.orig = [OrigRules(Command.apply, [])]
#                        newRules.add(newR)
#                        for rule in rules:
#                            # remove old rule
#                            removeRules.add(rule)
#
#                            # add new rule with new non-terminal and shorter
#                            newR = Rule(newName, rule.rightSide[1:])
#                            newR.orig = rule.orig
#                            newRules.add(newR)
#
#            for rule in removeRules:
#                self.rules.remove(rule)
#
#            for rule in newRules:
#                self.rules.append(rule)
#
#            for nonterm in newNonTerms:
#                self.nonterminals.append(nonterm)
#
#            if not change:
#                break
#
