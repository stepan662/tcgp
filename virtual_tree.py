"""Virtual tree."""

# -- coding: utf-8 --
__author__ = 'stepan'


class VirtualTree:
    """Composing of virtual tree from original rules."""
    def __init__(self):
        """Initialization."""
        self.stack = []
        self.blocked = []
