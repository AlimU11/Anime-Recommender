"""Callback util functions."""


import dash_bootstrap_components as dbc
import pandas as pd
from dash import no_update
from dash.development.base_component import Component

from anime_recommender.recommender.recommender import Recommender, RecommenderConfig, SimilarityMethod, VectorUtility
from anime_recommender.ui.app_data import app_data
from anime_recommender.ui.constants import NUMBER_OF_TITLES, USER_EXCLUDED_LISTS, USER_INCLUDED_LISTS
from anime_recommender.ui.layout.layout_dynamic import alert, card
from anime_recommender.ui.ui_utils.dcw import callback_manager as cm


def recommend_content() -> Component:
    """Get recommendations.

    Returns
    -------
    Component
        Output container with recommendations.
    """
    recommender_config = RecommenderConfig(
        app_data.ui_state.features_list,
        app_data.ui_state.included_lists,
        app_data.ui_state.excluded_lists,
        app_data.ui_state.is_weighted,
        app_data.ui_state.is_scaled,
        app_data.ui_state.scale_slider,
        app_data.ui_state.search_type_switch,
        app_data.ui_state.item_searchbar,
    )
    similarity_method = SimilarityMethod(app_data.ui_state.recommender_type)
    vector_utility = VectorUtility(similarity_method)
    app_data.service.recommender = Recommender(
        app_data.service.client,
        app_data.service.storage,
        recommender_config,
        vector_utility,
    )

    app_data.df = pd.merge(
        pd.DataFrame(app_data.service.recommender.recommend(), columns=['id', 'proba']),
        app_data.service.storage.info,
        how='left',
        left_on='id',
        right_on='id',
    )

    df = app_data.df.iloc[:NUMBER_OF_TITLES]

    pd.options.mode.chained_assignment = None

    df.loc[:, 'id'] = df.id.astype(int)
    df.loc[:, 'description'] = df.description.apply(
        lambda desc: app_data.service.text_processor(desc).remove_html_tags(),
    )

    pd.options.mode.chained_assignment = 'warn'

    cards = (
        df.sort_values(
            by='proba',
            ascending=False,
        )
        .apply(card, axis=1)
        .tolist()
    )

    return dbc.Row(cards, justify='evenly', align='center', className='mt-5')


def update_app_data():
    """Update app data."""
    is_weighted_and_scaled_scores = cm.is_weighted.value and cm.is_scaled.value

    app_data.ui_state.search_type_switch = cm.search_type_switch.value
    app_data.ui_state.username_searchbar = cm.username_searchbar.value
    app_data.ui_state.item_searchbar = cm.item_searchbar.value
    app_data.ui_state.recommender_type = cm.recommender_type.value
    app_data.ui_state.modal_notification = cm.modal_notification.is_open
    app_data.ui_state.features_list = cm.features_list.value
    app_data.ui_state.is_weighted = cm.is_weighted.value
    app_data.ui_state.is_scaled = is_weighted_and_scaled_scores
    app_data.ui_state.scale_slider = cm.scale_slider.value if is_weighted_and_scaled_scores else None
    # NOTE: possible overlap with initialization in get_recommendations()
    app_data.ui_state.included_lists = cm.included_list.value
    app_data.ui_state.excluded_lists = cm.excluded_list.value
    app_data.ui_state.user_lists_style = cm.user_lists.style
    app_data.ui_state.user_lists = cm.user_lists.children
    app_data.ui_state.language = cm.titles_language.label


def is_searchbar_empty_and_active() -> bool:
    """Check if either username or item searchbar is empty and active.

    Returns
    -------
    bool
        True if searchbar is empty and active, False otherwise.
    """
    is_username_searchbar_active = not app_data.ui_state.search_type_switch
    is_username_searchbar_active_and_empty = not app_data.ui_state.username_searchbar and is_username_searchbar_active
    is_item_searchbar_active_and_empty = not app_data.ui_state.item_searchbar and not is_username_searchbar_active

    return is_username_searchbar_active_and_empty or is_item_searchbar_active_and_empty


def update_username_if_not_match():
    """Update username if it doesn't match with the current one."""
    username_not_match = (
        app_data.ui_state.username_searchbar
        and app_data.service.client.username != app_data.ui_state.username_searchbar.strip().lower()
    )

    if username_not_match:
        app_data.service.client.username = app_data.ui_state.username_searchbar.strip().lower()
        app_data.ui_state.included_lists = USER_INCLUDED_LISTS
        app_data.ui_state.excluded_lists = USER_EXCLUDED_LISTS


def set_user_lists_style():
    """Set the display style for user lists based on conditions.

    If username searchbar is active and not empty, display user lists.
    """
    if not app_data.ui_state.user_lists_style:
        app_data.ui_state.user_lists_style = {}

    should_display_block = (
        not app_data.ui_state.search_type_switch
        and app_data.service.client
        and app_data.service.client.username
        and app_data.service.client.user_id
    )

    app_data.ui_state.user_lists_style['display'] = 'block' if should_display_block else 'none'


def get_recommendations() -> tuple[Component, Component, Component]:
    """Check recommendations strategy.

    Returns
    -------
    tuple[Component, Component, Component]
        Recommendations or alert message, user lists, and user lists style.
    """
    if is_searchbar_empty_and_active():
        return no_update, 0, no_update

    update_username_if_not_match()

    is_username_searchbar_active = not app_data.ui_state.search_type_switch
    if not is_username_searchbar_active or app_data.service.client.user_id:
        set_user_lists_style()

        return recommend_content(), no_update, 0

    return alert(), no_update, no_update
