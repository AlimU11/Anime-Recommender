import os
from typing import Optional, final

import numpy as np
import pandas as pd
from loguru import logger
from pandas import DataFrame
from sklearn.metrics.pairwise import linear_kernel, rbf_kernel
from sklearn.preprocessing import minmax_scale

from anime_recommender.client import IClient

from ..storage import IStorage
from . import IRecommender


@final
class Recommender(IRecommender):
    """IRecommender interface implementation.

    Parameters
    ----------
    client : IClient
        IClient interface implementation.

    storage : IStorage
        IStorage interface implementation.

    similarity_method : str
        Similarity method.

    columns : list[str]
        List of features to use for similarity calculation.

    lists_include : list[str]
        List of user's lists to include in the calculation.

    lists_exclude : list[str]
        List of user's lists to exclude from the calculation.

    weighted : bool, optional
        Whether to use user's scores as weights, by default False.

    scaled : bool, optional
        Whether to use minmax scaling on user's scores, by default False.

    scale_range : list[float], optional
        Range to scale user's scores to, by default None.

    is_titles : bool, optional
        Whether to calculate similarity for individual titles instead of user's lists, by default False.

    titles : list[str], optional
        List of titles to calculate similarity for, by default None.

    language : str, optional
        Language of titles to calculate similarity for, by default 'english'.

    Attributes
    ----------
    __CHUNK_SIZE : np.uint16
        Number of titles to process at once. Defined in global_config.yaml.

    __indexes_include : np.ndarray
        Indexes of titles to include in the calculation. If `is_titles` is False, use user's lists to get indexes using
        client's `indexes` method and consequently remap them to internal indexes using storage's `map` method. If
        `is_titles` is True, use storage's `select_by_title` method to get internal indexes of titles straight away.

    __indexes_exclude : np.ndarray
        Indexes of titles to exclude from the calculation. If `is_titles` is False, use user's lists to get indexes
        using client's `indexes` method and consequently remap them to internal indexes using storage's `map` method. If
        `is_titles` is True, the attribute is an empty array.

    __scores : np.ndarray
        User's scores for titles to include in the calculation. If `weighted` is False or `is_titles` is True, the
        attribute is an array of ones. If `scaled` is True, additionally apply MinMax scaling on user's scores using
        `scale_range` as minimum and maximum values.

    __sum : np.uint32
        Sum of user's scores for titles to include in the calculation. If `weighted` is False or `is_titles` is True,
        the attribute is 1.

    __matrix : np.ndarray
        Matrix of features for all titles in the storage. Selected from storage with method `select` on premise that
        `columns` have at least one feature.

    __result_indexes : np.ndarray
        Array of indexes of all titles sort in recommendation order from most recommended to least recommended.
        Initially empty.
    """

    __similarity_method_dict = {
        'linear_kernel': linear_kernel,
        'rbf_kernel': rbf_kernel,
    }
    """Functional dictionary with kernel names as keys and respective functions as values."""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls is not Recommender:
            raise TypeError(f'{cls.__base__.__name__} class cannot be subclassed.')

    def __init__(
        self,
        client: IClient,
        storage: IStorage,
        similarity_method: str,
        columns: list[str],
        lists_include: list[str],
        lists_exclude: list[str],
        weighted: bool = False,
        scaled: bool = False,
        scale_range: list[float] = [1, 10],
        is_titles: bool = False,
        titles: Optional[list[str]] = None,
    ):
        self.__client: IClient = client
        self.__storage: IStorage = storage
        self.__similarity_method: str = similarity_method
        self.__columns: list[str] = columns
        self.__lists_include: list[str] = lists_include
        self.__lists_exclude: list[str] = lists_exclude
        self.__weighted: bool = weighted
        self.__scaled: bool = scaled
        self.__scale_range: np.float16 = np.float16(scale_range)
        self.__is_titles: bool = is_titles
        self.__titles: Optional[list[str]] = titles
        self.__CHUNK_SIZE: np.uint16 = np.uint16(os.environ['CHUNK_SIZE'])

        self.__indexes_include: np.ndarray = (
            np.array(
                self.__storage.map(self.__client.indexes(self.__lists_include)),
                dtype=np.uint32,
            )
            if not self.__is_titles
            else self.__storage.info[self.__storage.info.id.isin(self.__titles)].index.values
        )

        self.__indexes_exclude: np.ndarray = (
            np.array(
                self.__storage.map(self.__client.indexes(self.__lists_exclude)),
                dtype=np.uint32,
            )
            if not self.__is_titles
            else np.array([])
        )

        self.__scores: np.ndarray = (
            np.array(self.__client.scores(self.__lists_include), dtype=np.uint8).reshape(
                -1,
                1,
            )
            if self.__weighted and not self.__is_titles
            else np.ones(
                (len(self.__indexes_include), 1),
                dtype=np.uint8,
            )
        )

        self.__scores = (
            minmax_scale(self.__scores, feature_range=tuple(self.__scale_range))
            if self.__scaled and not self.__is_titles
            else self.__scores
        )

        self.__sum: np.uint32 = self.__scores.sum() if self.__weighted and not self.__is_titles else 1
        self.__matrix: np.ndarray = self.__storage.data.iloc[
            :,
            self.__storage.metadata[self.__storage.metadata.column_name.isin(self.__columns)].index,
        ].values
        self.__result_indexes: np.ndarray = np.empty((0,), dtype=np.uint32)

        # logger.debug(self)

    def __repr__(self):
        return ''.join(
            [
                f'Recommender(\n ',
                f'  similarity_method={self.__similarity_method},\n',
                f'  columns={self.__columns},\n',
                f'  lists_include={self.__lists_include},\n',
                f'  lists_exclude={self.__lists_exclude},\n',
                f'  weighted={self.__weighted},\n',
                f'  scaled={self.__scaled},\n',
                f'  scale_range={self.__scale_range},\n',
                f'  INDEXES_INCLUDE_SHAPE={self.__indexes_include.shape},\n',
                f'  INDEXES_EXCLUDE_SHAPE={self.__indexes_exclude.shape},\n',
                f'  SCORES_SHAPE={self.__scores.shape},\n',
                f'  SUM={self.__sum},\n',
                f'  MATRIX_SHAPE={self.__matrix.shape},\n',
                f'  CHUNK_SIZE={self.__CHUNK_SIZE},\n',
                f'  client={self.__client},\n',
                f'  storage={self.__storage})',
            ],
        )

    def __str__(self):
        return self.__repr__()

    def recommend(self) -> np.ndarray:
        return self.__chunk_calculate() if len(self.__indexes_include) else np.array([])

    def __calculate_vector(self, indexes: np.ndarray, scores: np.ndarray) -> np.ndarray:
        """Calculate vector of recommendations for given indexes and scores.

        Parameters
        ----------
        indexes : np.ndarray
            Indexes of titles to include in the calculation.

        scores : np.ndarray
            Scores of titles to include in the calculation.

        Returns
        -------
        ndarray
            Vector of recommendations.
        """
        return (
            (
                Recommender.__similarity_method_dict[self.__similarity_method](
                    self.__matrix[indexes],
                    self.__matrix,
                ).astype(np.float16)
                * scores
            ).sum(axis=0)
        ).T

    def __chunk_calculate(self):
        """Chunked calculation of recommendations vector.

        Returns
        -------
        ndarray
            ndarray with titles and scores of recommendations. Current implementation bounded to constant top 20
            recommendations.
        """
        result_vector = np.zeros((self.__matrix.shape[0],))
        n_iters = (
            int(np.round(self.__indexes_include.shape[0] / self.__CHUNK_SIZE))
            if self.__indexes_include.shape[0] >= self.__CHUNK_SIZE
            else 1
        )

        for i in range(1, n_iters + 1):
            indexes_chunk = self.__indexes_include[(i - 1) * self.__CHUNK_SIZE : i * self.__CHUNK_SIZE]
            scores_chunk = self.__scores[(i - 1) * self.__CHUNK_SIZE : i * self.__CHUNK_SIZE]
            result_vector += self.__calculate_vector(indexes_chunk, scores_chunk)

        result_vector = result_vector / self.__sum

        # same calculation without using chunks. Memory consumptive even with recasting to float16
        # res = (Recommender.__similarity_method_dict[self.__similarity_method](self.__matrix[self.__indexes], self.__matrix).astype(np.float16) * self.__scores).sum(axis=0) / self.__sum

        index_sorted = np.argsort(-result_vector)
        self.__result_indexes = index_sorted[
            ~np.isin(
                index_sorted,
                np.union1d(self.__indexes_include, self.__indexes_exclude),
            )
        ]
        self.__result_scores = minmax_scale(result_vector[self.__result_indexes])

        return np.hstack(
            [
                self.__storage.info.iloc[self.__result_indexes].id.values.reshape(
                    -1,
                    1,
                ),
                self.__result_scores.reshape(-1, 1),
            ],
        )

    def get_data(self) -> None:
        raise NotImplementedError('This method is not implemented')
