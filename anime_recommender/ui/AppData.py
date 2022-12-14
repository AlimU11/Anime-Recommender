from typing import Optional, Type

from pandas import DataFrame

from ..client import IClient
from ..etl import ITextProcessor, TextProcessor
from ..recommender import IRecommender
from ..storage import IStorage


class AppData:
    """Web App data holder class.

    Note
    ----
    Since it is not possible to pass class instances to dash callbacks, there are four options to resolve this:
    1. use global variables
    2. use singleton pattern
    3. save and load classes to file (not possible or difficult to implement for a small web app with possible
    concurrent users)
    4. use holder class

    Thus, the holder class was considered the best option in this case.

    Attributes
    ----------
    __client : IClient, optional

    __storage : IStorage, optional

    __recommender : IRecommender, optional

    __similarity_method : str, optional

    __columns : list[str]

    __included_lists : list[str]

    __excluded_lists : list[str]

    __is_weighted : bool

    __scaled : bool

    __scale_range : list[float]

    __type_switch : bool

    __input_values : list[str]

    __df : DataFrame

    __text_processor : Type[ITextProcessor]
    """

    def __init__(self):
        self.__client: Optional[IClient] = None
        self.__storage: Optional[IStorage] = None
        self.__recommender: Optional[IRecommender] = None
        self.__recommender_type: Optional[str] = None
        self.__columns: list[str] = []
        self.__included_lists: list[str] = []
        self.__excluded_lists: list[str] = []
        self.__is_weighted: bool = False
        self.__scaled: bool = False
        self.__scale_range: list[float] = []
        self.__type_switch: bool = False
        self.__input_values: list[str] = []
        self.__language: str = 'english'
        self.__df: Optional[DataFrame] = None
        self.__text_processor: Type[ITextProcessor] = TextProcessor

    @property
    def client(self) -> Optional[IClient]:
        """IClient interface implementation (`IClient`, optional)."""
        return self.__client

    @client.setter
    def client(self, client: IClient):
        self.__client = client

    @property
    def storage(self) -> Optional[IStorage]:
        """IStorage interface implementation (`IStorage`, optional)."""
        return self.__storage

    @storage.setter
    def storage(self, storage: IStorage):
        self.__storage = storage

    @property
    def recommender(self) -> Optional[IRecommender]:
        """IRecommender interface implementation (`IRecommender`, optional)."""
        return self.__recommender

    @recommender.setter
    def recommender(self, recommender: IRecommender):
        self.__recommender = recommender

    @property
    def recommender_type(self) -> Optional[str]:
        """Similarity method used by recommender. Stores last chosen similarity method (`str`, optional)."""
        return self.__recommender_type

    @recommender_type.setter
    def recommender_type(self, similarity_method: str):
        self.__recommender_type = similarity_method

    @property
    def columns(self) -> list[str]:
        """List of columns used by recommender. Stores last chosen columns (`list[str]`)."""
        return self.__columns

    @columns.setter
    def columns(self, columns: list[str]):
        self.__columns = columns

    @property
    def included_lists(self) -> list[str]:
        """List of included lists of user used by recommender. Stores last chosen included lists (`list[str]`)."""
        return self.__included_lists

    @included_lists.setter
    def included_lists(self, included_lists: list[str]):
        self.__included_lists = included_lists

    @property
    def excluded_lists(self) -> list[str]:
        """List of excluded lists of user used by recommender. Stores last chosen excluded lists (`list[str]`)."""
        return self.__excluded_lists

    @excluded_lists.setter
    def excluded_lists(self, excluded_lists: list[str]):
        self.__excluded_lists = excluded_lists

    @property
    def is_weighted(self) -> bool:
        """Weighted flag used by recommender. Stores last chosen weighted flag (`bool`)."""
        return self.__is_weighted

    @is_weighted.setter
    def is_weighted(self, weighted: bool):
        self.__is_weighted = weighted

    @property
    def scaled(self) -> bool:
        """Scaled flag used by recommender. Stores last chosen scaled flag (`bool`)."""
        return self.__scaled

    @scaled.setter
    def scaled(self, scaled: bool):
        self.__scaled = scaled

    @property
    def scale_range(self) -> list[float]:
        """Scale range used by recommender. Stores last chosen scale range (`list[float]`)."""
        return self.__scale_range

    @scale_range.setter
    def scale_range(self, scale_range: list[float]):
        self.__scale_range = scale_range

    @property
    def type_switch(self) -> bool:
        """Recommendation type. Stores last chosen recommendation type. True - recommendation based on individual
        title(s). False - recommendation based on user's list(s) (`bool`)."""
        return self.__type_switch

    @type_switch.setter
    def type_switch(self, type_switch: bool):
        self.__type_switch = type_switch

    @property
    def input_values(self) -> list[str]:
        """List of chosen titles. Stores last chosen titles (`list[str]`)."""
        return self.__input_values

    @input_values.setter
    def input_values(self, input_values: list[str]):
        self.__input_values = input_values

    @property
    def language(self) -> str:
        """Language for titles (`str`)."""
        return self.__language

    @language.setter
    def language(self, language: str):
        self.__language = language

    @property
    def df(self) -> DataFrame:
        """DataFrame with recommendations. The purpose is to reduce the number of requests to the API. Stores
        information required to identify titles and visualize them (create UI cards). Stores external index,
        probability, cover image, color, description and title of recommendations. Rewrite values in probability column
        every time when the title appears in recommendations again (`DataFrame`)."""
        return self.__df

    @df.setter
    def df(self, df: DataFrame):
        self.__df = df

    @property
    def text_processor(self) -> Type[ITextProcessor]:
        """Text processor class. The purpose is to preprocess the newly acquired description of titles by removing html
        tags from it (`Type[ITextProcessor]`, read-only)."""
        return self.__text_processor
