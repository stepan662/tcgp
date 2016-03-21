"""LR Table operation."""

from enum import Enum

# -- coding: utf-8 --
__author__ = 'stepan'


class Operation(Enum):
    """LR operation type."""
    shift = 0
    reduce = 1
