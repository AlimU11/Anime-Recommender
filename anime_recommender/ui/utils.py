import tracemalloc  # isort:skip

import numpy as np
import pandas as pd
from dash import ctx

from anime_recommender.client.AnilistClient import AnilistClient

from ..recommender import Recommender
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
        app_data.similarity_method,
        app_data.columns,
        app_data.included_lists,
        app_data.excluded_lists,
        app_data.weighted,
        app_data.scaled,
        app_data.scale_values,
        app_data.type_switch,
        app_data.input_values,
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
    df.loc[:, 'description'] = df.description.apply(lambda x: app_data.text_processor(x).remove_html_tags())
    pd.options.mode.chained_assignment = 'warn'

    cards = df.sort_values(by='proba', ascending=False).apply(card, axis=1).tolist()

    return dbc.Row(cards, justify='evenly', align='center', className='mt-5')


def update_app_data(
    similarity_method: str,
    columns: list,
    weighted: bool,
    scaled: bool,
    scale_values: list,
    included_lists: list,
    excluded_lists: list,
    type_switch: bool,
    input_values: list,
) -> None:
    app_data.similarity_method = similarity_method
    app_data.columns = columns
    app_data.weighted = True if weighted else False
    app_data.scaled = True if weighted and scaled else False
    app_data.scale_values = scale_values if weighted and scaled else None
    app_data.included_lists = included_lists
    app_data.excluded_lists = excluded_lists
    app_data.type_switch = type_switch
    app_data.input_values = input_values


def close(
    type_switch,
    output_content,
    search_value,
    style,
    columns_container,
    weighted,
    input_values,
):
    return [
        output_content,
        False,
        modal_body('', ''),
        style,
        columns_container,
        weighted,
    ]


def apply_generate(
    type_switch,
    output_content,
    search_value,
    style,
    columns_container,
    weighted,
    input_values,
):
    # TODO refactor this function

    if (not search_value and not type_switch) or (not input_values and type_switch):
        return [
            output_content,
            True,
            modal_body('Empty', 'Search field is empty'),
            style,
            columns_container,
            weighted,
        ]

    elif (
        not app_data.client or (search_value and app_data.client.username != search_value.strip().lower())
    ) and not type_switch:
        app_data.client = AnilistClient(
            search_value.strip().lower(),
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
            user_lists([{'label': i, 'value': i} for i in list(app_data.client.user_lists.keys())])
            if app_data.client and app_data.client.user_id and ctx.triggered_id == 'generate-recommendations-button'
            else columns_container,
            weighted,
        ]

    return [
        alert(
            html.Span(
                [
                    'Username not found. Are you sure that ',
                    html.A(
                        f'https://anilist.co/user/{search_value}/',
                        href=f'https://anilist.co/user/{search_value}/',
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
        weighted,
    ]


def switch_view(
    type_switch,
    output_content,
    search_value,
    style,
    columns_container,
    weighted,
    input_values,
):
    return [
        output_content,
        False,
        modal_body('', ''),
        {'display': 'block'}
        if not type_switch and app_data.client and app_data.client.user_id
        else {'display': 'none'},
        columns_container,
        weighted,
    ]


trigger_id = {
    'close-button': close,
    'generate-recommendations-button': apply_generate,
    'apply-parameters-button': apply_generate,
    'search-switch': switch_view,
}


def dispatcher(
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
    update_app_data(
        similarity_method,
        columns,
        weighted,
        scaled,
        scale_slider,
        included,
        excluded,
        type_switch,
        input_values,
    )

    return trigger_id[ctx.triggered_id](
        type_switch,
        output_content,
        search_value,
        style,
        columns_container,
        weighted,
        input_values,
    )
