import os
import pickle
from typing import Final

from loguru import logger
from pandas import DataFrame, RangeIndex, notna

from . import IProcessor, stage_file


class APIProcessor(DataFrame, IProcessor):
    """DataFrame Adapter for processing data retrieved from AniList API.

    Parameters
    ----------
    inner : bool
        If True, assumes reinitialization of APIProcessor within its method. In this case, will not log initialization
        info again and reinitialize `staged_path` and `processed_path` attributes with the same values.

    data : DataFrame
        Data to be passed to DataFrame constructor. Assumed that this parameter is passed only when reinitializing class,
        thus inner should be True.

    Attributes
    ----------
    __staged_path: str
        Path to the file with staged data. Assumed to be a result of the APIExtractor class.

    __processed_path: str
        Path to the file with processed data.
    """

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
    """Dictionary to convert Season feature (or month if season is missing) to corresponding quarter."""

    __SEASON_UNDEFINED: Final[str] = 5
    """Value to fill missing values in the source column."""

    __SOURCE_UNDEFINED: Final[str] = 'UNDEFINED'
    """Value to fill missing values in the season column."""

    def __init__(self, inner=False, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        if not inner:
            self.__staged_path = os.environ.get('DATA_STAGED_PATH')
            self.__processed_path = os.environ.get('DATA_PROCESSED_PATH')

            logger.info('APIProcessor initialized.')
            logger.info('\n' + self.__repr__())

    def __repr__(self):
        return ''.join(
            [
                f'APIProcessor(\n',
                f'  staged_path={self.__staged_path}\n',
                f'  processed_path={self.__processed_path}\n',
                f'{super().__repr__()}\n',
                f')',
            ],
        )

    def __str__(self):
        return self.__repr__()

    @staticmethod
    def __fill_title(row):
        """Fill missing values in the title column.
        Performs broadcast from romaji to english and native columns. Assumes that romaji title is always present.
        """
        row.english = row.english if row.english else row.romaji
        row.native = row.native if row.native else row.romaji
        return row

    @staticmethod
    def __fill_transform_season(row):
        """Fill missing values in the season column and transform it to corresponding quarter.

        If season is missing, will fill it with the corresponding month from the start date (if present) and convert
        month or season to the corresponding quarter using the `quarter_dict` dictionary. If both season and month are
        missing, will fill season with the `SEASON_UNDEFINED` value.
        """
        row.season = (
            APIProcessor.__quarter_dict[row.season]
            if notna(row.season)
            else APIProcessor.__quarter_dict[row.startDate_month]
            if notna(row.startDate_month)
            else APIProcessor.__SEASON_UNDEFINED
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
                    for i in range(len(data))
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
        logger.info('Dropping missing values...')

        # NOTE: Consider not to drop 'RELEASING' and 'NOT_YET_RELEASED' statuses in future updates.
        self.query(
            '''format.notna() and status == 'FINISHED' and episodes.notna() and duration.notna() and startDate_year.notna()''',
            inplace=True,
        )

        logger.info('Done.')
        return self

    def fill_na(self):
        logger.info('Filling missing values...')

        self.__init__(inner=True, data=self.apply(self.__fill_title, axis=1))
        self.__init__(inner=True, data=self.apply(self.__fill_transform_season, axis=1))
        self['description'] = self.description.fillna('')
        self['source'] = self.source.fillna(self.__SOURCE_UNDEFINED)

        logger.info('Done.')
        return self

    def process_pipe(self):
        logger.info('Processing data...')

        self.__to_frame()
        self.drop_na()
        self.fill_na()

        self.index = RangeIndex(range(len(self)))
        self.__stage()

        logger.info('Done.')
        return self
