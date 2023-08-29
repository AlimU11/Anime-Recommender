from abc import ABCMeta, abstractmethod


class IExtractor(metaclass=ABCMeta):
    """A data extractor interface."""

    @abstractmethod
    def extract_pipe(self):
        """Extract and stage data."""
