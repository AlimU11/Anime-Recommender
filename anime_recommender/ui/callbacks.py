import tracemalloc  # isort:skip

import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, ctx, dcc, html
from sklearn.preprocessing import MinMaxScaler, minmax_scale

from .layout import app, feature_options
from .utils import dispatcher


@app.callback(
    [
        Output('search-user-input-container', 'style'),
        Output('search-title-input-container', 'style'),
        Output('search-switch', 'label'),
        Output('score-container', 'style'),
    ],
    Input('search-switch', 'value'),
)
def search_switch(value):
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
        Output('checklist-features', 'options'),
        Output('alert-included-features', 'children'),
    ],
    Input('checklist-features', 'value'),
)
def update_multi_options(value):
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

    alert = dbc.Alert(
        [
            html.I(className='bi bi-info-circle-fill me-2'),
            'At least one feature must be selected',
        ],
        color='info',
        className='d-flex align-items-center',
        style={
            'height': 'fit-content',
            'font-size': '0.8em',
            'margin': '0px',
            'margin-bottom': '1rem',
            'padding': '2px 5px',
        },
    )

    return [options, alert if len(value) == 1 else None]


@app.callback(
    [
        Output('checklist-included', 'options'),
        Output('checklist-excluded', 'options'),
    ],
    [
        Input('checklist-included', 'value'),
        Input('checklist-excluded', 'value'),
    ],
    [
        State('checklist-included', 'options'),
        State('checklist-excluded', 'options'),
    ],
)
def lists_mutual_exclusion(included, excluded, included_list, excluded_list):
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
    Output('container-scaled', 'style'),
    Input('checklist-weighted', 'value'),
)
def update_scaled(value):
    return {'display': 'block'} if value else {'display': 'none'}


@app.callback(
    Output('scale-graph-container', 'style'),
    [
        Input('checklist-scaled', 'value'),
        Input('checklist-weighted', 'value'),
    ],
)
def change_visibility(v1, v2):
    return {'display': 'block'} if v1 and v2 else {'display': 'none'}


@app.callback(
    [
        Output('graph', 'figure'),
        Output('scale-slider', 'value'),
        Output('scale-text', 'children'),
    ],
    [Input('scale-slider', 'value'), Input('reset-graph', 'n_clicks')],
)
def update_output(value, btn):
    normal_scores = np.array([i for i in minmax_scale(np.arange(1, 11), feature_range=(1, 10))])
    index = np.arange(1, 11)
    value = [-5, 4] if ctx.triggered_id == 'button' else value

    mm = MinMaxScaler(feature_range=(value[0], value[1]))
    mm.fit(np.arange(1, 11).reshape(-1, 1))

    scaled_scores = minmax_scale(
        np.array([1 / (1 + np.exp(-i)) for i in mm.transform(np.arange(1, 11).reshape(-1, 1))]).flatten(),
        feature_range=(1, 10),
    )

    where = np.argwhere(scaled_scores[1:-1] >= normal_scores[1:-1])
    val = normal_scores[where[0]][0] if where.shape[0] > 0 else 10

    # lower = f'All titles with scores <b>below {val+1 if val != 10 else val}</b> will have <b>less</b> impact.' if val != 1 else ''
    # higher = f'<br>All titles with scores <b>higher than {val}</b> will have <b>more</b> impact.' if val != 10 else ''

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

    fig = go.Figure(go.Scatter(x=index, y=scaled_scores, name='<b>Scaled Scores</b>'))
    fig.add_trace(go.Scatter(x=index, y=normal_scores, name='<b>Normal Scores</b>'))
    fig.update_layout(title='', title_x=0.5, title_y=0.93, title_font_size=10)
    fig.update_layout(xaxis_title='Score', yaxis_title='Coefficient')
    fig.update_layout(hovermode='x unified')
    fig.update_layout(
        legend=dict(
            yanchor='top',
            y=-0.05,
            xanchor='left',
            x=0,
            bgcolor='rgba(0,0,0,0)',
            orientation='h',
        ),
    )
    fig.update_yaxes(ticklabelposition='inside top', title=None)
    fig.update_xaxes(title='')
    fig.add_annotation(
        x=0.5,
        y=-0.05,
        xref='paper',
        yref='paper',
        showarrow=False,
        text='<b>Score<b>',
        font=dict(size=14),
    )
    fig.update_xaxes(ticklabelposition='inside')
    fig.update_layout(
        margin=dict(l=0, r=0, t=20, b=0),
    )

    return [fig, value, html.P(higher + lower)]


@app.callback(
    Output('positioned-toast', 'is_open'),
    Input('positioned-toast-toggle', 'n_clicks'),
    State('positioned-toast', 'is_open'),
)
def open_toast(n, is_open):
    if n and not is_open:
        return True
    return False


@app.callback(
    [
        Output('output', 'children'),
        Output('modal', 'is_open'),
        Output('modal', 'children'),
        Output('columns-container', 'style'),
        Output('columns-container', 'children'),
        Output('checklist-weighted', 'value'),
    ],
    [
        Input('generate-recommendations-button', 'n_clicks'),
        Input('apply-parameters-button', 'n_clicks'),
        Input('close-button', 'n_clicks'),
        Input('search-switch', 'value'),
    ],
    [
        State('output', 'children'),
        State('search-user-input', 'value'),
        State('radio-input-engine', 'value'),
        State('modal', 'is_open'),
        State('checklist-features', 'value'),
        State('checklist-weighted', 'value'),
        State('checklist-scaled', 'value'),
        State('scale-slider', 'value'),
        State('checklist-included', 'value'),
        State('checklist-excluded', 'value'),
        State('columns-container', 'style'),
        State('columns-container', 'children'),
        State('search-titles-input', 'value'),
    ],
    prevent_initial_call=True,
)
def multi_output(
    _,
    _1,
    _2,
    type_switch,
    output_content,
    search_value,
    similarity_method,
    is_open,
    columns,
    weighted,
    scaled,
    scale_slider,
    included,
    excluded,
    style,
    columns_container,
    input_values,
):
    # tracemalloc.start()

    d = dispatcher(
        type_switch,
        output_content,
        search_value,
        similarity_method,
        is_open,
        columns,
        weighted,
        scaled,
        scale_slider,
        included,
        excluded,
        style,
        columns_container,
        input_values,
    )

    # curr, peak = tracemalloc.get_traced_memory()
    # print(
    #     f'AFTER DISPATCH Current memory usage is {peak / 10**6:.2f} MB; Peak was {peak / 10**6:.2f} MB',
    # )
    # tracemalloc.stop()

    return d
