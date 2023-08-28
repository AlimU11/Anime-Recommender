"""Recommender module.

Provides the implementation of a recommender system for suggesting anime based on user preferences and features of
individual titles. The main component of this module is the `Recommender` class that computes recommendations based on
various similarity metrics, user lists, and anime features.
"""

from inspect import getattr_static
from typing import Callable, final

import numpy as np
from attr import dataclass
from numpy.typing import NDArray
from sklearn.metrics.pairwise import linear_kernel, rbf_kernel
from sklearn.preprocessing import minmax_scale

from anime_recommender.client import IClient
from anime_recommender.config import config
from anime_recommender.recommender.recommender_interface import IRecommender, IVectorUtility
from anime_recommender.storage import IStorage


class SimilarityMethod(object):
    """Similarity method class.

    Attributes
    ----------
    linear_kernel : Callable[[NDArray, NDArray], NDArray]
        Linear kernel function.

    rbf_kernel : Callable[[NDArray, NDArray], NDArray]
        Radial basis function kernel function.
    """

    linear_kernel = linear_kernel
    rbf_kernel = rbf_kernel

    def __init__(self, similarity_method: str):
        """Initialize the similarity method class with the given parameters.

        Parameters
        ----------
        similarity_method : str
            The similarity method to use for calculating the recommendation vector.
        """
        self._similarity_method = similarity_method

    @property
    def similarity_method(self) -> Callable:
        """Return the similarity method function.

        Returns
        -------
        Callable
            The similarity method function.
        """
        return getattr_static(self, self._similarity_method)

    def __repr__(self) -> str:
        """Return the string representation of the class.

        Returns
        -------
        str
            The string representation of the class.
        """
        repr_template = ''.join(
            [
                'SimilarityMethod(\n',
                '  similarity_method={similarity_method})',
            ],
        )

        return repr_template.format(
            similarity_method=self._similarity_method,
        )

    def __str__(self) -> str:
        """Return the string representation of the class.

        Returns
        -------
        str
            The string representation of the class.
        """
        return self.__repr__()


@dataclass
class RecommenderConfig(object):
    """Recommender configuration class.

    Attributes
    ----------
    columns : list[str]
        List of columns to include in the calculation.

    lists_include : list[str]
        List of user lists to include in the calculation.

    lists_exclude : list[str]
        List of user lists to exclude from the calculation.

    weighted : bool
        Whether to weight the user lists.

    scaled : bool
        Whether to scale the user lists.

    scale_range : tuple[float, float]
        The range to scale the user lists to.

    is_titles : bool
        Whether to include the titles in the calculation.

    titles : list[str], optional
        List of titles to include in the calculation.
    """

    columns: list[str]
    lists_include: list[str]
    lists_exclude: list[str]
    weighted: bool = False
    scaled: bool = False
    scale_range: tuple[float, float] = (1, 10)
    is_titles: bool = False
    titles: list[str] | None = None

    def __repr__(self) -> str:
        """Return the string representation of the class.

        Returns
        -------
        str
            The string representation of the class.
        """
        repr_template = ''.join(
            [
                'RecommenderConfig(\n',
                '  columns={columns}, \n',
                '  lists_include={lists_include},\n',
                '  lists_exclude={lists_exclude},\n',
                '  weighted={weighted},\n',
                '  scaled={scaled},\n',
                '  scale_range={scale_range},\n',
                '  is_titles={is_titles},\n',
                '  titles={titles})',
            ],
        )

        return repr_template.format(
            columns=self.columns,
            lists_include=self.lists_include,
            lists_exclude=self.lists_exclude,
            weighted=self.weighted,
            scaled=self.scaled,
            scale_range=self.scale_range,
            is_titles=self.is_titles,
            titles=self.titles,
        )

    def __str__(self) -> str:
        """Return the string representation of the class.

        Returns
        -------
        str
            The string representation of the class.
        """
        return self.__repr__()


