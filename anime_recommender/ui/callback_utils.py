import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import ctx, no_update
from sklearn.preprocessing import MinMaxScaler, minmax_scale

from anime_recommender.client.AnilistClient import AnilistClient

from ..recommender import Recommender
from .layout import EXCLUDED_LISTS, INCLUDED_LISTS, alert, app_data, card, dbc, html
from .utils.dcw import callback_manager as cm
from .utils.IdHolder import IdHolder as ID


def recommend_content():
    app_data.recommender = Recommender(
        app_data.client,
        app_data.storage,
        app_data.recommender_type,
        app_data.features_list,
        app_data.included_lists,
        app_data.excluded_lists,
        app_data.is_weighted,
        app_data.is_scaled,
        app_data.scale_slider,
        app_data.search_type_switch,
        app_data.item_searchbar,
    )

    app_data.df = pd.merge(
        pd.DataFrame(app_data.recommender.recommend(), columns=['id', 'proba']),
        app_data.storage.info,
        how='left',
        left_on='id',
        right_on='id',
    )

    df = app_data.df.iloc[:20]  # TODO replace

    pd.options.mode.chained_assignment = None

    df.loc[:, 'id'] = df.id.astype(int)
    df.loc[:, 'description'] = df.description.apply(
        lambda x: app_data.text_processor(x).remove_html_tags(),
    )

    pd.options.mode.chained_assignment = 'warn'
    cards = df.sort_values(by='proba', ascending=False).apply(card, axis=1).tolist()

    return dbc.Row(cards, justify='evenly', align='center', className='mt-5')


def update_app_data() -> None:
    app_data.search_type_switch = cm.search_type_switch.value
    app_data.output_container = cm.output_container.children
    app_data.username_searchbar = cm.username_searchbar.value
    app_data.item_searchbar = cm.item_searchbar.value
    app_data.recommender_type = cm.recommender_type.value
    app_data.modal_notification = cm.modal_notification.is_open
    app_data.features_list = cm.features_list.value
    app_data.is_weighted = True if cm.is_weighted.value else False
    app_data.is_scaled = True if cm.is_weighted.value and cm.is_scaled.value else False
    app_data.scale_slider = cm.scale_slider.value if cm.is_weighted.value and cm.is_scaled.value else None
    # NOTE: possible overlap with initialization in get_recommendations()
    app_data.included_lists = cm.included_list.value
    app_data.excluded_lists = cm.excluded_list.value
    app_data.user_lists_style = cm.user_lists.style
    app_data.user_lists = cm.user_lists.children
    app_data.language = cm.titles_language.label


def get_recommendations():
    is_username_searchbar_active = not app_data.search_type_switch

    is_username_searchbar_active_and_empty = not app_data.username_searchbar and is_username_searchbar_active

    is_item_searchbar_active_and_empty = not app_data.item_searchbar and not is_username_searchbar_active

    if is_username_searchbar_active_and_empty or is_item_searchbar_active_and_empty:
        return no_update, 0, no_update

    is_client_not_present = not app_data.client
    is_client_present_but_username_not_match = (
        app_data.client
        and getattr(app_data.client, 'username') != (getattr(app_data, 'username_searchbar', '') or '').strip().lower()
    )

    if is_client_not_present or is_client_present_but_username_not_match:
        # NOTE: possibly change to IClient?
        app_data.client = AnilistClient(
            (getattr(app_data, 'username_searchbar', '') or '').strip().lower(),
        )

        app_data.included_lists = INCLUDED_LISTS
        app_data.excluded_lists = EXCLUDED_LISTS

    if not is_username_searchbar_active or getattr(app_data.client, 'user_id'):
        if not app_data.user_lists_style:
            app_data.user_lists_style = {}

        app_data.user_lists_style['display'] = (
            'block'
            if not is_username_searchbar_active and app_data.client and getattr(app_data.client, 'user_id')
            else 'none'
        )

        return recommend_content(), no_update, 0

    return alert(), no_update, no_update


def plot_scaled_unscaled_scores_diff():
    normal_scores = np.array(
        [i for i in minmax_scale(np.arange(1, 11), feature_range=(1, 10))],
    )
    index = np.arange(1, 11)
    value = [-5, 4] if ctx.triggered_id == ID.reset_graph_button else cm.scale_slider.value

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
        font=dict(size=14),
    )

    return [fig, value, html.P(higher + lower)]
