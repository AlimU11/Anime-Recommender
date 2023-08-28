"""Dynamic components for layout."""

import dash_bootstrap_components as dbc
import pandas as pd
from dash import html
from dash.development.base_component import Component

from anime_recommender.ui.app_data import app_data
from anime_recommender.ui.constants import (
    TITLE_DISPLAY_LENGTH,
    TITLE_NATIVE_DISPLAY_LENGTH,
    USER_EXCLUDED_LISTS,
    USER_INCLUDED_LISTS,
)
from anime_recommender.ui.ui_utils.id_holder import IdHolder as ID
from anime_recommender.ui.ui_utils.user_interface_en import UserInterfaceEN as UI


def alert_features():
    """Create alert notification in features tab.

    Returns
    -------
    Component
        Alert notification.
    """
    return dbc.Alert(
        [
            html.I(className='bi bi-info-circle-fill me-2'),
            UI.feature_selection_aleart,
        ],
        color='info',
        className='d-flex align-items-center feature-alert',
    )


def tooltip(text, link_id, placement='auto'):
    """Create tooltip for titles in cards.

    Parameters
    ----------
    text : str
        Text to display in tooltip.

    link_id : dict
        Id of link to create tooltip for with the same index.

    placement : str, optional
        Placement of tooltip. Default is "auto".

    Returns
    -------
    Component
        Tooltip for titles in cards.
    """
    return dbc.Tooltip(
        text,
        id={'type': 'tooltip-title', 'index': link_id['index']},
        target=link_id,
        autohide=False,
        placement=placement,
    )


def alert():
    """Create alert notification in output container.

    Returns
    -------
    Component
        Alert notification.
    """
    link = 'https://anilist.co/user/{username}/'.format(username=app_data.ui_state.username_searchbar)

    return dbc.Alert(
        [
            html.I(className='bi bi-exclamation-triangle-fill'),
            html.Span(
                [
                    UI.not_found_alert_text_start,
                    html.A(link, href=link, target='_blank', className='alert-link'),
                    UI.not_found_alert_text_end,
                ],
            ),
        ],
        color='danger',
        id=ID.not_found_alert,
    )


def option_template(options: list[int], language: str = 'english') -> list[dict]:
    """Return list of options for dropdown menu.

    Parameters
    ----------
    options : list[int]
        List of title ids.

    language : str
        Language of titles. Default is "english".

    Returns
    -------
    list[dict]
        List of options for dropdown menu.
    """
    return [
        {
            'label': html.Div(
                [
                    html.Div(
                        style={
                            'background-color': row.color,
                            'background-image': 'url({img})'.format(img=row.img_small),
                        },
                        className='dropdown-image',
                    ),
                    html.Div(
                        [
                            html.Span(
                                (
                                    row.english
                                    if language == 'english'
                                    else row.romaji
                                    if language == 'romaji'
                                    else row.native
                                ),
                                className='dropdown-title',
                            ),
                            html.Div([row.startDate_year, ' ', row.format], className='dropdown-info'),
                        ],
                        className='dropdown-text-container',
                    ),
                ],
                className='dropdown-item',
            ),
            'value': row.id,
            'search': (
                row.english if language == 'english' else row.romaji if language == 'romaji' else row.native
            ).lower(),
        }
        for row in app_data.by_popularity.query('id in @options').itertuples()
    ]


