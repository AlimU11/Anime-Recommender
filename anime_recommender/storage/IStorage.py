from abc import ABCMeta, abstractmethod
from typing import Optional

from pandas import DataFrame


class IStorage(metaclass=ABCMeta):
    """A storage interface."""

    @abstractmethod
    def map(self, indexes: list, inverse: Optional[bool] = False) -> list[int]:
        """Map external indexes to internal indexes and vice versa.

        Parameters
        ----------
        indexes : list
            List of indexes to map.

        inverse : bool, optional
            If True, map internal indexes to external indexes. Otherwise, map external indexes to internal ones.


        Returns
        -------
        list[int]
            List of mapped indexes.
        """

    @property
    @abstractmethod
    def data(self) -> DataFrame:
        """Unpacked data in form of pandas DataFrame. Unpacking method is determined by the file extension. Supported
        extensions are: `.csv`, `.gz`, `.pickle` (DataFrame, read-only)."""

    @property
    @abstractmethod
    def metadata(self) -> DataFrame:
        """Unpacked metadata in form of pandas DataFrame. Unpacking method is determined by the file extension. Supported
        extensions are: `.csv`, `.gz`, `.pickle`. (DataFrame)"""

    @property
    @abstractmethod
    def info(self) -> DataFrame:
        """Information about the data mart. Unpacking method is determined by the file extension. Supported extensions are:
        `.csv`, `.gz`, `.pickle` (DataFrame)."""
