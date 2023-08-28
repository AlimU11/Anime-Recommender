import os
import pickle
import sys
import time
from datetime import datetime
from typing import Final

import requests
from loguru import logger

from . import IExtractor, query, stage_file


class APIExtractor(IExtractor):
    """IExtractor interface implementation.

    This class is responsible for extracting data from the API.

    Attributes
    ----------
    __url : str
        URL of the API.

    __API_PERIOD : int
        Period of time (in seconds) for which the `API_LIMIT` specified.

    __API_LIMIT : int
        Number of requests allowed within the `API_PERIOD` specified.

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

    __url: Final[str] = os.environ.get('API_URL')
    __API_PERIOD: Final[int] = int(os.environ.get('API_PERIOD'))
    __API_LIMIT: Final[int] = int(os.environ.get('API_LIMIT'))

    def __init__(self):
        self.__metadata_path: str = os.environ.get('METADATA_STAGED_PATH')
        self.__max_per_page: int = int(os.environ.get('MAX_PER_PAGE'))
        self.__data_path: str = os.environ.get('DATA_STAGED_PATH')
        self.__data: list[dict] = []

        if os.path.exists(self.__metadata_path):
            with open(self.__metadata_path, 'rb') as f:
                self.__metadata = pickle.load(f)
                self.__metadata['per_page'] = self.__max_per_page

        else:
            self.__metadata = {
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'pages': 0,
                'per_page': self.__max_per_page,
            }

        logger.info('APIExtractor initialized.')
        logger.info('\n' + self.__repr__())

    def __repr__(self):
        nl = '\n'
        return ''.join(
            [
                f'APIExtractor(\n',
                f'    url="{self.__url}",\n',
                f'    API_PERIOD={self.__API_PERIOD},\n',
                f'    API_LIMIT={self.__API_LIMIT},\n',
                f'    metadata_path="{self.__metadata_path}",\n',
                f'    max_per_page="{self.__max_per_page}",\n',
                f'    data_path="{self.__data_path}",\n',
                f'    data={self.__data},\n',
                f'''    metadata=({''.join([nl] + [
                    f'        {key}={value},{nl}' for key, value in self.__metadata.items()
                ])}    )\n''',
                f')',
            ],
        )

    def __str__(self):
        return self.__repr__()

    def extract_pipe(self):
        logger.info('Processing data...')

        self.__extract()
        self.__stage()

        logger.info('Done.')

    def __stage(self):
        """Stage data and metadata to files."""
        logger.info('Staging data...')

        stage_file(self.__data, self.__data_path)
        stage_file(self.__metadata, self.__metadata_path)

        logger.info('Done.')

    def __extract(self):
        """Extract data from AniList API."""
        logger.info('Extracting data...')

        page = 1
        has_next_page = True

        while has_next_page:
            logger.info(f'''Progress {page}/{self.__metadata['pages']} (estimated)''')

            response = self.__get_response(page)

            time.sleep(0.7)

            page_info, media = response.json()['data']['Page'].values()

            page += 1
            has_next_page = page_info['hasNextPage']
            self.__data += media

        self.__meta = {
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'pages': page,
            'per_page': self.__metadata['per_page'],
        }

        logger.info('Done.')

    def __get_response(self, page: int) -> requests.Response:
        """Get response from API.

        If status code is 429, wait for the specified time and try again.
        If status code is not 200 or 429, exit.

        Parameters
        ----------
        page : int
            Page number.

        Returns
        -------
        response : requests.Response
            Response from API.
        """
        response = requests.post(
            self.__url,
            json={
                'query': query,
                'variables': {
                    'page': page,
                    'perPage': self.__metadata['per_page'],
                },
            },
        )

        if response.status_code != 200:
            if response.status_code == 429:
                retry_after = int(response.headers['Retry-After'])
                logger.warning(f'Too many requests. Retry after {retry_after} seconds.')
                for i in range(retry_after):
                    logger.warning(f'Waiting {i+1} second(s)...')
                    time.sleep(1)

                return self.__get_response(page)

            else:
                logger.error(
                    f'Server does not returned status code 200. Unexpected status code {response.status_code} returned. Exiting...',
                )
                sys.exit(1)

        return response
