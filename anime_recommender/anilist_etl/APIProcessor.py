import os
import pickle
from typing import Final

import pandas as pd
from loguru import logger
from pandas import DataFrame, RangeIndex, notna

from . import IProcessor, stage_file


class APIProcessor(DataFrame, IProcessor):
    """A processor for data retrieved from AniList API."""

    __quarter_dict: Final[dict] = {
        'WINTER': 1,
        'SPRING': 2,
        'SUMMER': 3,
        'FALL': 4,
        1: 1,
        2: 1,
        3: 1,
        4: 2,
        5: 2,
        6: 2,
        7: 3,
        8: 3,
        9: 3,
        10: 4,
        11: 4,
        12: 4,
    }

    __SEASON_UNDEFINED: Final[str] = 5
    __SOURCE_UNDEFINED: Final[str] = 'UNDEFINED'

    def __init__(self, inner=False, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        if not inner:
            self.__staged_path = os.environ.get('DATA_STAGED_PATH')
            self.__processed_path = os.environ.get('DATA_PROCESSED_PATH')

            logger.info('APIProcessor initialized.')
            logger.info(f'Loading data from "{self.__staged_path}"')
            logger.info(f'Staging processed data to "{self.__processed_path}"')

    @staticmethod
    def __fill_title(row):
        row.english = row.english if row.english else row.romaji
        row.native = row.native if row.native else row.romaji
        return row

    @staticmethod
    def __fill_season(row):
        row.season = (
            APIProcessor.__quarter_dict[row.season]
            if notna(row.season)
            else APIProcessor.__quarter_dict[row.startDate_month]
            if notna(row.startDate_month)
            else row.season
        )

        return row

    def __to_frame(self):
        """Convert nested dict to DataFrame."""
        logger.info('Converting data to DataFrame...')

        with open(self.__staged_path, 'rb') as f:
            data = pickle.load(f)

        self.__init__(
            inner=True,
            data=DataFrame(
                [
                    {
                        key: data[i][key]
                        for key in data[i]
                        if key
                        not in [
                            'title',
                            'coverImage',
                            'tags',
                            'startDate',
                            'endDate',
                            'studios',
                            'producers',
                        ]
                    }
                    | data[i]['title']
                    | data[i]['coverImage']
                    | {'tags': [(i['name'], i['rank']) for i in data[i]['tags']]}
                    | {'startDate_' + key: value for key, value in data[i]['startDate'].items()}
                    | {'endDate_' + key: value for key, value in data[i]['endDate'].items()}
                    | {
                        'studios': [
                            j['name']
                            for k, j in enumerate(data[i]['studios']['nodes'])
                            if data[i]['studios']['edges'][k]['isMain']
                        ],
                        'producers': [
                            j['name']
                            for k, j in enumerate(data[i]['studios']['nodes'])
                            if not data[i]['studios']['edges'][k]['isMain']
                        ],
                    }
                    for i in range(0, len(data))
                ],
            ),
        )

        logger.info('Done.')
        return self

    def __stage(self):
        """Stage processed data."""
        logger.info('Staging processed data...')

        stage_file(self, self.__processed_path)

        logger.info('Done.')
        return self

    def drop_na(self):
        """Drop specified rows with missing values."""
        logger.info('Dropping missing values...')

        self.query(
            '''format.notna() and status == 'FINISHED' and episodes.notna() and duration.notna() and startDate_year.notna()''',
            inplace=True,
        )

        logger.info('Done.')
        return self

    def fill_na(self):
        """Fill missing values for specified columns in the DataFrame."""
        logger.info('Filling missing values...')

        self.__init__(inner=True, data=self.apply(self.__fill_title, axis=1))
        self.__init__(inner=True, data=self.apply(self.__fill_season, axis=1))
        self['description'] = self.description.fillna('')
        self['source'] = self.source.fillna(self.__SOURCE_UNDEFINED)
        self['season'] = self.season.fillna(self.__SEASON_UNDEFINED)

        logger.info('Done.')
        return self

    def process_pipe(self):
        """Process DataFrame with all the methods in predefined order."""
        logger.info('Processing data...')

        self.__to_frame()
        self.drop_na()
        self.fill_na()

        self.index = RangeIndex(range(len(self)))
        self.__stage()

        logger.info('Done.')
        return self
