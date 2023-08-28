"""Scaled plot module."""

import numpy as np
from dash import ctx, html
from dash.development.base_component import Component
from plotly import graph_objects as go
from sklearn.preprocessing import MinMaxScaler, minmax_scale

from anime_recommender.ui.ui_utils.dcw import callback_manager as cm
from anime_recommender.ui.ui_utils.id_holder import IdHolder as ID


def sigmoid(score: int) -> float:
    """Sigmoid function.

    Parameters
    ----------
    score : int
        Input value.

    Returns
    -------
    float
        Sigmoid value.
    """
    return 1 / (1 + np.exp(-score))


def plot_scaled_unscaled_scores_diff() -> tuple[go.Figure, list[int], Component]:  # noqa: WPS210
    """Plot scaled and unscaled scores difference.

    Returns
    -------
    tuple[Figure, list[int], Component]
        Plot, scale slider value, and description about difference between scaled and unscaled scores.

    """
    normal_scores = np.array(
        minmax_scale(np.arange(1, 11), feature_range=(1, 10)),
    )
    index = np.arange(1, 11)
    is_reset_button_triggered = ctx.triggered_id == ID.reset_graph_button
    slider_values = [-5, 4] if is_reset_button_triggered else cm.scale_slider.value

    score_range = np.arange(1, 11).reshape(-1, 1)
    mm = MinMaxScaler(feature_range=(slider_values[0], slider_values[1]))
    mm.fit(score_range)

    scaled_scores = minmax_scale(
        np.array(
            [sigmoid(score) for score in mm.transform(score_range)],
        ).flatten(),
        feature_range=(1, 10),
    )

    # min and max values will be always 1 and 10
    scaled_subscores = scaled_scores[1:-1]
    normal_subscores = normal_scores[1:-1]
    mask = scaled_subscores >= normal_subscores
    are_scaled_scores_higher = np.argwhere(mask)
    has_true_values = are_scaled_scores_higher.shape[0] > 0
    score_value = normal_scores[are_scaled_scores_higher[0]][0] if has_true_values else 10

    lower = (
        ['']
        if score_value == 1
        else [
            html.Br(),
            'All titles with scores ',
            html.B(
                'below {score}'.format(
                    score=score_value if score_value == 10 else score_value + 1,
                ),
            ),
            ' will have ',
            html.B('less'),
            ' impact.',
        ]
    )

    higher = (
        ['']
        if score_value == 10
        else [
            'All titles with scores ',
            html.B('higher than {score_value}'.format(score_value=score_value)),
            ' will have ',
            html.B('more'),
            ' impact.',
        ]
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
        legend={
            'yanchor': 'top',
            'y': -0.05,
            'xanchor': 'left',
            'x': 0,
            'bgcolor': 'rgba(0,0,0,0)',
            'orientation': 'h',
        },
        margin={'l': 0, 'r': 0, 't': 20, 'b': 0},
        dragmode=False,
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
        font={'size': 14},
    )

    return fig, slider_values, html.P(higher + lower)