def card(title: pd.Series) -> Component:
    """Create html card with information about title.

    Parameters
    ----------
    title : pd.Series
        Series with information about title.

    Returns
    -------
    Component
        HTML card with information about title.
    """
    title_len = TITLE_NATIVE_DISPLAY_LENGTH if app_data.ui_state.language == 'native' else TITLE_DISPLAY_LENGTH

    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.Div(
                        html.Div(
                            '{proba:.0%}'.format(proba=title.proba),
                            style={'color': '{color}'.format(color='white' if title.color else 'black')},
                            className='probability-score',
                        ),
                        style={'background-color': '{color}'.format(color=title.color if title.color else 'white')},
                        className='probability-container',
                    ),
                    html.Div(
                        [
                            html.Div(
                                style={
                                    'background-color': '{color}'.format(color=title.color if title.color else 'white'),
                                    'background-image': 'url({img})'.format(img=title.img_small),
                                },
                                className='card-image-small',
                            ),
                            html.Div(
                                style={'background-image': 'url({img})'.format(img=title.img_large)},
                                className='card-image-large',
                            ),
                            html.Div(
                                [
                                    html.Span(
                                        '{score:.1f}{placeholder}'.format(
                                            score=title.meanScore * 10,
                                            placeholder='' if title.meanScore else 'N/A',
                                        ),
                                        style={'margin-right': '0.25rem'},
                                    ),
                                    html.I(className='bi bi-star-fill'),
                                ],
                                style={
                                    'background-color': '{color}'.format(color=title.color if title.color else 'white'),
                                    'color': '{color}'.format(color='white' if title.color else 'black'),
                                },
                                className='card-rating-container',
                            ),
                        ],
                        className='card-image-container',
                    ),
                    html.Div(
                        [
                            html.H6(
                                html.A(
                                    '{title}{ellipsis}'.format(
                                        title=title[app_data.ui_state.language][:title_len],
                                        ellipsis='...' if len(title[app_data.ui_state.language]) > title_len else '',
                                    ),
                                    href='https://anilist.co/anime/{href}'.format(href=int(title['id'])),
                                    target='_blank',
                                    style={'color': '{color}'.format(color=title.color if title.color else 'black')},
                                    id={'type': 'link-title', 'index': int(title['id'])},
                                    className='card-title',
                                ),
                                style={'margin': '0', 'display': 'inline-block'},
                            ),
                            html.P(
                                '{year} {format}'.format(year=int(title.startDate_year), format=title.format),
                                style={
                                    'margin': '0',
                                    'color': '{color}'.format(color=title.color if title.color else 'black'),
                                    'font-size': '0.8rem',
                                    'margin-top': '-0.25rem',
                                },
                            ),
                            html.P('{description}'.format(description=title.description), className='card-description'),
                        ],
                        className='mt-auto card-text-container',
                    ),
                    tooltip(
                        title[app_data.ui_state.language],
                        {'type': 'link-title', 'index': int(title['id'])},
                        'top',
                    ),
                    # if len(title[app_data.ui_state.language]) > title_len
                    # else "",
                    html.A(
                        className='stretched-link',
                        href='https://anilist.co/anime/{title_id}'.format(title_id=int(title['id'])),
                        target='_blank',
                    ),
                ],
                className='flex-column d-flex content-card',
            ),
        ],
    )


def modal_body(header: str, text: str) -> list[Component]:
    """Create modal notification.

    Parameters
    ----------
    header : str
        Modal header.

    text : str
        Modal text.

    Returns
    -------
    list[Component]
        Modal notification.
    """
    return [
        dbc.ModalHeader(dbc.ModalTitle(header)),
        dbc.ModalBody(text),
        dbc.ModalFooter(
            dbc.Button(
                UI.button_close,
                id=ID.close_button,
                className='ms-auto',
                n_clicks=0,
            ),
        ),
    ]


def user_lists(lists: list[dict[str, str]]) -> list[Component]:
    """Create user lists section in parameters tab.

    Parameters
    ----------
    lists : list[dict[str, str]]
        List of user lists. Each list is a dictionary with keys `label` and `value`.

    Returns
    -------
    list[Component]
        User lists section.
    """
    return [
        html.P(UI.title_user_lists, className='title-mobile'),
        html.I(
            [
                UI.user_lists_desc1,
                html.B(UI.user_lists_desc2),
                UI.user_lists_desc3,
                html.B(UI.user_lists_desc4),
                UI.user_lists_desc5,
            ],
            className='user-lists-description',
        ),
        html.H5(UI.included_list_title),
        dbc.Checklist(
            options=lists,
            value=USER_INCLUDED_LISTS,
            id=ID.included_list,
        ),
        html.H5(UI.excluded_list_title),
        dbc.Checklist(
            options=lists,
            value=USER_EXCLUDED_LISTS,
            id=ID.excluded_list,
        ),
    ]
