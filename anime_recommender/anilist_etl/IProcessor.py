from abc import ABCMeta, abstractmethod


class IProcessor(metaclass=ABCMeta):
    """A processor interface."""

    @abstractmethod
    def process_dict_column(self):
        """Process dict columns in the DataFrame."""

    @abstractmethod
    def drop_columns(self):
        """Drop specified columns from the DataFrame."""

    @abstractmethod
    def drop_na(self):
        """Drop specified rows with missing values."""

    @abstractmethod
    def concat(self):
        """Concatenate information from mutually exclusive columns."""

    @abstractmethod
    def fill_na(self):
        """Fill missing values for specified columns in the DataFrame."""

    @abstractmethod
    def change_types(self):
        """Convert columns to specified types."""

    @abstractmethod
    def convert_season(self):
        """Convert season column to int representation."""

    @abstractmethod
    def process_pipe(self):
        """Process DataFrame with all the methods in predefined order."""
