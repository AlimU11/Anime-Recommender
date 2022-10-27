import tracemalloc  # isort:skip
import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, ctx, dcc, html
from dash.exceptions import PreventUpdate
from sklearn.preprocessing import MinMaxScaler, minmax_scale

from . import IdHolder
from .layout import (  # , ITEMS_NATIVE, ITEMS_ROMAJI
    ITEMS_ENG,
    alert_features,
    app,
    app_data,
    feature_options,
)
from .utils import dispatcher


@app.callback(
    [
        Output(IdHolder.username_searchbar_container.name, 'style'),
        Output(IdHolder.item_searchbar_container.name, 'style'),
        Output(IdHolder.search_type_switch.name, 'label'),
        Output(IdHolder.score_container.name, 'style'),
    ],
    Input(IdHolder.search_type_switch.name, 'value'),
    prevent_initial_call=True,
)
def change_search_type(value):
    return (
        [{'display': 'none'}, {'display': 'block'}, 'By title', {'display': 'none'}]
        if value
        else [
            {'display': 'block'},
            {'display': 'none'},
            'By username',
            {'display': 'block'},
        ]
    )


@app.callback(
    [
        Output(IdHolder.features_list.name, 'options'),
        Output(IdHolder.features_alert.name, 'children'),
    ],
    Input(IdHolder.features_list.name, 'value'),
    prevent_initial_call=True,
)
def update_features_list(value):
    options = feature_options
    if len(value) == 1:
        options = [
            {
                'label': option['label'],
                'value': option['value'],
                'disabled': option['value'] in value,
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

    return [options, alert_features if len(value) == 1 else None]


@app.callback(
    [
        Output(IdHolder.included_list.name, 'options'),
        Output(IdHolder.excluded_list.name, 'options'),
    ],
    [
        Input(IdHolder.included_list.name, 'value'),
        Input(IdHolder.excluded_list.name, 'value'),
    ],
    [
        State(IdHolder.included_list.name, 'options'),
        State(IdHolder.excluded_list.name, 'options'),
    ],
)
def user_lists_mutual_exclusion(included, excluded, included_list, excluded_list):
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


@app.callback(
    Output(IdHolder.scaled_container.name, 'style'),
    Input(IdHolder.is_weighted.name, 'value'),
    prevent_initial_call=True,
)
def update_scaled(value):
    return {'display': 'block'} if value else {'display': 'none'}


@app.callback(
    Output(IdHolder.graph_container.name, 'style'),
    [
        Input(IdHolder.is_scaled.name, 'value'),
        Input(IdHolder.is_weighted.name, 'value'),
    ],
    prevent_initial_call=True,
)
def update_scaled_container(v1, v2):
    return {'display': 'block'} if v1 and v2 else {'display': 'none'}


@app.callback(
    [
        Output(IdHolder.graph.name, 'figure'),
        Output(IdHolder.scale_slider.name, 'value'),
        Output(IdHolder.score_description.name, 'children'),
    ],
    [
        Input(IdHolder.scale_slider.name, 'value'),
        Input(IdHolder.reset_graph_button.name, 'n_clicks'),
    ],
)
def update_scaled_graph(value, btn):
    normal_scores = np.array(
        [i for i in minmax_scale(np.arange(1, 11), feature_range=(1, 10))],
    )
    index = np.arange(1, 11)
    value = [-5, 4] if ctx.triggered_id == 'button' else value

    mm = MinMaxScaler(feature_range=(value[0], value[1]))
    mm.fit(np.arange(1, 11).reshape(-1, 1))

    scaled_scores = minmax_scale(
        np.array(
            [1 / (1 + np.exp(-i)) for i in mm.transform(np.arange(1, 11).reshape(-1, 1))],
        ).flatten(),
        feature_range=(1, 10),
    )

    where = np.argwhere(scaled_scores[1:-1] >= normal_scores[1:-1])
    val = normal_scores[where[0]][0] if where.shape[0] > 0 else 10

    lower = (
        [
            html.Br(),
            'All titles with scores ',
            html.B(f'below {val + 1 if val != 10 else val}'),
            ' will have ',
            html.B('less'),
            ' impact.',
        ]
        if val != 1
        else ['']
    )

    higher = (
        [
            'All titles with scores ',
            html.B(f'higher than {val}'),
            ' will have ',
            html.B(f'more'),
            ' impact.',
        ]
        if val != 10
        else ['']
    )

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=index, y=scaled_scores, name='<b>Scaled Scores</b>'))
    fig.add_trace(go.Scatter(x=index, y=normal_scores, name='<b>Normal Scores</b>'))

    fig.update_layout(
        title='',
        title_x=0.5,
        title_y=0.93,
        title_font_size=10,
        xaxis_title='Score',
        yaxis_title='Coefficient',
        hovermode='x unified',
        legend=dict(
            yanchor='top',
            y=-0.05,
            xanchor='left',
            x=0,
            bgcolor='rgba(0,0,0,0)',
            orientation='h',
        ),
        margin=dict(l=0, r=0, t=20, b=0),
    )

    fig.update_xaxes(title='', ticklabelposition='inside')
    fig.update_yaxes(ticklabelposition='inside top', title=None)

    fig.add_annotation(
        x=0.5,
        y=-0.05,
        xref='paper',
        yref='paper',
        showarrow=False,
        text='<b>Score<b>',
        font=dict(size=14),
    )

    return [fig, value, html.P(higher + lower)]


