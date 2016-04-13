"""Debug print."""

import sys

# -- coding: utf-8 --
__author__ = 'stepan'

err_messages = {
    '1': 'INPUT STRING NOT IN GRAMMAR',
    '2': 'NONDETERMINISTIC PROCESSING ERROR',
    '3': 'GRAMMAR PARSE ERROR',
    '4': 'LR TABLE ERROR',
    '5': 'FINITE AUTOMAT ERROR',
    '10': 'PROGRAM ARGUMENTS ERROR',
    '99': 'INTERNAL ERROR'
}


def err_print(exit_code, *args, **kwargs):
    """Print error message to stderr and exit with err_code."""
    if not sys.stdout.closed:
        sys.stdout.flush()
    if str(exit_code) in err_messages:
        sys.stderr.write(err_messages[str(exit_code)] + ": ")
    else:
        sys.stderr.write("UNDEFINED ERR " + str(exit_code) + " : ")
    print(*args, file=sys.stderr, **kwargs)
    sys.exit(exit_code)


def debug_print(category, *positional_parameters, **keyword_parameters):
    """Print if debug mode is allowed."""
    Debug.print(category, *positional_parameters, **keyword_parameters)


class Debug:
    """Debug print static class."""
    all = False
    categories = set()

    @classmethod
    def addCategory(cls, cat):
        """Add category."""
        cls.categories.add(cat)

    @classmethod
    def setDebugMode(cls, allow):
        """Set debug mode."""
        cls.all = allow

    @classmethod
    def isActivated(cls, category):
        """Determine if category is activated."""
        return cls.all or category in cls.categories

    @classmethod
    def print(cls, category, *positional_parameters, **keyword_parameters):
        """Print only if debug mode is set."""
        if cls.all or category in cls.categories:
            print(*positional_parameters, **keyword_parameters)
