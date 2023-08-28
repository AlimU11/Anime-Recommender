"""Callbacks for parameters section."""

from dash import Input, Output, State

from anime_recommender.ui.layout.layout_dynamic import alert_features
from anime_recommender.ui.layout.layout_static import feature_options
from anime_recommender.ui.plot_utils.scaled_plot import plot_scaled_unscaled_scores_diff
from anime_recommender.ui.ui_utils.dcw import callback
from anime_recommender.ui.ui_utils.dcw import callback_manager as cm
from anime_recommender.ui.ui_utils.id_holder import IdHolder as ID


@callback(
    [
        Output(ID.features_list, 'options'),
        Output(ID.features_alert, 'children'),
    ],
    Input(ID.features_list, 'value'),
    prevent_initial_call=True,
)
def update_features_list():
    """Prevent user from selecting less than 1 feature."""
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

    return [options, alert_features() if len(cm.features_list.value) == 1 else None]


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
    """Prevent user from selecting same list in both included and excluded lists."""
    excluded_list = [
        {'label': title['label'], 'value': title['value'], 'disabled': False}
        if title['value'] not in included
        else {'label': title['label'], 'value': title['value'], 'disabled': True}
        for title in excluded_list
    ]

    included_list = [
        {'label': title['label'], 'value': title['value'], 'disabled': False}
        if title['value'] not in excluded
        else {'label': title['label'], 'value': title['value'], 'disabled': True}
        for title in included_list
    ]

    return included_list, excluded_list


@callback(
    Output(ID.scaled_container, 'style'),
    Input(ID.is_weighted, 'value'),
    prevent_initial_call=True,
)
def update_scaled():
    """Update scaled scores container visibility.

    Show or hide option to use user scores for recommendation depending on whether checkbox with ID `is_weighted` is
    checked or not.
    """
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
    """Show or hide option to scale scores depending on whether checkbox with ID `is_scaled` is checked or not."""
    if cm.is_scaled.value and cm.is_weighted.value:
        return {'display': 'block'}
    return {'display': 'none'}


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
    """Update graph showing difference between scaled and unscaled scores."""
    return plot_scaled_unscaled_scores_diff()