@app.callback(
    Output(IdHolder.info_container.name, 'is_open'),
    Input(IdHolder.info_button.name, 'n_clicks'),
    State(IdHolder.info_container.name, 'is_open'),
    prevent_initial_call=True,
)
def update_info_toast(n, is_open):
    if n and not is_open:
        return True
    return False


@app.callback(
    [
        Output(IdHolder.titles_language_titles.name, 'label'),
        Output(IdHolder.titles_language_username.name, 'label'),
    ],
    [
        Input(i, 'n_clicks')
        for i in [
            IdHolder.english.name,
            # IdHolder.romaji.name,
            # IdHolder.native.name,
        ]
    ]
    + [
        Input(i, 'n_clicks')
        for i in [
            IdHolder.english_username.name,
            # IdHolder.romaji_username.name,
            # IdHolder.native_username.name,
        ]
    ],
    prevent_initial_call=True,
)
def mutual_update_dropdown_language(*args):
    if not ctx.triggered:
        return [IdHolder.english.name, IdHolder.english.name]
    else:
        return [
            ctx.triggered[0]['prop_id'].split('.')[0].split('_')[0],
            ctx.triggered[0]['prop_id'].split('.')[0].split('_')[0],
        ]


@app.callback(
    [
        Output(IdHolder.item_searchbar.name, 'options'),
    ],
    [
        Input(IdHolder.titles_language_titles.name, 'label'),
    ],
    prevent_initial_call=True,
)
def update_items_dropdown(language):
    if language == 'english':
        items = ITEMS_ENG
    # elif language == 'romaji':
    #     items = ITEMS_ROMAJI
    # elif language == 'native':
    #     items = ITEMS_NATIVE

    return [items]


@app.callback(
    [
        Output(IdHolder.output_container.name, 'children'),
        Output(IdHolder.modal_notification.name, 'is_open'),
        Output(IdHolder.modal_notification.name, 'children'),
        Output(IdHolder.user_lists.name, 'style'),
        Output(IdHolder.user_lists.name, 'children'),
        Output(IdHolder.is_weighted.name, 'value'),
    ],
    [
        Input(IdHolder.generate_button.name, 'n_clicks'),
        Input(IdHolder.apply_button.name, 'n_clicks'),
        Input(IdHolder.close_button.name, 'n_clicks'),
        Input(IdHolder.search_type_switch.name, 'value'),
    ],
    [
        State(IdHolder.output_container.name, 'children'),
        State(IdHolder.username_searchbar.name, 'value'),
        State(IdHolder.recommender_type.name, 'value'),
        State(IdHolder.modal_notification.name, 'is_open'),
        State(IdHolder.features_list.name, 'value'),
        State(IdHolder.is_weighted.name, 'value'),
        State(IdHolder.is_scaled.name, 'value'),
        State(IdHolder.scale_slider.name, 'value'),
        State(IdHolder.included_list.name, 'value'),
        State(IdHolder.excluded_list.name, 'value'),
        State(IdHolder.user_lists.name, 'style'),
        State(IdHolder.user_lists.name, 'children'),
        State(IdHolder.item_searchbar.name, 'value'),
        State(IdHolder.titles_language_titles.name, 'label'),
    ],
    prevent_initial_call=True,
)
def dispatch(
    _,
    _1,
    _2,
    type_switch,
    output_content,
    username,
    recommender_type,
    is_open,
    columns,
    is_weighted,
    scaled,
    scale_slider,
    included,
    excluded,
    style,
    columns_container,
    item_values,
    language,
):
    return dispatcher(
        type_switch,
        output_content,
        username,
        recommender_type,
        is_open,
        columns,
        is_weighted,
        scaled,
        scale_slider,
        included,
        excluded,
        style,
        columns_container,
        item_values,
        language,
    )
