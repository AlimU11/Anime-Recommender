"""Callbacks for searchbar and output container."""

import dash_bootstrap_components as dbc
from dash import Input, Output, State, ctx, no_update

from anime_recommender.config import config
from anime_recommender.ui.app_data import app_data
from anime_recommender.ui.callbacks.callback_utils import get_recommendations, update_app_data
from anime_recommender.ui.constants import NUMBER_OF_TITLES
from anime_recommender.ui.layout.layout_dynamic import card, option_template, user_lists
from anime_recommender.ui.ui_utils.dcw import callback
from anime_recommender.ui.ui_utils.dcw import callback_manager as cm
from anime_recommender.ui.ui_utils.id_holder import IdHolder as ID


@callback(
    [
        Output(ID.input_group, 'style'),
        Output(ID.source, 'toggle_style'),
        Output(ID.input_group_text, 'style'),
        Output(ID.username_searchbar, 'style'),
        Output(ID.item_searchbar, 'style'),
        Output(ID.search_type_switch, 'label'),
        Output(ID.score_container, 'style'),
        Output(ID.user_lists, 'style'),
        Output(ID.user_lists, 'children'),
    ],
    [
        Input(ID.search_type_switch, 'value'),
        Input(ID.trigger_switch_update, 'n_clicks'),
    ],
)
def change_search_type():  # noqa: WPS210
    """Change search type between username and titles."""
    input_group_style = (
        {'grid-template-columns': '1fr max-content'}
        if cm.search_type_switch.value
        else {'grid-template-columns': 'max-content max-content 1fr max-content'}
    )

    is_username_searchbar_active_and_valid = (
        not cm.search_type_switch.value and app_data.service.client and app_data.service.client.user_id
    )

    user_lists_style = {'display': 'block'} if is_username_searchbar_active_and_valid else {'display': 'none'}

    user_lists_children = (
        user_lists(
            [
                {
                    'label': user_list,
                    'value': user_list,
                }
                for user_list in list(app_data.service.client.user_lists.keys())
            ],
        )
        if is_username_searchbar_active_and_valid
        else no_update
    )

    username_source_style = {'display': 'none'} if cm.search_type_switch.value else {'display': 'block'}

    username_input_group_style = {'display': 'none'} if cm.search_type_switch.value else {'display': 'block'}

    username_searchbar_style = (
        {'display': 'none'} if cm.search_type_switch.value else {'display': 'block', 'width': '100%'}
    )

    item_searchbar_style = {'display': 'table'} if cm.search_type_switch.value else {'display': 'none'}

    score_container_style = {'display': 'none'} if cm.search_type_switch.value else {'display': 'block'}

    switch_label = 'By title' if cm.search_type_switch.value else 'By username'

    return [
        input_group_style,
        username_source_style,
        username_input_group_style,
        username_searchbar_style,
        item_searchbar_style,
        switch_label,
        score_container_style,
        user_lists_style,
        user_lists_children,
    ]


@callback(
    [
        Output(ID.titles_language, 'label'),
        Output(ID.output_container, 'children', allow_duplicate=True),
    ],
    [
        Input(ID.english, 'n_clicks'),
        Input(ID.romaji, 'n_clicks'),
        Input(ID.native, 'n_clicks'),
    ],
    State(ID.output_container, 'children'),
    prevent_initial_call=True,
)
def update_titles_language():
    """Update titles language."""
    language = ctx.triggered[0]['prop_id'].split('.')[0]
    app_data.ui_state.language = language

    output_not_empty_and_language_changed = (
        cm.output_container.children
        and cm.output_container.children['props']['children'][0]['props']['children']  # noqa: WPS219
        and app_data.df is not None
    )

    output = (
        dbc.Row(
            app_data.df.iloc[:NUMBER_OF_TITLES].apply(card, axis=1).tolist(),
            justify='evenly',
            align='center',
            className='mt-5',
        )
        if output_not_empty_and_language_changed
        else no_update
    )

    return language, output


@callback(
    Output(ID.item_searchbar, 'options'),
    [
        Input(ID.titles_language, 'label'),
        Input(ID.item_searchbar, 'search_value'),
        Input(ID.item_searchbar, 'value'),
    ],
)
def update_items_dropdown(language, search_value, selected_indexes):
    """Update dropdown with titles based on searchbar value and language."""
    chosen_items = option_template(selected_indexes, language) if selected_indexes else []
    items_return = []
    is_searchbar_empty = not search_value
    selected_indexes = selected_indexes or []

    if is_searchbar_empty:
        items_return = (
            app_data.by_popularity.query('id not in @selected_indexes').head(config.dropdown_item_count).id.tolist()
        )
        return option_template(items_return, language) + chosen_items

    for row in app_data.by_popularity.query('id not in @selected_indexes').itertuples():
        if search_value.lower() in row.english.lower():
            items_return.append(row.id)

        if len(items_return) >= config.dropdown_item_count:
            return option_template(items_return, language) + chosen_items

    return option_template(items_return, language) + chosen_items


@callback(
    [
        Output(ID.output_container, 'children', allow_duplicate=True),
        Output(ID.trigger_modal_update, 'n_clicks'),
        Output(ID.trigger_switch_update, 'n_clicks'),
    ],
    [
        Input(ID.generate_button, 'n_clicks'),
        Input(ID.apply_button, 'n_clicks'),
    ],
    [
        State(ID.search_type_switch, 'value'),
        State(ID.output_container, 'children'),
        State(ID.username_searchbar, 'value'),
        State(ID.item_searchbar, 'value'),
        State(ID.recommender_type, 'value'),
        State(ID.modal_notification, 'is_open'),
        State(ID.features_list, 'value'),
        State(ID.is_weighted, 'value'),
        State(ID.is_scaled, 'value'),
        State(ID.scale_slider, 'value'),
        State(ID.included_list, 'value'),
        State(ID.excluded_list, 'value'),
        State(ID.user_lists, 'style'),
        State(ID.user_lists, 'children'),
        State(ID.titles_language, 'label'),
    ],
    prevent_initial_call=True,
)
def update_output():
    """Update output container with recommendations."""
    update_app_data()
    return get_recommendations()
