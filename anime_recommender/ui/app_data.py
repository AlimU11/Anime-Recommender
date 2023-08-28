"""App Data Module.

Contains classes essential for managing the web application's state and
the various services it relies upon. Central to the module is the AppData class, which
serves as the primary data holder for the application. This data is sourced from and
interacts with various services, each represented as distinct classes within the module.
"""

from typing import Type

from attr import dataclass
from pandas import DataFrame

from anime_recommender.client import AnilistClient, IClient
from anime_recommender.etl.ITextProcessor import ITextProcessor
from anime_recommender.etl.TextProcessor import TextProcessor
from anime_recommender.recommender.recommender_interface import IRecommender
from anime_recommender.storage import IStorage, LocalStorage


@dataclass
class UIState(object):
    """Web App data class. Represent the current state of the web application's user interface.

    This class serves as a container for various UI-related properties and settings,
    capturing user choices and preferences during their interaction with the application.
    By abstracting these UI elements into this data class, the application can more easily
    respond to user interactions, update the UI dynamically, and store or reset the UI
    state as necessary.

    Attributes
    ----------
    search_type_switch : bool
        Recommendation type. Stores last chosen recommendation type. True - recommendation based on individual
        titles. False - recommendation based on user's lists.

    username_searchbar : str, optional
        Username searchbar. Stores last chosen username.

    item_searchbar : list[str]
        List of chosen titles. Stores last chosen titles.

    recommender_type : str
        Similarity method used by recommender. Stores last chosen similarity method.

    modal_notification : bool
        Modal window flag. Stores whether modal window is open.

    features_list : list[str]
        List of columns used by recommender. Stores last chosen columns.

    included_lists : list[str]
        List of included lists of user used by recommender. Stores last chosen included lists.

    excluded_lists : list[str]
        List of excluded lists of user used by recommender. Stores last chosen excluded lists.

    is_weighted : bool
        Weighted flag used by recommender. Stores last chosen weighted flag.

    is_scaled : bool
        Scaled flag used by recommender. Stores last chosen scaled flag.

    scale_slider : list[float]
        Scale range used by recommender. Stores last chosen scale range.

    user_lists_style : dict
        Style of user's lists. Stores last chosen style of user's lists.

    user_lists : list
        List of user's lists. Stores last chosen user's lists.

    language : str
        Language for titles.
    """

    search_type_switch: bool = False
    username_searchbar: str | None = None
    item_searchbar: list[str] = []
    recommender_type: str = 'linear_kernel'
    modal_notification: bool = False
    features_list: list[str] = []
    included_lists: list[str] = []
    excluded_lists: list[str] = []
    is_weighted: bool = False
    is_scaled: bool = False
    scale_slider: list[float] = []
    user_lists_style: dict = {}
    user_lists: list = []
    language: str = 'english'


@dataclass
class Service(object):
    """Aggregator class for backend services and utilities.

    This encapsulation facilitates easier management and injection of these services
    into other components of the system. The class holds references to clients for external
    interactions, storage mechanisms, text processing utilities, and recommendation algorithms.
    By centralizing these services within this class, the application achieves a more modular
    design, making it convenient to switch out or modify individual services without extensive
    changes to other parts of the codebase.

    Attributes
    ----------
    client : IClient, optional
        IClient interface implementation.

    storage : IStorage, optional
        IStorage interface implementation.

    recommender : IRecommender, optional
        IRecommender interface implementation.

    text_processor : Type[ITextProcessor]
        Text processor class.
    """

    client: IClient | None = None
    storage: IStorage | None = None
    recommender: IRecommender | None = None
    _text_processor: Type[ITextProcessor] = TextProcessor

    @property
    def text_processor(self) -> Type[ITextProcessor]:
        """Text processor class.

        Preprocess the description for titles by removing html
        tags from it.

        Returns
        -------
        Type[ITextProcessor]
            Text processor class.
        """
        return self._text_processor


class AppData(object):
    """Compositon data class for Web App.

    AppData captures and manages the core data that powers the application. By interfacing
    with UIState, it ensures the data remains in sync with the current UI settings and
    user preferences. Through its connection with the Service class, AppData can access
    backend services, manipulate data based on user interactions, and manage how data flows
    within the application.

    Attributes
    ----------
    df : DataFrame, optional
        Recommendations data. Stores information required to identify titles and visualize them (create UI cards).
    """

    def __init__(self, service: Service, ui_state: UIState):
        """Initialize AppData class.

        Parameters
        ----------
        service : Service
            Service class.

        ui_state: UIState
            UIState class.
        """
        self._service: Service = service
        self._ui_state: UIState = ui_state
        self._df: DataFrame | None = None
        self._by_popularity: DataFrame = service.storage.info.sort_values(by='popularity', ascending=False)

    @property
    def service(self) -> Service:
        """Service class.

        Returns
        -------
        Service
            Service class.
        """
        return self._service

    @property
    def ui_state(self) -> UIState:
        """Web App data class.

        Returns
        -------
        UIState
            UIState class.
        """
        return self._ui_state

    @property
    def df(self) -> DataFrame | None:
        """Recommendations data.

        The purpose is to reduce the number of requests to the API. Stores
        information required to identify titles and visualize them (create UI cards). Stores external index,
        probability, cover image, color, description and title of recommendations. Rewrites values in probability column
        every time when the title appears in recommendations again.

        Returns
        -------
        DataFrame, optional
            DataFrame with recommendations.
        """
        return self._df

    @df.setter
    def df(self, df: DataFrame):
        self._df = df

    @property
    def by_popularity(self) -> DataFrame:
        """Titles sorted by popularity.

        Returns
        -------
        DataFrame
            DataFrame with titles sorted by popularity.
        """
        return self._by_popularity


client = AnilistClient()
storage = LocalStorage()
ui_state = UIState()
service = Service(client, storage)
app_data = AppData(service, ui_state)
