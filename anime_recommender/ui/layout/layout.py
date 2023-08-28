"""Web App layout."""
import dash_bootstrap_components as dbc
from dash import html

from anime_recommender.ui.layout.layout_dynamic import modal_body
from anime_recommender.ui.layout.layout_static import info_button, main, settings
from anime_recommender.ui.ui_utils.id_holder import IdHolder as ID

layout = html.Div(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    dbc.Row([main, settings], align='center'),
                    dbc.Modal([modal_body('', '')], id=ID.modal_notification, is_open=False),
                    html.Span(className='hidden', id=ID.hidden),
                ],
                class_name='main-card-body',
            ),
            class_name='main-card',
        ),
        dbc.Button(id=ID.trigger_modal_update),
        dbc.Button(id=ID.trigger_switch_update),
        *info_button,
    ],
)
