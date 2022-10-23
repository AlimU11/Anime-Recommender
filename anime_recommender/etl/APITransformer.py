import os
import pickle
from typing import Final, Optional

import numpy as np
import pandas as pd
from loguru import logger
from pandas import DataFrame, RangeIndex, Series
from sklearn.preprocessing import MinMaxScaler

from . import ITransformer, TextProcessor, stage_file


class APITransformer(DataFrame, ITransformer):
    """DataFrame Adapter for data transformation.

    Attributes
    ----------
    __staged_path: str
        Path to the staged data file.

    __transformed_path: str
        Path to the transformed data file.

    __metadata_path: str
        Path to the metadata file.

    __info_path: str
        Path to the info file.

    __metadata: DataFrame
        Metadata of the transformed data. Contains the column names and their data types.

    __info: DataFrame
        Info of the transformed data. Contains information that is not used for creating recommendations, but needed to
        display the results.

    __META_CATEGORIES: Final[list[str]]

    Categories of transformed data columns. Used to build metadata information about the data. This is used to
    effectively select columns for the recommender system.

    Examples:
    ---------
    >>> df = data.iloc[:, metadata[metadata.column_name.isin(['tags', 'genres'])].index]
    >>> df
              tags_4-koma tags_Achromatic  ... genres_Supernatural genres_Thriller
        0             0.0            0.75  ...                   1               1
        1            0.35             0.0  ...                   0               0
        2            0.85             0.0  ...                   0               1
    """

    __META_CATEGORIES: Final[list[str]] = [
        'genres',
        'producers',
        'tags',
        'source',
        'studios',
        'format',
        'season',
        'episodes',
        'countryOfOrigin',
        'isAdult',
    ]

    def __init__(self, inner=False, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        if not inner:
            self.__staged_path: str = os.environ.get('DATA_PROCESSED_PATH')
            self.__transformed_path: str = os.environ.get('DATA_PATH')
            self.__metadata_path: str = os.environ.get('METADATA_PATH')
            self.__info_path: str = os.environ.get('INFO_PATH')

            self.__metadata: Optional[DataFrame] = None
            self.__info: Optional[DataFrame] = None

            with open(self.__staged_path, 'rb') as f:
                super().__init__(data=pickle.load(f), *args, **kwargs)

            logger.info('APITransformer initialized.')

    @staticmethod
    def __get_row(s: Series, info_dict: dict, column: str, mode: str) -> dict:
        if mode == 'value':
            for i in s:
                info_dict[f'{column}_' + i[0]] = i[1] / 100

        elif mode == 'binary':
            for i in s:
                info_dict[f'{column}_' + i] = 1

        return info_dict

    def __stage(self):
        """Stage the transformed data, metadata and info to files."""
        logger.info('Staging data...')

        self.__info = self[['id', 'description', 'romaji', 'english', 'native', 'large', 'color']]
        self.drop(['description', 'romaji', 'english', 'native', 'large', 'color'], axis=1, inplace=True)

        self.__metadata = self.dtypes.to_frame().reset_index().rename({'index': 'column_name', 0: 'dtype'}, axis=1)

        for column in APITransformer.__META_CATEGORIES:
            self.__metadata.loc[self.__metadata.column_name.str.startswith(column + '_'), 'column_name'] = column

        stage_file(self.__info, self.__info_path)
        stage_file(self.__metadata, self.__metadata_path)
        stage_file(DataFrame(self), self.__transformed_path)

        logger.info('Done.')

    def transform_list(self, column: str, mode: str) -> DataFrame:
        logger.info(f'Transforming {column} column...')

        unique_set = self[column].apply(lambda x: [i[0] for i in x]).values if mode == 'value' else self[column].values

        unique_dict = {f'{column}_' + key: 0 for key in np.unique(np.hstack(unique_set))}

        key_matrix = DataFrame(
            self[column].apply(lambda x: self.__get_row(x, unique_dict.copy(), column, mode)).values.tolist(),
            dtype=np.uint8 if mode == 'binary' else np.float16,
        )

        self.__init__(inner=True, data=pd.concat([self, key_matrix], axis=1))

        logger.info('Done.')
        return self

    def transform_categorical(self) -> DataFrame:
        logger.info('Transforming categorical columns...')

        self['episodes'] = pd.cut(
            self['episodes'],
            bins=[0, 1, 7, 13, 26, float('inf')],
            labels=['single', 'short', 'average', 'double_average', 'long'],
        )

        self.__init__(
            inner=True,
            data=pd.get_dummies(
                self,
                columns=[
                    'isAdult',
                    'format',
                    'countryOfOrigin',
                    'episodes',
                    'season',
                    'source',
                ],
                dtype=np.uint8,
            ),
        )

        logger.info('Done.')
        return self

    def transform_description(self) -> DataFrame:
        """This method is not yet fully implemented. It is currently only cleaning the description column but not apply
        any NLP techniques."""
        logger.info('Transforming description column...')

        self['description_cleaned'] = self.description.apply(
            lambda x: TextProcessor(x).text_pipe(),
        )

        logger.info('Done.')
        return self

    def transform_scale(self) -> DataFrame:
        """Scales the data to a range of 0 to 1.

        This scales continuous data to the same range as one-hot encoded data.
        """
        logger.info('Scaling numerical columns...')

        mm = MinMaxScaler()
        self.loc[:, 'duration':'favourites'] = mm.fit_transform(
            self.loc[:, 'duration':'favourites'],
        )

        logger.info('Done.')
        return self

    def transform_dates(self) -> DataFrame:
        """This method is not yet implemented."""
        return self

    def drop_transformed(self) -> DataFrame:
        """Drops all columns that not used for recommendations."""
        logger.info('Dropping transformed columns...')

        self.drop(
            [
                'tags',
                'studios',
                'producers',
                'genres',
                'status',
                'startDate_year',
                'startDate_month',
                'startDate_day',
                'endDate_year',
                'endDate_month',
                'endDate_day',
            ],
            axis=1,
            inplace=True,
        )

        logger.info('Done.')
        return self

    def transform_pipe(self) -> DataFrame:
        logger.info('Processing data...')

        self.transform_list('tags', 'value')
        self.transform_list('studios', 'binary')
        self.transform_list('producers', 'binary')
        self.transform_list('genres', 'binary')

        self.transform_categorical()

        # self.transform_description()
        # self.transform_dates()

        self.transform_scale()
        self.drop_transformed()
        self['id'] = self['id'].astype(np.int32)

        self.index = RangeIndex(range(len(self)))
        self.__stage()

        logger.info('Done.')
        return self
