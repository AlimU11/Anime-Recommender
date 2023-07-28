import dash_bootstrap_components as dbc
from dash import Input, Output, State, ctx, no_update
from dash.dependencies import ClientsideFunction

from .callback_utils import (
    get_recommendations,
    plot_scaled_unscaled_scores_diff,
    update_app_data,
)
from .layout import (
    RESULT_AMOUNT,
    alert_features,
    app,
    app_data,
    by_popularity,
    card,
    feature_options,
    modal_body,
    option_template,
    user_lists,
)
from .utils.dcw import callback
from .utils.dcw import callback_manager as cm
from .utils.IdHolder import IdHolder as ID

app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='resizeOnPageLoad',
    ),
    Output(ID.hidden, 'children'),
    Input(ID.hidden, 'children'),
)


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
def change_search_type():
    """Changes search type between username and titles"""

    input_group_style = (
        {'grid-template-columns': '1fr max-content'}
        if cm.search_type_switch.value
        else {'grid-template-columns': 'max-content max-content 1fr max-content'}
    )

    is_username_searchbar_active_and_valid = (
        not cm.search_type_switch.value and app_data.client and app_data.client.user_id
    )

    user_lists_style = {'display': 'block'} if is_username_searchbar_active_and_valid else {'display': 'none'}

    user_lists_children = (
        user_lists(
            [{'label': i, 'value': i} for i in list(app_data.client.user_lists.keys())],
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
        Output(ID.features_list, 'options'),
        Output(ID.features_alert, 'children'),
    ],
    Input(ID.features_list, 'value'),
    prevent_initial_call=True,
)
def update_features_list():
    """Prevents user from selecting less than 1 feature"""
    options = feature_options
    if len(cm.features_list.value) == 1:
        options = [
            {
                'label': option['label'],
                'value': option['value'],
                'disabled': option['value'] in cm.features_list.value,
            }
            for option in options
        ]

    else:
        options = [
            {
                'label': option['label'],
                'value': option['value'],
                'disabled': False,
            }
            for option in options
        ]

    return [options, alert_features if len(cm.features_list.value) == 1 else None]


@callback(
    [
        Output(ID.included_list, 'options'),
        Output(ID.excluded_list, 'options'),
    ],
    [
        Input(ID.included_list, 'value'),
        Input(ID.excluded_list, 'value'),
    ],
    [
        State(ID.included_list, 'options'),
        State(ID.excluded_list, 'options'),
    ],
)
def user_lists_mutual_exclusion(included, excluded, included_list, excluded_list):
    """Prevents user from selecting same list in both included and excluded lists"""
    excluded_list = [
        {'label': i['label'], 'value': i['value'], 'disabled': False}
        if i['value'] not in included
        else {'label': i['label'], 'value': i['value'], 'disabled': True}
        for i in excluded_list
    ]

    included_list = [
        {'label': i['label'], 'value': i['value'], 'disabled': False}
        if i['value'] not in excluded
        else {'label': i['label'], 'value': i['value'], 'disabled': True}
        for i in included_list
    ]

    return included_list, excluded_list


@callback(
    Output(ID.scaled_container, 'style'),
    Input(ID.is_weighted, 'value'),
    prevent_initial_call=True,
)
def update_scaled():
    """Shows or hides option to use user scores for recommendation depending on whether checkbox with ID `is_weighted` is checked or not"""
    return {'display': 'block'} if cm.is_weighted.value else {'display': 'none'}


@callback(
    Output(ID.graph_container, 'style'),
    [
        Input(ID.is_scaled, 'value'),
        Input(ID.is_weighted, 'value'),
    ],
    prevent_initial_call=True,
)
def update_scaled_container():
    """Shows or hides option to scale scores depending on whether checkbox with ID `is_scaled` is checked or not"""
    return {'display': 'block'} if cm.is_scaled.value and cm.is_weighted.value else {'display': 'none'}


@callback(
    [
        Output(ID.graph, 'figure'),
        Output(ID.scale_slider, 'value'),
        Output(ID.score_description, 'children'),
    ],
    [
        Input(ID.scale_slider, 'value'),
        Input(ID.reset_graph_button, 'n_clicks'),
    ],
)
def update_scaled_graph():
    """Updates graph showing difference between scaled and unscaled scores"""
    return plot_scaled_unscaled_scores_diff()


@callback(
    Output(ID.info_container, 'is_open'),
    Input(ID.info_button, 'n_clicks'),
    State(ID.info_container, 'is_open'),
    prevent_initial_call=True,
)
def update_info_toast(n, is_open):
    """Shows or hides info toast"""
    if n and not is_open:
        return True
    return False


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
    """Updates titles language"""
    app_data.language = ctx.triggered[0]['prop_id'].split('.')[0]

    output = (
        dbc.Row(
            app_data.df.iloc[:20].apply(card, axis=1).tolist(),
            justify='evenly',
            align='center',
            className='mt-5',
        )
        if cm.output_container.children
        and cm.output_container.children['props']['children'][0]['props']['children']
        and app_data.df is not None
        else no_update
    )
    return app_data.language, output


@callback(
    Output(ID.item_searchbar, 'options'),
    [
        Input(ID.titles_language, 'label'),
        Input(ID.item_searchbar, 'search_value'),
        Input(ID.item_searchbar, 'value'),
    ],
)
def update_items_dropdown(language, search_value, selected_indexes):
    """Updates dropdown with titles based on searchbar value and language"""
    chosen_items = option_template(selected_indexes, language) if selected_indexes else []
    items_return = []
    is_searchbar_empty = not search_value
    selected_indexes = selected_indexes or []

    if is_searchbar_empty:
        items_return = by_popularity.query('id not in @selected_indexes').head(RESULT_AMOUNT).id.tolist()
        return option_template(items_return, language) + chosen_items

    for row in by_popularity.query('id not in @selected_indexes').itertuples():
        if search_value.lower() in row.english.lower():
            items_return.append(row.id)

        if len(items_return) >= RESULT_AMOUNT:
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
    """Updates output container with recommendations"""
    update_app_data()
    return get_recommendations()


@callback(
    [
        Output(ID.modal_notification, 'is_open'),
        Output(ID.modal_notification, 'children'),
    ],
    [
        Input(ID.trigger_modal_update, 'n_clicks'),
        Input(ID.close_button, 'n_clicks'),
    ],
    prevent_initial_call=True,
)
def update_modal():
    """Shows modal with error message if search field is empty after `update_output` callback is triggered"""
    if ctx.triggered_id == ID.trigger_modal_update:
        return True, modal_body('Empty', 'Search field is empty')

    return False, modal_body('', '')
