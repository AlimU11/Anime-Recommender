"""Callbacks for miscellaneous UI elements."""

from dash import Input, Output, State, clientside_callback, ctx
from dash.dependencies import ClientsideFunction

from anime_recommender.ui.layout.layout_dynamic import modal_body
from anime_recommender.ui.ui_utils.dcw import callback
from anime_recommender.ui.ui_utils.id_holder import IdHolder as ID

cl = clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='resizeOnPageLoad',
    ),
    Output(ID.hidden, 'children'),
    Input(ID.hidden, 'children'),
)


@callback(
    Output(ID.info_container, 'is_open'),
    Input(ID.info_button, 'n_clicks'),
    State(ID.info_container, 'is_open'),
    prevent_initial_call=True,
)
def update_info_toast(n_clicks, is_open):
    """Show or hide info toast."""
    return n_clicks and not is_open


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
    """Show modal with error message if search field is empty after `update_output` callback is triggered."""
    if ctx.triggered_id == ID.trigger_modal_update:
        return True, modal_body('Empty', 'Search field is empty')

    return False, modal_body('', '')
