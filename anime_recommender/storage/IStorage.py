from abc import ABCMeta, abstractmethod
from typing import Literal, Optional

from pandas import DataFrame


class IStorage(metaclass=ABCMeta):
    """A storage interface."""

    @abstractmethod
    def select(self, selected: list, sort_by: Optional[list[str]] = None, axis: Literal[0, 1] = 0) -> DataFrame:
        """Select columns from data. Use `metadata` to select columns by type (e.g. `genre` to select all genre columns).
         Optionally, sort the data by the specified columns.

        Parameters
        ----------
        selected : list
            List of objects to select.

        sort_by: list[str], optional
            List of columns to sort the data by.

        axis: Literal[0, 1], optional
            The axis to select along.

        Returns
        -------
        DataFrame
            Selected columns from the data, optionally sorted by the specified columns.
        """

    @abstractmethod
    def sort_by(self, columns: Optional[list[str]]) -> DataFrame:
        """Optional sorting of the data by the specified columns.

        Parameters
        ----------
        columns : list[str], optional
            List of columns to sort the data by.

        Returns
        -------
        DataFrame
            Data sorted by the specified columns.
        """

    @abstractmethod
    def map(self, indexes: list, reverse: Optional[bool] = False) -> list[int]:
        """Map external indexes to internal indexes and vice versa.

        Parameters
        ----------
        indexes : list
            List of indexes to map.

        reverse : bool, optional
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
