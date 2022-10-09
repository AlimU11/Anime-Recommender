from abc import ABCMeta, abstractmethod
from typing import Optional


class IClient(metaclass=ABCMeta):
    """A client interface."""

    @abstractmethod
    def indexes(self, user_lists: list[str]) -> list[int]:
        """Get set of indexes from chosen user lists.

        Parameters
        ----------
        user_lists : list[str]
            List of user lists to get indexes from.

        Returns
        -------
        list[int]
            Set of indexes from chosen user lists.
        """

    @abstractmethod
    def scores(self, user_lists: list[str]) -> list[int]:
        """Get set of scores from chosen user lists.

        Parameters
        ----------
        user_lists : list[str]
            List of user lists to get scores from.

        Returns
        -------
        list[int]
            Set of scores from chosen user lists.
        """

    @abstractmethod
    def get_user_id(self) -> Optional[str]:
        """Get Anilist user's ID."""

    @abstractmethod
    def get_user_lists(self) -> Optional[dict]:
        """Get Anilist user's lists."""

    @staticmethod
    @abstractmethod  # cannot have dispatch decorator for abstractmethod
    def get_media_info(media_id: int) -> dict:
        """Get media info from Anilist API by media ID.

        Parameters
        ----------
        media_id : int
            Media ID to get info by.

        Returns
        -------
        dict
            Media info.
        """

    @staticmethod
    @abstractmethod  # cannot have dispatch decorator for abstractmethod
    def get_media_info(media_ids: list) -> list[dict]:
        """Get media info from Anilist API by list of media ID.

        Parameters
        ----------
        media_ids : list
            List of media IDs to get info by.

        Returns
        -------
        list[dict]
            List of media info.
        """
