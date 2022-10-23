from abc import ABCMeta, abstractmethod


class IProcessor(metaclass=ABCMeta):
    """A processor interface."""

    @abstractmethod
    def drop_na(self):
        """Drop specified rows with missing values."""

    @abstractmethod
    def fill_na(self):
        """Fill missing values for specified columns in the DataFrame."""

    @abstractmethod
    def process_pipe(self):
        """Process DataFrame with all the methods in predefined order."""
