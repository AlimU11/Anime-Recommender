from typing import Final, Optional, final

import requests
from multipledispatch import dispatch

from . import IClient, id_query, lists_query, media_query, query, variables


@final
class AnilistClient(IClient):
    """IClient interface implementation.

    Parameters
    ----------
    username : str
        Anilist user's username.
    """

    __url: Final[str] = 'https://graphql.anilist.co'

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls is not AnilistClient:
            raise TypeError(f'{cls.__base__.__name__} class cannot be subclassed.')

    def __init__(self):
        self._username: str | None = None
        self._user_id: int | None = None
        self._user_lists: dict | None = None
        self._unique_scores: list[tuple[int, int]] | None = None

    def __repr__(self):
        nl = '\n'
        return (
            f'Client(\n'
            f'  username={self._username},\n'
            f'  user_id={self._user_id},\n'
            f"""  user_lists={ f'{nl}'.join([f'({key}, {str(len(self._user_lists[key]))})' for key in self._user_lists.keys()]) })"""
        )

    def __str__(self):
        return self.__repr__()

    @property
    def request_url(self) -> str:
        """Anilist API URL (`str`, read-only)."""
        return AnilistClient.__url

    @property
    def username(self) -> str:
        """Anilist user's username (`str`, read-only)."""
        return self._username

    @username.setter
    def username(self, username: str):
        self._username = username
        self._user_id = self.get_user_id()
        self._user_lists = self.get_user_lists()
        self._unique_scores = (
            list(
                set(tuple(i) for j in self._user_lists.values() for i in j),
            )
            if self._user_id
            else None
        )

    @property
    def user_id(self) -> Optional[int]:
        """Anilist user's ID (`int`, optional, read-only)."""
        return self._user_id

    @property
    def user_lists(self) -> Optional[dict]:
        """Anilist user's lists (`dict`, optional, read-only)."""
        return self._user_lists

    @property
    def unique_scores(self) -> list[tuple[int, int]]:
        """Anilist user's unique scores (`list[tuple[int, int]]`, read-only)."""
        return self._unique_scores

    def indexes(self, user_lists: list[str]) -> list[int]:
        return [
            k[0]
            for k in self._unique_scores
            if k[0]
            in set(
                [i[0] for j in self._user_lists.keys() for i in self._user_lists[j] if j in user_lists],
            )
        ]

    def scores(self, user_lists: list[str]) -> list[int]:
        return [
            k[1]
            # else 0  # FIXME: values without scores have 0 score. Replace with appropriate values for missing ones
            #               or make this method private and introduce wrapper to check for missing scores
            #               (i.e. `scores()` + `__scores()`).
            for k in self._unique_scores
            if k[0]
            in set(
                [i[0] for j in self._user_lists.keys() for i in self._user_lists[j] if j in user_lists],
            )
        ]

    def get_user_id(self) -> Optional[str]:
        response = requests.post(
            AnilistClient.__url,
            json={'query': id_query, 'variables': {'name': self._username}},
        ).json()['data']['User']
        return response if response is None else response['id']

    def get_user_lists(self) -> Optional[dict]:
        if self._user_id is None:
            return None

        response = requests.post(
            AnilistClient.__url,
            json={'query': lists_query, 'variables': {'id': self._user_id}},
        ).json()['data']['MediaListCollection']['lists']

        if response is None:
            raise ValueError('User lists are empty.')

        return {i['name']: [[j['mediaId'], j['score']] for j in i['entries']] for i in response}

    @staticmethod
    @dispatch(int)
    def get_media_info(media_id: int) -> dict:
        """Get media info from Anilist API by media ID.

        Parameters
        ----------
        media_id : int
            Media ID to get info by.

        Returns
        -------
        dict
            Media info containing cover image, media color, description and title.
        """
        response = requests.post(
            AnilistClient.__url,
            json={'query': media_query, 'variables': {'id': media_id}},
        ).json()['data']['Media']

        if not response:
            return {}

        title = response['title']['english'] if response['title']['english'] else response['title']['romaji']

        return {
            'cover_image': response['coverImage']['large'],
            'color': response['coverImage']['color'],
            'description': response['description'],
            'title': title,
        }

    @staticmethod
    @dispatch(list)  # cannot be parametrized generic (list[int])
    def get_media_info(media_ids: list) -> list[dict]:
        """Get media info from Anilist API by list of media ID.

        Parameters
        ----------
        media_ids : list
            List of media IDs to get info by.

        Returns
        -------
        list[dict]
            List of media info. Each media contains cover image, media color, description and title.
        """

        response = requests.post(
            AnilistClient.__url,
            json={'query': query(media_ids), 'variables': variables(media_ids)},
        )

        return [
            {
                'cover_image': v['coverImage']['large'],
                'color': v['coverImage']['color'],
                'description': v['description'],
                'title': v['title']['english'] if v['title']['english'] else v['title']['romaji'],
            }
            for v in response.json()['data'].values()
        ]
