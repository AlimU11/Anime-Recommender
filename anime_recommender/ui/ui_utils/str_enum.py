"""
Extended Enumerations Module.

This module provides an enhanced version of Python's built-in Enum type,
allowing for direct string representations and automatic value generation based
on the enum member's name.

It's especially useful for situations where you want the name of the enum member
to be its value, and for these values to be used directly as strings.

Classes
-------
StrEnum : Enum
    A string-based Enum allowing direct string representations and automatic value generation.

Author
------
AlimU
"""


from enum import Enum


class StrEnum(str, Enum):  # noqa: WPS600
    """
    String representation of Python's built-in Enum.

    This class extends the functionality of the standard Enum by allowing
    direct string representations and value generation based on the enum member's name.

    Methods
    -------
    __str__() -> str:
        Returns the string representation of the enum member's value.
    _generate_next_value_(name: str, `*_`) -> str:
        Generates the next value for an enum member based on its name.

    Examples
    --------
    >>> class Colors(StrEnum):
    ...     RED = auto()
    ...     BLUE = auto()
    ...
    >>> print(Colors.RED)
    RED
    >>> Colors.RED.value
    'RED'
    """

    def __str__(self):
        """
        Return the string representation of the enum member's value.

        Returns
        -------
        str
            The string representation of the enum member's value.
        """
        return str(self.value)

    def _generate_next_value_(name, *_):  # noqa: WPS120, N805
        return name
