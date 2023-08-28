"""Interface for recommender systems.

Provides a standardized interface for recommender systems.
"""

from abc import ABCMeta, abstractmethod

import numpy as np
from numpy.typing import NDArray

from anime_recommender.storage.IStorage import IStorage


class IVectorUtility(object, metaclass=ABCMeta):
    """Interface for utility class for calculating recommendation vector."""

    @abstractmethod
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

    @abstractmethod
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


class IRecommender(object, metaclass=ABCMeta):
    """A recommender system interface."""

    @abstractmethod
    def recommend(self) -> NDArray[np.float32]:
        """Generate recommendations based on the provided indexes and scores.

        Returns
        -------
        NDArray[np.float32]
            Array of recommended items. An empty array is returned if there are no indexes to consider.
        """
