from enum import Enum


class StrEnum(str, Enum):
    def __str__(self):
        return str(self.value)

    def _generate_next_value_(name, *_):
        return name
