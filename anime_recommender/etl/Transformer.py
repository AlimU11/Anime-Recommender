# OBSOLETE, USED FOR SCRAPING

import re

import numpy as np
import pandas as pd
from pandas import DataFrame, Series
from sklearn.preprocessing import MinMaxScaler

from . import ITransformer, TextProcessor


class Transformer(DataFrame, ITransformer):
    """DataFrame Adapter for data transformation."""

    def transform_list(self, column: str, mode: str) -> DataFrame:
        unique_set = self[column].apply(lambda x: [i[0] for i in x]).values if mode == 'value' else self[column].values
        unique_dict = {f'{column}_' + key: 0 for key in np.unique(np.hstack(unique_set))}

        key_matrix = DataFrame(
            self[column].apply(lambda x: self.__get_row(x, unique_dict.copy(), column, mode)).values.tolist(),
            dtype=np.uint8 if mode == 'binary' else np.float16,
        )

        self = pd.concat([self, key_matrix], axis=1)

        return self

    @staticmethod
    def __get_row(s: Series, info_dict: dict, column: str, mode: str) -> dict:
        if mode == 'value':
            for i in s:
                info_dict[f'{column}_' + i[0]] = int(i[1].replace('%', '')) / 100

        elif mode == 'binary':
            for i in s:
                info_dict[f'{column}_' + i] = 1

        return info_dict

    def transform_format(self) -> DataFrame:
        """Transform format column to origin column and format column. Assume that format value without specification
        is japanese. Otherwise, that origin value is specified in parentheses.

        Returns
        -------
        DataFrame
            Transformed DataFrame.
        """
        self['origin'] = self.format.apply(
            lambda x: re.search(r'\((.+)\)', x).group(1) if '(' in x else 'japanese',
        )
        self.format = self.format.apply(
            lambda x: re.search(r'(.+)\(', x).group(1) if '(' in x else x,
        )

        return self

    def transform_categorical(self) -> DataFrame:
        self.episodes = pd.cut(
            self.episodes,
            bins=[0, 1, 7, 13, 26, float('inf')],
            labels=['single', 'short', 'average', 'double_average', 'long'],
        )

        self = pd.get_dummies(
            self,
            columns=['is_adult', 'format', 'origin', 'episodes', 'season', 'source'],
            dtype=np.uint8,
        )

        return self

    def transform_description(self) -> DataFrame:
        """This method is not yet fully implemented. It is currently only cleaning the description column but not apply
        any NLP techniques."""
        self['description_cleaned'] = self.description.apply(
            lambda x: TextProcessor(x).text_pipe(),
        )
        return self

    def transform_scale(self) -> DataFrame:
        mm = MinMaxScaler()
        self.loc[:, 'duration':'favorites'] = mm.fit_transform(
            self.loc[:, 'duration':'favorites'],
        )

        return self

    def transform_dates(self) -> DataFrame:
        """This method is not yet implemented."""
        return self

    def drop_transformed(self) -> DataFrame:
        self = self.drop(
            ['tags', 'studios', 'producers', 'genres', 'status', 'description'],
            axis=1,
        )
        return self

    def transform_pipe(self) -> DataFrame:
        self = Transformer(self.transform_list('tags', 'value'))
        self = Transformer(self.transform_list('studios', 'binary'))
        self = Transformer(self.transform_list('producers', 'binary'))
        self = Transformer(self.transform_list('genres', 'binary'))
        self = Transformer(self.transform_format())
        self = Transformer(self.transform_categorical())
        self.transform_description()
        self.transform_scale()
        self.transform_dates()
        self = Transformer(self.drop_transformed())

        self['index'] = self['index'].astype(np.int32)

        return self
