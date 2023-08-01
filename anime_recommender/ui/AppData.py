from typing import Sequence, Type

from dash.development.base_component import Component
from pandas import DataFrame

from ..client import IClient
from ..etl import ITextProcessor, TextProcessor
from ..recommender import IRecommender
from ..storage import IStorage


class AppData:
    """Web App data holder class.

    Attributes
    ----------
    __client : IClient, optional

    __storage : IStorage, optional

    __recommender : IRecommender, optional

    __search_type_switch : bool

    __output_container : Sequence[Component]

    __username_searchbar : str, optional

    __item_searchbar : list[str]

    __recommender_type : str, optional

    __modal_notification : bool

    __features_list : list[str]

    __included_lists : list[str]

    __excluded_lists : list[str]

    __is_weighted : bool

    __is_scaled : bool

    __scale_slider : list[float], optional

    __user_lists_style : dict

    __user_lists : list

    __language : str

    __df : DataFrame

    __text_processor : Type[ITextProcessor]
    """

    def __init__(self):
        self.__client: IClient | None = None
        self.__storage: IStorage | None = None
        self.__recommender: IRecommender | None = None

        self.__search_type_switch: bool = False
        self.__output_container: Sequence[Component] | None = None

        self.__username_searchbar: str | None = None
        self.__item_searchbar: list[str] = []

        self.__recommender_type: str | None = None
        self.__modal_notification: bool = False

        self.__features_list: list[str] = []
        self.__included_lists: list[str] = []
        self.__excluded_lists: list[str] = []
        self.__is_weighted: bool = False
        self.__is_scaled: bool = False
        self.__scale_slider: list[float] | None = []

        self.__user_lists_style: dict = {}
        self.__user_lists: list = []

        self.__language: str = 'english'
        self.__df: DataFrame | None = None
        self.__text_processor: Type[ITextProcessor] = TextProcessor

    @property
    def client(self) -> IClient | None:
        """IClient interface implementation (`IClient`, optional)."""
        return self.__client

    @client.setter
    def client(self, client: IClient):
        self.__client = client

    @property
    def storage(self) -> IStorage | None:
        """IStorage interface implementation (`IStorage`, optional)."""
        return self.__storage

    @storage.setter
    def storage(self, storage: IStorage):
        self.__storage = storage

    @property
    def recommender(self) -> IRecommender | None:
        """IRecommender interface implementation (`IRecommender`, optional)."""
        return self.__recommender

    @recommender.setter
    def recommender(self, recommender: IRecommender):
        self.__recommender = recommender

    @property
    def search_type_switch(self) -> bool:
        """Recommendation type. Stores last chosen recommendation type. True - recommendation based on individual
        title(s). False - recommendation based on user's list(s) (`bool`)."""
        return self.__search_type_switch

    @search_type_switch.setter
    def search_type_switch(self, search_type_switch: bool):
        self.__search_type_switch = search_type_switch

    @property
    def output_container(self) -> Sequence[Component] | None:
        """Recommendation grid container. Stores last state of recommendation grid container (`Sequence[Component]`)."""
        return self.__output_container

    @output_container.setter
    def output_container(self, output_container: Sequence[Component] | None):
        self.__output_container = output_container

    @property
    def username_searchbar(self) -> str | None:
        """Username searchbar. Stores last chosen username (`str`, optional)."""
        return self.__username_searchbar

    @username_searchbar.setter
    def username_searchbar(self, username: str):
        self.__username_searchbar = username

    @property
    def recommender_type(self) -> str | None:
        """Similarity method used by recommender. Stores last chosen similarity method (`str`, optional)."""
        return self.__recommender_type

    @recommender_type.setter
    def recommender_type(self, similarity_method: str):
        self.__recommender_type = similarity_method

    @property
    def modal_notification(self) -> bool:
        """Modal window flag. Stores whether modal window is open (`bool`)."""
        return self.__modal_notification

    @modal_notification.setter
    def modal_notification(self, modal_notification: bool):
        self.__modal_notification = modal_notification

    @property
    def features_list(self) -> list[str]:
        """List of columns used by recommender. Stores last chosen columns (`list[str]`)."""
        return self.__features_list

    @features_list.setter
    def features_list(self, columns: list[str]):
        self.__features_list = columns

    @property
    def is_weighted(self) -> bool:
        """Weighted flag used by recommender. Stores last chosen weighted flag (`bool`)."""
        return self.__is_weighted

    @is_weighted.setter
    def is_weighted(self, weighted: bool):
        self.__is_weighted = weighted

    @property
    def is_scaled(self) -> bool:
        """Scaled flag used by recommender. Stores last chosen scaled flag (`bool`)."""
        return self.__is_scaled

    @is_scaled.setter
    def is_scaled(self, is_scaled: bool):
        self.__is_scaled = is_scaled

    @property
    def scale_slider(self) -> list[float] | None:
        """Scale range used by recommender. Stores last chosen scale range (`list[float]`)."""
        return self.__scale_slider

    @scale_slider.setter
    def scale_slider(self, scale_slider: list[float] | None):
        self.__scale_slider = scale_slider

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
    def item_searchbar(self) -> list[str]:
        """List of chosen titles. Stores last chosen titles (`list[str]`)."""
        return self.__item_searchbar

    @item_searchbar.setter
    def item_searchbar(self, item_searchbar: list[str]):
        self.__item_searchbar = item_searchbar

    @property
    def user_lists_style(self) -> dict:
        """Style of user's lists. Stores last chosen style of user's lists (`dict`)."""
        return self.__user_lists_style

    @user_lists_style.setter
    def user_lists_style(self, user_lists_style: dict):
        self.__user_lists_style = user_lists_style

    @property
    def user_lists(self) -> list:
        """List of user's lists. Stores last chosen user's lists (`list`)."""
        return self.__user_lists

    @user_lists.setter
    def user_lists(self, user_lists: list):
        self.__user_lists = user_lists

    @property
    def language(self) -> str:
        """Language for titles (`str`)."""
        return self.__language

    @language.setter
    def language(self, language: str):
        self.__language = language

    @property
    def df(self) -> DataFrame | None:
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
