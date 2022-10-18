import json
import os
import time
from datetime import datetime
from typing import Final

import requests
from loguru import logger

from . import IExtractor, query


class AnilistExtractor(IExtractor):
    """A data extractor class."""

    __url: Final[str] = 'https://graphql.anilist.co'

    def __init__(self) -> None:
        self.__meta_path: str = os.environ.get('METADATA_STAGED_PATH')
        self.__max_per_page: int = int(os.environ.get('MAX_PER_PAGE'))
        self.__data_staged_path: str = os.environ.get('DATA_STAGED_PATH')
        self.__data: list[dict] = []

        if os.path.exists(self.__meta_path):
            with open(self.__meta_path, 'r') as f:
                self.__metadata = json.load(f)

        else:
            self.__metadata = {
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'pages': 0,
                'per_page': self.__max_per_page,
            }

    def extract(self) -> None:
        """Extract data."""
        self.__extract()
        self.__stage()

    def __stage(self) -> None:
        logger.info('Staging data...')

        if os.path.exists(self.__meta_path + '_old'):
            os.remove(self.__data_staged_path + '_old')

        if os.path.exists(self.__meta_path):
            os.rename(self.__meta_path, self.__meta_path + '_old')

        if os.path.exists(self.__data_staged_path):
            if os.path.exists(self.__data_staged_path + '_old'):
                os.remove(self.__data_staged_path + '_old')

            os.rename(self.__data_staged_path, self.__data_staged_path + '_old')

        with open(self.__data_staged_path, 'w') as f:
            json.dump(self.__data, f)

        with open(self.__meta_path, 'w') as f:
            json.dump(self.__meta, f)

        logger.info('Done.')

    def __extract(self) -> None:
        logger.info('Extracting data...')

        page = 1
        has_next_page = True

        while has_next_page:
            logger.info(f'''Progress {page}/{self.__metadata['pages']} (last iteration)''')

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

            time.sleep(1)  # NOTE: Avoid rate limit

        self.__meta = {
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'pages': page,
            'per_page': self.__metadata['per_page'],
        }
