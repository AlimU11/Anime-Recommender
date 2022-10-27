import tracemalloc  # isort:skip

import numpy as np
import pandas as pd
from dash import ctx

from anime_recommender.client.AnilistClient import AnilistClient

from ..recommender import Recommender
from . import IdHolder
from .layout import (
    EXCLUDED_LISTS,
    INCLUDED_LISTS,
    alert,
    app_data,
    card,
    dbc,
    html,
    modal_body,
    user_lists,
)


def recommend_content():
    app_data.recommender = Recommender(
        app_data.client,
        app_data.storage,
        app_data.recommender_type,
        app_data.columns,
        app_data.included_lists,
        app_data.excluded_lists,
        app_data.is_weighted,
        app_data.scaled,
        app_data.scale_values,
        app_data.type_switch,
        app_data.input_values,
        app_data.language,
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


def update_app_data(
    recommender_type: str,
    columns: list,
    is_weighted: bool,
    scaled: bool,
    scale_values: list,
    included_lists: list,
    excluded_lists: list,
    type_switch: bool,
    item_values: list,
    language: str,
) -> None:
    app_data.recommender_type = recommender_type
    app_data.columns = columns
    app_data.is_weighted = True if is_weighted else False
    app_data.scaled = True if is_weighted and scaled else False
    app_data.scale_values = scale_values if is_weighted and scaled else None
    app_data.included_lists = included_lists
    app_data.excluded_lists = excluded_lists
    app_data.type_switch = type_switch
    app_data.input_values = item_values
    app_data.language = language


def close(
    type_switch,
    output_content,
    username,
    style,
    columns_container,
    is_weighted,
    item_values,
):
    return [
        output_content,
        False,
        modal_body('', ''),
        style,
        columns_container,
        is_weighted,
    ]


def apply_generate(
    type_switch,
    output_content,
    username,
    style,
    columns_container,
    is_weighted,
    item_values,
):
    # TODO refactor this function

    if (not username and not type_switch) or (not item_values and type_switch):
        return [
            output_content,
            True,
            modal_body('Empty', 'Search field is empty'),
            style,
            columns_container,
            is_weighted,
        ]

    elif (
        not app_data.client or (username and app_data.client.username != username.strip().lower())
    ) and not type_switch:
        app_data.client = AnilistClient(
            username.strip().lower(),
        )  # NOTE temporary one class # TODO change to client_dict
        app_data.included_lists = INCLUDED_LISTS
        app_data.excluded_lists = EXCLUDED_LISTS

        # elif utils.client and utils.client.username == value.strip().lower():
        #    print('Already searched')

    if type_switch or app_data.client.user_id:
        if not style:
            style = {}
        style['display'] = 'block' if not type_switch and app_data.client and app_data.client.user_id else 'none'

        return [
            recommend_content(),
            False,
            modal_body('', ''),
            style,
            user_lists(
                [{'label': i, 'value': i} for i in list(app_data.client.user_lists.keys())],
            )
            if app_data.client
            and app_data.client.user_id
            and ctx.triggered_id == IdHolder.generate_button.name  # FIXME: does the last statement correct?
            else columns_container,
            is_weighted,
        ]

    return [
        alert(
            html.Span(
                [
                    'Username not found. Are you sure that ',
                    html.A(
                        f'https://anilist.co/user/{username}/',
                        href=f'https://anilist.co/user/{username}/',
                        target='_blank',
                        className='alert-link',
                        style={'text-underline-position': 'under'},
                    ),
                    ' is exist?',
                ],
            ),
        ),
        False,
        modal_body('', ''),
        style,
        columns_container,
        is_weighted,
    ]


def switch_view(
    type_switch,
    output_content,
    username,
    style,
    columns_container,
    is_weighted,
    item_values,
):
    return [
        output_content,
        False,
        modal_body('', ''),
        {'display': 'block'}
        if not type_switch and app_data.client and app_data.client.user_id
        else {'display': 'none'},
        columns_container,
        is_weighted,
    ]


trigger_id = {
    IdHolder.close_button.name: close,
    IdHolder.generate_button.name: apply_generate,
    IdHolder.apply_button.name: apply_generate,
    IdHolder.search_type_switch.name: switch_view,
}


def dispatcher(
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
    update_app_data(
        recommender_type,
        columns,
        is_weighted,
        scaled,
        scale_slider,
        included,
        excluded,
        type_switch,
        item_values,
        language,
    )

    return trigger_id[ctx.triggered_id](
        type_switch,
        output_content,
        username,
        style,
        columns_container,
        is_weighted,
        item_values,
    )
