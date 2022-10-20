import numpy as np
from dateutil import parser
from pandas import DataFrame

from . import IProcessor


def to_time(s: str) -> int:
    """Convert a string duration to int time in seconds.

    Parameters
    ----------
    s : str
        A string to convert.

    Returns
    -------
    int
        A time in seconds.
    """
    l = s.split(',')

    time = 0

    for i in l:
        if 'mins' in i:
            time += int(i.replace('mins', '').strip())
        elif 'min' in i:
            time += int(i.replace('min', '').strip())
        elif 'hours' in i:
            time += int(i.replace('hours', '').strip()) * 60
        elif 'hour' in i:
            time += int(i.replace('hour', '').strip()) * 60
        else:
            print('unexpected duration passed to the function')
    return time


class Processor(DataFrame, IProcessor):
    """DataFrame Adapter for data processing."""

    def __process_dict_column(self):
        """Process dict columns in the DataFrame.

        Extract information from `data` column to separate columns. Fill columns containing lists with empty lists for
        missing values.
        """
        for key in [
            'format',
            'episodes',
            'status',
            'start_date',
            'end_date',
            'release_date',
            'season',
            'average_score',
            'mean_score',
            'popularity',
            'favorites',
            'source',
            'hashtag',
        ]:
            self[key] = self.data.apply(lambda x: x[key] if key in x.keys() else np.nan)

        for key in ['studios', 'producers', 'genres']:
            self[key] = self.data.apply(lambda x: x[key] if key in x.keys() else [])

        self['duration'] = self.data.apply(
            lambda x: x['episodeduration']
            if 'episodeduration' in x.keys()
            else x['duration']
            if 'duration' in x.keys()
            else np.nan,
        )

        self.title = self.title.str.replace('\n\t\t\t\t\t \n\t\t\t\t\t\tAdult', '')

        return self

    def __drop_columns(self):
        """Drop specified columns from the DataFrame."""
        self = self.drop(
            ['link', 'image_src', 'data', 'average_score', 'hashtag'],
            axis=1,
        )[self.status == 'finished']
        self = self.drop('status', axis=1)
        return self

    def drop_na(self):
        """Drop specified rows with missing values."""
        self = self.query(
            'format.notna() and episodes.notna() and mean_score.notna() and duration.notna()',
        )
        return self

    def __concat(self):
        """Concatenate information from mutually exclusive columns."""
        self.release_date = self.release_date.fillna('')
        self.start_date = self.start_date.fillna('')
        self.release_date = self.release_date + self.start_date
        self = self.drop('start_date', axis=1)
        return self

    def fill_na(self):
        """Fill missing values for specified columns in the DataFrame."""
        self.end_date = self.end_date.fillna(self.release_date)
        self.description = self.description.fillna('')
        self.favorites = self.favorites.fillna(0)
        self.source = self.source.fillna('unspecified')
        return self

    def __change_types(self):
        """Convert columns to specified types."""
        self.release_date = self.release_date.apply(lambda x: parser.parse(x))
        self.end_date = self.end_date.str.replace('undefined,', '').apply(
            lambda x: parser.parse(x),
        )
        self.episodes = self.episodes.astype(int)
        self.mean_score = self.mean_score.str.replace('%', '').astype(float)
        self.popularity = self.popularity.astype(int)
        self.favorites = self.favorites.astype(int)
        self.duration = self.duration.apply(to_time)

    def __convert_season(self):
        """Convert season column to int representation."""
        self.season = (self.release_date.dt.month - 1) // 3

    def process_pipe(self):
        self.__process_dict_column()
        self.__drop()
        self.dropna()
        self.concat()
        self.fill_na()
        self.changetypes()
        self.convert_season()
