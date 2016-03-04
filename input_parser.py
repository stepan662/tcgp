"""Parse grammar and finite state automat from file."""

# -- coding: utf-8 --
__author__ = 'stepan'


class InputParser:
    """Parser of input file."""

    def __init__(self, input):
        """Initialization."""
        self.arr = input.split()

    def getToken(self):
        """Finite state machine parser."""
        if len(self.arr) == 0:
            return ''
        else:
            return self.arr.pop(0)