class VectorUtility(IVectorUtility):  # noqa: WPS214
    """A utility class for calculating recommendation vector.

    Attributes
    ----------
    chunk_size : np.uint16
        The size of the chunks to process.

    matrix_size : int, default: 0
            The size of the matrix to process.

    result_vector : NDArray[np.float16]
        The result vector of the calculation.
    """

    def __init__(self, similarity_method: SimilarityMethod):
        """Initialize the utility class with the given parameters.

        Parameters
        ----------
        similarity_method : SimilarityMethod
            SimilarityMethod class that provides the similarity method function.
        """
        self._similarity_method: SimilarityMethod = similarity_method
        self._matrix_size: int = 0
        self._result_vector: NDArray[np.float16] = np.zeros((self._matrix_size,), dtype=np.float16)
        self._chunk_size: np.uint16 = np.uint16(config.chunk_size)

    def __repr__(self) -> str:
        """Return the string representation of the class.

        Returns
        -------
        str
            The string representation of the class.
        """
        repr_template = ''.join(
            [
                'VectorUtility(\n',
                '  similarity_method={similarity_method},\n',
                '  chunk_size={chunk_size})',
            ],
        )

        return repr_template.format(
            similarity_method=self._similarity_method,
            chunk_size=self._chunk_size,
        )

    def __str__(self) -> str:
        """Return the string representation of the class.

        Returns
        -------
        str
            The string representation of the class.
        """
        return self.__repr__()

    @property
    def matrix_size(self) -> int:
        """Return the size of the matrix to process.

        Returns
        -------
        int
            The size of the matrix to process.
        """
        return self._matrix_size

    @matrix_size.setter
    def matrix_size(self, matrix_size: int):
        self._matrix_size = matrix_size
        self._result_vector = np.zeros((matrix_size,), dtype=np.float16)

    def accumulate_chunked_results(
        self,
        indexes_include: NDArray[np.uint32],
        scores: NDArray[np.uint8],
        scores_sum: np.uint32,
        matrix: NDArray[np.float64],
    ):
        """Calculate the accumulated recommendation vector by processing chunks of indexes and scores.

        Parameters
        ----------
        indexes_include : NDArray[np.uint32]
            The indexes of the titles to include in the calculation.

        scores : NDArray[np.uint8]
            The scores of the titles to include in the calculation.

        scores_sum : np.uint32
            The sum of the scores of the titles to include in the calculation.

        matrix : NDArray[np.float64]
            The matrix of features.
        """
        num_iterations: int = max(
            int(np.round(indexes_include.shape[0] / self._chunk_size)),
            1,
        )

        for iteration_num in range(1, num_iterations + 1):
            indexes_chunk, scores_chunk = self._get_iteration_chunk(iteration_num, indexes_include, scores)
            self._result_vector += self._calculate_vector(indexes_chunk, scores_chunk, matrix)

        self._result_vector = (self._result_vector / scores_sum).astype(np.float16)

    def extract_sorted_recommendations(
        self,
        storage: IStorage,
        indexes_include: NDArray[np.uint32],
        indexes_exclude: NDArray[np.uint32],
    ) -> NDArray[np.float32]:
        """Extract the top sorted recommendations from the result vector.

        Parameters
        ----------
        storage : IStorage
            The storage instance to use for retrieving titles' information.

        indexes_include : NDArray[np.uint32]
            The indexes of the titles to include in the calculation.

        indexes_exclude : NDArray[np.uint32]
            The indexes of the titles to exclude from the calculation.

        Returns
        -------
        NDArray[np.float32]
            An array containing the top recommended items indexes and their scores.
        """
        index_sorted = np.argsort(-self._result_vector)
        combined_indexes = np.union1d(indexes_include, indexes_exclude)
        result_indexes = index_sorted[~np.isin(index_sorted, combined_indexes)]

        scaled_scores = minmax_scale(self._result_vector[result_indexes])
        scaled_scores = scaled_scores.reshape(-1, 1).astype(np.float32)

        item_ids = storage.info.iloc[result_indexes]
        item_ids = item_ids.id.values.reshape(-1, 1).astype(np.float32)

        return np.hstack([item_ids, scaled_scores])

    def _calculate_vector(
        self,
        indexes: NDArray[np.uint32],
        scores: NDArray[np.uint8],
        matrix: NDArray[np.float64],
    ) -> NDArray[np.float16]:
        """Calculate vector of recommendations for given indexes and scores.

        Parameters
        ----------
        indexes : NDArray[np.uint32]
            Indexes of titles to include in the calculation.

        scores : NDArray[np.uint8]
            Scores of titles to include in the calculation.

        matrix : NDArray[np.float64]
            The matrix of features.

        Returns
        -------
        NDArray[np.float16]
            Vector of recommendations.
        """
        similarity_method = self._similarity_method.similarity_method
        similarity_score = similarity_method(matrix[indexes], matrix).astype(np.float16) * scores

        return similarity_score.sum(axis=0).T

    def _get_iteration_chunk(
        self,
        iteration_num: int,
        indexes_include: NDArray[np.uint32],
        scores: NDArray[np.uint8],
    ) -> tuple[NDArray[np.uint32], NDArray[np.uint8]]:
        """Get the indexes and scores for a specific chunk iteration.

        Parameters
        ----------
        iteration_num : int
            The iteration number for which to retrieve the chunk data.

        indexes_include : NDArray[np.uint32]
            The indexes of the titles to include in the calculation.

        scores : NDArray[np.uint8]
            The scores of the titles to include in the calculation.

        Returns
        -------
        tuple[NDArray[np.uint32], NDArray[np.uint8]]
            The indexes and scores for the specified iteration.
        """
        range_start = (iteration_num - 1) * self._chunk_size
        range_end = iteration_num * self._chunk_size

        indexes_chunk = indexes_include[range_start:range_end]
        scores_chunk = scores[range_start:range_end]

        return indexes_chunk, scores_chunk


