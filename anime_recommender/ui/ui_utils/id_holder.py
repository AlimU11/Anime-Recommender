"""
Module for centralized management of unique component IDs in a dashboard.

This module provides the `IdHolder` enumeration, which contains string constants
generated using the auto() method. These constants are used as unique IDs for various
Dash components, ensuring a consistent and organized method of referencing components
across the application.

This approach aids in preventing potential ID clashes and provides a single source of truth
for component ID naming.

Classes
-------
IdHolder : StrEnum
    An enumeration derived from `StrEnum` that holds unique IDs for various Dash
    components such as modals, buttons, dropdowns, inputs, and more.

Notes
-----
Using a centralized enum for IDs like this helps in ensuring consistency, especially in
larger projects where multiple developers might be working on different parts of the
Dash callbacks.

Author
------
AlimU
"""

from enum import auto

from anime_recommender.ui.ui_utils.str_enum import StrEnum


class IdHolder(StrEnum):
    """ID holder for dash components."""

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

    anilist = auto()

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
