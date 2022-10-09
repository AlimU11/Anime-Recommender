from abc import ABCMeta, abstractmethod

from pandas import DataFrame


class IRecommender(metaclass=ABCMeta):
    """A recommender system interface."""

    @abstractmethod
    def recommend(self) -> DataFrame:
        """Calculate recommendations.

        Returns
        -------
        DataFrame
            DataFrame with titles and scores of recommendations.
        """

    @abstractmethod
    def get_data(self) -> None:
        """Return recommendation results."""
