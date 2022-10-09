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

    df = app_data.recommender.recommend()

    # curr, peak = tracemalloc.get_traced_memory()
    # print(f'AFTER RECOMMEND Current memory usage is {curr / 10 ** 6:.2f}MB; Peak was {peak / 10**6:.2f} MB')

    app_data.recommender = None

    if df.empty:
        return alert(
            '''No titles found to include in calculations. By default, included lists are [Completed]. Ensure that chosen lists are not empty or try to choose lists manually''',
        )

    # media content memoization
    # implemented in order to reduce the load on api

    cols = app_data.df.columns
    shared_index = np.intersect1d(app_data.df['index'].values, df['index'].values)

    if len(shared_index) > 0:
        no_media_update_df = df[df['index'].isin(shared_index)].sort_values(by='index')
        no_media_update_utils = app_data.df[app_data.df['index'].isin(shared_index)].sort_values(by='index')[
            ['cover_image', 'color', 'description', 'title']
        ]
        df = df[~df['index'].isin(shared_index)]
        app_data.df = app_data.df[~app_data.df['index'].isin(shared_index)]

        no_media_update_df.index = np.arange(len(no_media_update_df))
        no_media_update_utils.index = np.arange(len(no_media_update_utils))
        df.index = np.arange(len(df))
        app_data.df.index = np.arange(len(app_data.df))

        no_media_update = pd.concat([no_media_update_df, no_media_update_utils], axis=1, ignore_index=True)
        no_media_update.columns = cols

    else:
        no_media_update = pd.DataFrame(columns=cols)

    # tmp = pd.DataFrame(df['index'].apply(AnilistClient.get_media_info).tolist())
    # print(df)
    # print(tmp)
    # print('DF SHAPE: ', df.shape)
    # print('TMP SHAPE: ', tmp.shape)

    df = pd.merge(
        df,
        pd.DataFrame(
            AnilistClient.get_media_info(df['index'].values.tolist())
            if len(df)
            else pd.DataFrame(columns=['cover_image', 'color', 'description', 'title']),
        ),
        left_index=True,
        right_index=True,
        how='outer',
    )

    # print(df)

    if 'description' in df.columns:
        df.description = df.description.apply(lambda x: app_data.text_processor(x).remove_html_tags())

    # print(df)

    df = pd.concat([df, no_media_update], axis=0, ignore_index=True)
    df.columns = cols
    app_data.df = pd.concat([app_data.df, df], axis=0, ignore_index=True)
    app_data.df.columns = cols

    # print(df)

    # curr, peak = tracemalloc.get_traced_memory()
    # print(f'BEFORE CARDS Current memory usage is {curr / 10 ** 6:.2f}MB; Peak was {peak / 10**6:.2f} MB')

    cards = df.sort_values(by='proba', ascending=False).apply(card, axis=1).tolist()

    # curr, peak = tracemalloc.get_traced_memory()
    # print(f'AFTER CARDS Current memory usage is {curr / 10 ** 6:.2f}MB; Peak was {peak / 10**6:.2f} MB')

    return dbc.Row(cards, justify='evenly', align='center', className='mt-5')

    # dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)


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

    elif (not app_data.client or app_data.client.username != search_value.strip().lower()) and not type_switch:
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
