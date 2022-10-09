from abc import ABCMeta, abstractmethod

from pandas import DataFrame


class ITransformer(metaclass=ABCMeta):
    """ """

    @abstractmethod
    def transform_list(self, column: str, mode: str) -> DataFrame:
        """Transform list column  to dummy variables.


        Parameters
        ----------
        column : str
            Column name.

        mode : str
            'binary' or 'value'. If 'binary', the list will be transformed to dummy variables with 1 and 0. If 'value',
            assume that format is tuple of (str, str) and the second element is an element value.


        Returns
        -------
        DataFrame
            Transformed DataFrame.
        """

    @abstractmethod
    def transform_format(self) -> DataFrame:
        """Transform format column to origin column and format column. Assume that format value without specification
        is japanese. Otherwise, that origin value is specified in parentheses.

        Returns
        -------
        DataFrame
            Transformed DataFrame.
        """

    @abstractmethod
    def transform_categorical(self) -> DataFrame:
        """Transform to categorical and dummy variables.

        Returns
        -------
        DataFrame
            Transformed DataFrame.
        """

    @abstractmethod
    def transform_description(self) -> DataFrame:
        """Transform description column to vectorized representation.

        Returns
        -------
        DataFrame
            Transformed DataFrame.
        """

    @abstractmethod
    def transform_dates(self) -> DataFrame:
        """Transform date columns. The actual transformation is not yet specified.

        Returns
        -------
        DataFrame
            Transformed DataFrame.
        """

    @abstractmethod
    def transform_pipe(self) -> DataFrame:
        """Transform DataFrame with all the methods in predefined order.

        Returns
        -------
        DataFrame
            Transformed DataFrame.
        """
