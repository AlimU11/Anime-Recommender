from enum import Enum, auto


class IdHolder(Enum):
    """ID holder for dash components"""

    # modal window
    modal_notification = auto()

    # buttons and switches
    generate_button = auto()
    apply_button = auto()
    close_button = auto()
    search_type_switch = auto()

    # dropdowns and inputs
    username_searchbar = auto()
    username_searchbar_container = auto()
    item_searchbar = auto()
    item_searchbar_container = auto()

    # title language and profile source
    username_source = auto()
    titles_language_username = auto()
    titles_language_titles = auto()

    # buttons in dropdown
    english = auto()
    romaji = auto()
    native = auto()

    english_username = auto()
    romaji_username = auto()
    native_username = auto()

    Anilist = auto()

    # output
    output_container = auto()

    # parameters

    # recommender
    recommender_type = auto()

    # features
    features_list = auto()
    features_alert = auto()

    # user lists
    user_lists = auto()
    included_list = auto()
    excluded_list = auto()

    # weights and scaling
    score_container = auto()

    is_weighted = auto()
    weighted_container = auto()

    is_scaled = auto()
    score_description = auto()
    scaled_container = auto()
    scale_slider = auto()
    graph = auto()
    reset_graph_button = auto()
    graph_container = auto()

    # info toast
    info_container = auto()
    info_button = auto()

    hidden = auto()
