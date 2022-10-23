import os
import pickle
from datetime import datetime
from typing import Final

import requests
from loguru import logger
from ratelimit import limits

from . import IExtractor, query, stage_file


class APIExtractor(IExtractor):
    """IExtractor interface implementation.

    This class is responsible for extracting data from the API.

    Attributes
    ----------
    __metadata_path : str
        Path to metadata file.

    __max_per_page : int
        Maximum number of items per extracted page.

    __data_path : str
        Path to data file.

    __data : list[dict]
        List of extracted data.

    __metadata : dict
        Dictionary with metadata. Used primarily to display estimated amount of pages, assuming that the number of items
        per page has not changed.
    """

    __url: Final[str] = 'https://graphql.anilist.co'
    __API_LIMIT: Final[int] = 60

    def __init__(self) -> None:
        self.__metadata_path: str = os.environ.get('METADATA_STAGED_PATH')
        self.__max_per_page: int = int(os.environ.get('MAX_PER_PAGE'))
        self.__data_path: str = os.environ.get('DATA_STAGED_PATH')
        self.__data: list[dict] = []

        if os.path.exists(self.__metadata_path):
            with open(self.__metadata_path, 'rb') as f:
                self.__metadata = pickle.load(f)

        else:
            self.__metadata = {
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'pages': 0,
                'per_page': self.__max_per_page,
            }

        logger.info('APIExtractor initialized.')
        logger.info(f'''Data path: {self.__data_path}''')
        logger.info(f'''Metadata path: {self.__metadata_path}''')
        logger.info('Metadata:')
        logger.info(f'''Last update: {self.__metadata['last_update']}''')
        logger.info(f'''Pages: {self.__metadata['pages']}''')
        logger.info(f'''Per page: {self.__metadata['per_page']}''')

    def extract_pipe(self) -> None:
        logger.info('Processing data...')

        self.__extract()
        self.__stage()

        logger.info('Done.')

    def __stage(self) -> None:
        """Stage data and metadata to files."""
        logger.info('Staging data...')

        stage_file(self.__data, self.__data_path)
        stage_file(self.__metadata, self.__metadata_path)

        logger.info('Done.')

    @limits(
        calls=90,
        period=__API_LIMIT,  # NOTE: Avoid rate limit https://anilist.gitbook.io/anilist-apiv2-docs/overview/rate-limiting
    )
    def __extract(self) -> None:
        """Extract data from AniList API."""
        logger.info('Extracting data...')

        page = 1
        has_next_page = True

        while has_next_page:
            logger.info(f'''Progress {page}/{self.__metadata['pages']} (estimated)''')

            page_info, media = (
                requests.post(
                    self.__url,
                    json={
                        'query': query,
                        'variables': {
                            'page': page,
                            'perPage': self.__metadata['per_page'],
                        },
                    },
                )
                .json()['data']['Page']
                .values()
            )

            page += 1
            has_next_page = page_info['hasNextPage']
            self.__data += media

        self.__meta = {
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'pages': page,
            'per_page': self.__metadata['per_page'],
        }

        logger.info('Done.')
