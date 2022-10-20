from abc import ABCMeta, abstractmethod

from pandas import DataFrame


class IExtractor(metaclass=ABCMeta):
    """A data extractor interface."""

    @abstractmethod
    def extract_pipe(self) -> None:
        """Extract and stage data."""
