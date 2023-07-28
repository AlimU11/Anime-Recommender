from enum import auto

from .StrEnum import StrEnum


class IdHolder(StrEnum):
    """ID holder for dash components"""

    trigger_modal_update = auto()
    trigger_switch_update = auto()

    # modal window
    modal_notification = auto()

    # buttons and switches
    generate_button = auto()
    apply_button = auto()
    close_button = auto()
    search_type_switch = auto()

    # dropdowns and inputs
    username_searchbar = auto()
    item_searchbar = auto()
    searchbar_container = auto()
    input_group = auto()
    input_group_text = auto()

    # title language and profile source
    source = auto()
    titles_language = auto()

    # buttons in dropdown
    english = auto()
    romaji = auto()
    native = auto()

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

    # alert
    not_found_alert = auto()
