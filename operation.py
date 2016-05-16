"""LR Table operation."""

from enum import Enum

# -- coding: utf-8 --
__author__ = 'stepan'
__license__ = 'MIT'
__version__ = '1.0'


class Operation(Enum):
    """LR operation type."""
    shift = 0
    reduce = 1