@final
class Recommender(IRecommender):
    """IRecommender interface implementation.

    Attributes
    ----------
    indexes_include : NDArray[np.uint32]
        Indexes of titles to include in the calculation. If `is_titles` is False, use user's lists to get indexes using
        client's `indexes` method and consequently remap them to internal indexes using storage's `map` method. If
        `is_titles` is True, use storage's `select_by_title` method to get internal indexes of titles straight away.

    indexes_exclude : NDArray[np.uint32]
        Indexes of titles to exclude from the calculation. If `is_titles` is False, use user's lists to get indexes
        using client's `indexes` method and consequently remap them to internal indexes using storage's `map` method. If
        `is_titles` is True, the attribute is an empty array.

    scores : NDArray[np.uint8]
        User's scores for titles to include in the calculation. If `weighted` is False or `is_titles` is True, the
        attribute is an array of ones. If `scaled` is True, additionally apply MinMax scaling on user's scores using
        `scale_range` as minimum and maximum values.

    scores_sum : np.uint32
        Sum of user's scores for titles to include in the calculation. If `weighted` is False or `is_titles` is True,
        the attribute is 1.

    matrix : NDArray[np.float64]
        Matrix of features for all titles in the storage. Selected from storage with method `select` on premise that
        `columns` have at least one feature.
    """

    def __init_subclass__(cls, **kwargs):
        """
        Ensure the Recommender class is not subclassed.

        Parameters
        ----------
        **kwargs : dict
            Arbitrary keyword arguments.

        Raises
        ------
        TypeError
            If there's an attempt to subclass the Recommender class.
        """
        super().__init_subclass__(**kwargs)
        if cls is not Recommender:
            raise TypeError('{name} class cannot be subclassed.'.format(name=cls.__base__.__name__))

    def __init__(
        self,
        client: IClient,
        storage: IStorage,
        recommender_config: RecommenderConfig,
        vector_utility: VectorUtility,
    ):
        """Initialize the Recommender with the given parameters.

        Parameters
        ----------
        client : IClient
            IClient interface implementation.

        storage : IStorage
            IStorage interface implementation.

        recommender_config : RecommenderConfig
            Recommender configuration class containing all other parameters from UI.

        vector_utility : VectorUtility
            VectorUtility class providing methods for calculating vector of recommendations.
        """
        self._client: IClient = client
        self._storage: IStorage = storage
        self._recommender_config: RecommenderConfig = recommender_config
        self._vector_utility: VectorUtility = vector_utility

        self._indexes_include: NDArray[np.uint32]
        self._indexes_exclude: NDArray[np.uint32]
        self._scores: NDArray[np.uint8]
        self._scores_sum: np.uint32
        self._matrix: NDArray[np.float64]

        if recommender_config.is_titles:
            storage_info = self._storage.info
            self._indexes_include = storage_info[storage_info.id.isin(recommender_config.titles)].index.values
        else:
            self._indexes_include = np.array(
                self._storage.map(self._client.indexes(recommender_config.lists_include)),
                dtype=np.uint32,
            )

        self._indexes_exclude = (
            np.array([])
            if recommender_config.is_titles
            else np.array(
                self._storage.map(self._client.indexes(recommender_config.lists_exclude)),
                dtype=np.uint32,
            )
        )

        if recommender_config.weighted and not recommender_config.is_titles:
            user_scores = self._client.scores(recommender_config.lists_include)
            user_scores = np.array(user_scores, dtype=np.uint8)
            self._scores = user_scores.reshape(-1, 1)
        else:
            self._scores = np.ones((len(self._indexes_include), 1), dtype=np.uint8)  # noqa: WPS221

        self._scores = (
            minmax_scale(self._scores, feature_range=recommender_config.scale_range)
            if recommender_config.scaled and not recommender_config.is_titles
            else self._scores
        )

        self._scores_sum = (
            self._scores.sum()
            if recommender_config.weighted and not recommender_config.is_titles
            else np.uint32(1)  # noqa: WPS221
        )

        storage_metadata = self._storage.metadata
        storage_data = self._storage.data
        metadata_indexes = storage_metadata[storage_metadata.column_name.isin(recommender_config.columns)].index
        self._matrix = storage_data.iloc[:, metadata_indexes].values
        self._vector_utility.matrix_size = self._matrix.shape[0]

    def __repr__(self) -> str:
        """Return a representation of the Recommender object.

        Returns
        -------
        str
            A representation of the Recommender object.
        """
        repr_template = ''.join(
            [
                'Recommender(\n',
                '  indexes_include_shape={indexes_include_shape},\n',
                '  indexes_exclude_shape={indexes_exclude_shape},\n',
                '  scores_shape={scores_shape},\n',
                '  scores_sum={scores_sum},\n',
                '  matrix_shape={matrix_shape},\n',
                '  client={client},\n',
                '  storage={storage},\n',
                '  recommender_config={recommender_config},\n',
                '  vector_utility={vector_utility})',
            ],
        )

        return repr_template.format(
            indexes_include_shape=self._indexes_include.shape,
            indexes_exclude_shape=self._indexes_exclude.shape,
            scores_shape=self._scores.shape,
            scores_sum=self._scores_sum,
            matrix_shape=self._matrix.shape,
            client=self._client,
            storage=self._storage,
            recommender_config=self._recommender_config,
            vector_utility=self._vector_utility,
        )

    def __str__(self) -> str:
        """Return a string representation of the Recommender object.

        Returns
        -------
        str
            A string representation of the Recommender object.
        """
        return self.__repr__()

    def recommend(self) -> NDArray[np.float32]:
        """Generate recommendations based on the provided indexes and scores.

        Returns
        -------
        NDArray[np.float32]
            Array of recommended items. An empty array is returned if there are no indexes to consider.
        """
        if self._indexes_include.shape[0]:
            self._vector_utility.accumulate_chunked_results(
                self._indexes_include,
                self._scores,
                self._scores_sum,
                self._matrix,
            )

            return self._vector_utility.extract_sorted_recommendations(
                self._storage,
                self._indexes_include,
                self._indexes_exclude,
            )

        return np.array([])
