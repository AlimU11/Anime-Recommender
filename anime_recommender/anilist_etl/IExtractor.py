from abc import ABCMeta, abstractmethod

from pandas import DataFrame


class IExtractor(metaclass=ABCMeta):
    """A data extractor interface."""

    @abstractmethod
    def extract(self) -> None:
        """Extract data."""
