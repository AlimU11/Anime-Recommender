import gzip
import pickle
from typing import Callable, Optional, final

import pandas as pd
from pandas import DataFrame

from anime_recommender.config import config
from anime_recommender.storage.IStorage import IStorage


@final
class LocalStorage(IStorage):
    """IStorage implementation aimed to serve as local storage for the data mart.

    Attributes
    ----------
    __data_path : str
        Path to the data mart file.

    __metadata_path : str
        Path to the metadata file containing information about data, such as attribute ownership (e.g. `genre` for
        `genre_Action` column, etc.) and column dtype.

    __data : DataFrame, read-only

    __metadata : DataFrame
        Unpacked metadata in form of pandas DataFrame. Unpacking method is determined by the file extension. Supported
        extensions are: `.csv`, `.gz`, `.pickle`.

    __mapping : dict[int, int]
        Mapping between the external and internal indexes with the external index as a key and internal index as a value.

    __mapping_inverse : dict[int, int]
        Mapping between the external and internal indexes with the internal index as a key and external index as a value.
    """

    @staticmethod
    def __from_csv(path: str) -> DataFrame:
        """Static method to read data from csv file.

        Parameters
        ----------
        path : str
            Path to the csv file.

        Returns
        -------
        DataFrame
            Data read from the csv file.
        """
        return pd.read_csv(path)

    @staticmethod
    def __from_gzip(path: str) -> DataFrame:
        """Static method to read data from gzipped pickle file containing DataFrame instance.

        Parameters
        ----------
        path : str
            Path to the gzipped pickle file containing DataFrame instance.

        Returns
        -------
        DataFrame
            Data read from the gzipped pickle file.
        """
        with gzip.open(path, 'rb') as f:
            return pickle.load(f)

    @staticmethod
    def __from_pickle(path: str) -> DataFrame:
        """Static method to read data from pickle file containing DataFrame instance.

        Parameters
        ----------
        path : str
            Path to the pickle file containing DataFrame instance.

        Returns
        -------
        DataFrame
            Data read from the pickle file.
        """
        with open(path, 'rb') as f:
            return pickle.load(f)

    __format: dict[str, Callable] = {
        'csv': __from_csv.__get__(object),
        'gz': __from_gzip.__get__(object),
        'pickle': __from_pickle.__get__(object),
    }
    """Functional dictionary to map file extension to the corresponding unpacking method."""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls is not LocalStorage:
            raise TypeError(f'{cls.__base__.__name__} class cannot be subclassed.')

    def __init__(self):
        self.__data: DataFrame = LocalStorage.__format[config.data_path.split('.')[-1]](config.data_path)
        self.__metadata: DataFrame = LocalStorage.__format[config.metadata_path.split('.')[-1]](config.metadata_path)
        self.__info: DataFrame = LocalStorage.__format[config.info_path.split('.')[-1]](config.info_path)
        self.__mapping: dict[int, int] = {
            key: value for value, key in self.__data.reset_index().iloc[:, :2].values.tolist()
        }
        self.__mapping_inverse: dict[int, int] = {key: value for value, key in self.__mapping.items()}

    def __repr__(self):
        return ''.join(
            [
                f'LocalStorage(\n',
                f'  DATA_SHAPE={self.__data.shape},\n',
                f'  METADATA_SHAPE={self.__metadata.shape})',
            ],
        )

    def map(self, indexes: list, inverse: Optional[bool] = False) -> list[int]:
        return (
            [self.__mapping_inverse[index] for index in indexes if index in self.__mapping_inverse.keys()]
            if inverse
            else [self.__mapping[index] for index in indexes if index in self.__mapping.keys()]
        )

    @property
    def data(self) -> DataFrame:
        return self.__data

    @property
    def metadata(self) -> DataFrame:
        return self.__metadata

    @property
    def info(self) -> DataFrame:
        return self.__info
