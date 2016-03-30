"""Debug print."""

# -- coding: utf-8 --
__author__ = 'stepan'


def debug_print(*positional_parameters, **keyword_parameters):
    """Print if debug mode is allowed."""
    Debug.print(*positional_parameters, **keyword_parameters)


class Debug:
    """Debug print static class."""
    allow = False

    @classmethod
    def setDebugMode(cls, allow):
        """Set debug mode."""
        cls.allow = allow

    @classmethod
    def print(cls, *positional_parameters, **keyword_parameters):
        """Print only if debug mode is set."""
        if cls.allow:
            print(*positional_parameters, **keyword_parameters)
