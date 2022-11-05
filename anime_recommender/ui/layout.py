import os

import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc, html

from ..storage import LocalStorage
from . import AppData, IdHolder

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
    title='Anime Recommender',
    assets_folder=os.getcwd() + '/assets',
)

app_data = AppData()
app_data.storage = LocalStorage()

RESULT_AMOUNT = int(os.environ.get('RESULT_AMOUNT'))

INCLUDED_LISTS = ['Completed']
EXCLUDED_LISTS = ['Dropped', 'Watching', 'Rewatching', 'Planning', 'Paused']

app_data.storage.info.sort_values(by='popularity', ascending=False, inplace=True)

ITEMS_ENG = [
    {
        'label': html.Div(
            [
                html.Div(
                    style={
                        'background-color': color,
                        'background-image': f'url({img_small})',
                    },
                    className='dropdown-image',
                ),
                html.Div(
                    [
                        html.Span(english, className='dropdown-title'),
                        html.Div(
                            [startDate_year, ' ', format],
                            className='dropdown-info',
                        ),
                    ],
                    className='dropdown-text-container',
                ),
            ],
            className='dropdown-item',
        ),
        'value': id,
        'search': english.lower(),
    }
    for english, id, img_small, color, startDate_year, format in zip(
        app_data.storage.info.english.values,
        app_data.storage.info.id.values,
        app_data.storage.info.img_small.values,
        app_data.storage.info.color.values,
        app_data.storage.info.startDate_year.values,
        app_data.storage.info.format.values,
    )
]

ITEMS_ROMAJI = [
    {
        'label': html.Div(
            [
                html.Div(
                    style={
                        'background-color': color,
                        'background-image': f'url({img_small})',
                    },
                    className='dropdown-image',
                ),
                html.Div(
                    [
                        html.Span(romaji, className='dropdown-title'),
                        html.Div(
                            [startDate_year, ' ', format],
                            className='dropdown-info',
                        ),
                    ],
                    className='dropdown-text-container',
                ),
            ],
            className='dropdown-item',
        ),
        'value': id,
        'search': romaji.lower(),
    }
    for romaji, id, img_small, color, startDate_year, format in zip(
        app_data.storage.info.romaji.values,
        app_data.storage.info.id.values,
        app_data.storage.info.img_small.values,
        app_data.storage.info.color.values,
        app_data.storage.info.startDate_year.values,
        app_data.storage.info.format.values,
    )
]

ITEMS_NATIVE = [
    {
        'label': html.Div(
            [
                html.Div(
                    style={
                        'background-color': color,
                        'background-image': f'url({img_small})',
                    },
                    className='dropdown-image',
                ),
                html.Div(
                    [
                        html.Span(native, className='dropdown-title'),
                        html.Div(
                            [startDate_year, ' ', format],
                            className='dropdown-info',
                        ),
                    ],
                    className='dropdown-text-container',
                ),
            ],
            className='dropdown-item',
        ),
        'value': id,
        'search': native.lower(),
    }
    for native, id, img_small, color, startDate_year, format in zip(
        app_data.storage.info.native.values,
        app_data.storage.info.id.values,
        app_data.storage.info.img_small.values,
        app_data.storage.info.color.values,
        app_data.storage.info.startDate_year.values,
        app_data.storage.info.format.values,
    )
]

app_data.storage.info.sort_values(by='id', ascending=True, inplace=True)

language_options_username = [
    dbc.DropdownMenuItem('english', id=IdHolder.english_username.name),
    dbc.DropdownMenuItem('romaji', id=IdHolder.romaji_username.name),
    dbc.DropdownMenuItem('native', id=IdHolder.native_username.name),
]

language_options_titles = [
    dbc.DropdownMenuItem('english', id=IdHolder.english.name),
    dbc.DropdownMenuItem('romaji', id=IdHolder.romaji.name),
    dbc.DropdownMenuItem('native', id=IdHolder.native.name),
]

source_options = [
    dbc.DropdownMenuItem('Anilist', id=IdHolder.Anilist.name),
]

########################################################################################################################
#                                                Dynamic content                                                       #
########################################################################################################################

tooltip = lambda text, id, placement='auto': dbc.Tooltip(
    text,
    target=id,
    autohide=False,
    placement=placement,
)

question_mark = lambda id: html.Sup(
    [
        html.I(className='bi bi-question-circle-fill', style={'font-weight': 'bold'}),
    ],
    style={
        'margin-left': '5px',
        'font-size': '1rem',
        'vertical-align': 'top',
        'position': 'relative',
        'top': '-55px',
        'left': '15vw',
        'cursor': 'pointer',
        'z-index': '1000',
    },
    id=id,
)

alert = lambda text: dbc.Alert(
    [
        html.I(
            className='bi bi-exclamation-triangle-fill',
            style={'font-size': '16px', 'font-weight': 'bold', 'margin-right': '10px'},
        ),
        text,
    ],
    color='danger',
    style={'height': 'fit-content', 'margin-top': '0rem'},
)


def card(s):
    title_len = 24 if app_data.language != 'native' else 18

    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.Div(
                        html.Div(
                            f'{s.proba:.0%}',
                            style={
                                'color': f'''{'white' if s.color else 'black'}''',
                            },
                            className='probability-score',
                        ),
                        style={
                            'background-color': f'''{s.color if s.color else 'white'}''',
                        },
                        className='probability-container',
                    ),
                    html.Div(
                        [
                            html.Div(
                                style={
                                    'background-color': f'{s.color if s.color else "white"}',
                                    'background-image': f'url({s.img_small})',
                                },
                                className='card-image-small',
                            ),
                            html.Div(
                                style={
                                    'background-image': f'url({s.img_large})',
                                },
                                className='card-image-large',
                            ),
                        ],
                        className='card-image-container',
                    ),
                    html.Div(
                        [
                            html.H6(
                                html.A(
                                    f'''{s[app_data.language][:title_len]}{'...' if len(s[app_data.language]) > title_len else ''}''',
                                    href=f'''https://anilist.co/anime/{s['id']}''',
                                    target='_blank',
                                    style={
                                        'color': f'''{s.color if s.color else 'black'}''',
                                    },
                                    id=f'''tooltip-title-{s['id']}''',
                                    className='card-title',
                                ),
                            ),
                            html.P(
                                f'{s.description}',
                                className='card-description',
                            ),
                        ],
                        className='mt-auto card-text-container',
                    ),
                    tooltip(s[app_data.language], f'''tooltip-title-{s['id']}''', 'top')
                    if len(s[app_data.language]) > title_len
                    else '',
                    html.A(
                        className='stretched-link',
                        href=f'''https://anilist.co/anime/{s['id']}''',
                        target='_blank',
                    ),
                ],
                className='flex-column d-flex content-card',
            ),
        ],
    )


modal_body = lambda header, text: [
    dbc.ModalHeader(dbc.ModalTitle(header)),
    dbc.ModalBody(text),
    dbc.ModalFooter(
        dbc.Button(
            'Close',
            id=IdHolder.close_button.name,
            className='ms-auto',
            n_clicks=0,
        ),
    ),
]

user_lists = lambda lists: [
    html.I(
        [
            'User lists to include or exclude from recommendations. Entries from ',
            html.B('Included'),
            ' take part in calculation recommendations. Entries from ',
            html.B('Excluded'),
            ' do not participate in calculation, but simply excluded from recommendation results. ',
        ],
        style={'margin': '1rem 0', 'display': 'inline-block'},
    ),
    html.H5('Included:'),
    dbc.Checklist(
        options=lists,
        value=INCLUDED_LISTS,
        id=IdHolder.included_list.name,
    ),
    html.H5('Excluded:'),
    dbc.Checklist(
        options=lists,
        value=EXCLUDED_LISTS,
        id=IdHolder.excluded_list.name,
    ),
]

alert_features = dbc.Alert(
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

########################################################################################################################
#                                                  Main layout                                                         #
########################################################################################################################

search_type_switch = dbc.Col(
    [
        dbc.Switch(
            id=IdHolder.search_type_switch.name,
            label='By username',
            value=False,
        ),
        # html.Div("By username")
    ],
    align='top',
    width=2,
    style={'width': '170px'},
)

search_input = dbc.Col(
    [
        dbc.InputGroup(
            [
                dbc.DropdownMenu(
                    source_options,
                    label=f'Anilist',
                    id=IdHolder.username_source.name,
                ),  # TODO: add more sources
                dbc.InputGroupText('@'),
                dbc.Input(
                    placeholder='Username',
                    id=IdHolder.username_searchbar.name,
                    type='text',
                ),
                dbc.DropdownMenu(
                    language_options_username,
                    label='english',
                    id=IdHolder.titles_language_username.name,
                ),
            ],
            style={'height': '100%', 'margin': '0px'},
        ),
    ],
    style={'background-f': 'white', 'margin-left': '2rem'},
    id=IdHolder.username_searchbar_container.name,
    align='center',
)

search_input1 = dbc.Col(
    [
        dbc.ListGroup(
            [
                dcc.Dropdown(
                    ITEMS_ENG[:RESULT_AMOUNT],
                    placeholder='Type to search',
                    multi=True,
                    id=IdHolder.item_searchbar.name,
                    style={'width': '100%'},
                    maxHeight=400,
                    optionHeight=65,
                ),
                dbc.DropdownMenu(
                    language_options_titles,
                    label='english',
                    id=IdHolder.titles_language_titles.name,
                ),
            ],
            className='list-group-horizontal',
        ),
    ],
    style={'background-color': 'white', 'margin-left': '2rem', 'display': 'none'},
    id=IdHolder.item_searchbar_container.name,
)

generate_button = dbc.Col(
    dbc.Button(
        'Generate',
        color='primary',
        id=IdHolder.generate_button.name,
    ),
    width=2,
    style={'background-color': 'white'},
)

searchbar = dbc.Row(
    [
        dbc.Col(
            dbc.Row(
                [
                    search_type_switch,
                    search_input,
                    search_input1,
                ],
            ),
        ),
        generate_button,
    ],
    style={'background-color': 'white', 'min-height': '100px'},
)

output_container = dbc.Row(
    [
        dbc.Spinner(
            dbc.Col(
                [],
                id=IdHolder.output_container.name,
            ),
        ),
    ],
    style={'background-color': 'white', 'height': 'fit-content'},
)

main = dbc.Col(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    html.H2('Anime Recommender', style={'margin-bottom': '2rem'}),
                    searchbar,
                    output_container,
                ],
            ),
            style={
                'background-color': 'white',
                'height': '100%',
                #'overflow-y': 'auto',
            },
        ),
    ],
    width=8,
    style={'background-color': 'white', 'height': '100%'},
)

########################################################################################################################
#                                                  Parameters                                                          #
########################################################################################################################

header = dbc.Row(
    [
        html.H2(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                'Parameters',
                            ],
                            align='left',
                        ),
                        dbc.Col(
                            [
                                html.I(
                                    className='bi bi-sliders2',
                                    style={'font-weight': 'bold'},
                                ),
                            ],
                            align='right',
                            width=2,
                        ),
                    ],
                ),
            ],
        ),
    ],
)

recommender_type = dbc.AccordionItem(
    [
        html.P(
            html.I(
                'Recommendation engine stands for the algorithm used to generate recommendations. Standard (linear kernel) is the default engine and works good for most cases. Experimental (rbf kernel) is awful for large number of titles, but can give some interesting results for individual one(s).',
            ),
            style={'margin-bottom': '1rem'},
        ),
        dbc.RadioItems(
            options=[
                {'label': 'Standard', 'value': 'linear_kernel'},
                {'label': 'Experimental', 'value': 'rbf_kernel'},
            ],
            value='linear_kernel',
            id=IdHolder.recommender_type.name,
            style={'cursor': 'pointer'},
        ),
    ],
    title='Recommendation Engine',
)

user_lists_container = dbc.AccordionItem(
    user_lists([]),
    title='User Lists',
    id=IdHolder.user_lists.name,
    className='user-lists-container',
)

feature_options = [
    {'label': 'Tags', 'value': 'tags', 'disabled': True},
    {'label': 'Genres', 'value': 'genres'},
    {'label': 'Average Score', 'value': 'mean_score'},
    {'label': 'Format', 'value': 'format'},
    {'label': 'Number of Episodes', 'value': 'episodes'},
    {'label': 'Duration', 'value': 'duration'},
    {'label': 'Source', 'value': 'source'},
    {'label': 'Origin', 'value': 'countryOfOrigin'},
    {'label': 'Season', 'value': 'season'},
    {'label': 'Is Adult', 'value': 'isAdult'},
    {'label': 'Favorites', 'value': 'favorites'},
    {'label': 'Popularity', 'value': 'popularity'},
    # TODO add description and dates
    {'label': 'Studios', 'value': 'studios'},
    {'label': 'Producers', 'value': 'producers'},
]

weighted_options = [
    {'label': 'Include scores', 'value': True},
]

scaled_options = [
    {'label': 'Scale scores', 'value': True},
]

included_features = dbc.AccordionItem(
    [
        html.P(
            html.I(
                'Each title has individual features that make it unique and distinguish from others. Those features could be included in calculation and potentially affect recommendation results. The further information about each feature is presented below.',
            ),
            style={'margin-bottom': '1rem'},
        ),
        dbc.Accordion(
            dbc.AccordionItem(
                [
                    html.Ol(
                        [
                            html.Li(
                                'Tags: list of tags that title belongs to with their respective scores.',
                            ),
                            html.Li('Genres: list of genres that title belongs to.'),
                            html.Li('Average Score: average score of title.'),
                            html.Li('Format: format of title (TV, Movie, etc...).'),
                            html.Li('Number of Episodes: number of episodes in title.'),
                            html.Li('Duration: duration of each episode in minutes.'),
                            html.Li(
                                'Source: source of title (Manga, Light Novel, etc...).',
                            ),
                            html.Li('Origin: origin of title (Japan, China, etc...).'),
                            html.Li(
                                'Season: season of release (Winter, Spring, etc...).',
                            ),
                            html.Li('Is Adult: whether title is adult or not.'),
                            html.Li(
                                'Favorites: number of users that added title to their favorites.',
                            ),
                            html.Li('Popularity: AniList popularity score.'),
                            html.Li('Studios: list of studios that worked on title.'),
                            html.Li(
                                'Producers: list of producers that worked on title.',
                            ),
                        ],
                    ),
                ],
                title='Feature description',
                class_name='feature-description',
            ),
            start_collapsed=True,
        ),
        html.Div([], id=IdHolder.features_alert.name),
        dbc.Checklist(
            options=feature_options,
            value=['tags'],
            id=IdHolder.features_list.name,
            style={'cursor': 'pointer'},
        ),
    ],
    title='Included Features',
)

weighted_container = dbc.Container(
    [
        html.H5(
            [
                'Weighted',
            ],
        ),
        html.I(
            'Whether to include user scores in calculation or not. Each score applies as a coefficient to the corresponding title that user watched.',
            style={'margin': '0.5rem 0', 'display': 'inline-block'},
        ),
        dbc.Checklist(
            options=weighted_options,
            value=[True],
            id=IdHolder.is_weighted.name,
            style={'cursor': 'pointer'},
        ),
    ],
    id=IdHolder.weighted_container.name,
)

scaled_container = dbc.Container(
    [
        html.H5(
            [
                'Scaled',
            ],
        ),
        html.I(
            [
                'While usual scores make a linear effect on the results,',
                html.Br(),
                html.Span(
                    '(e.g. if two titles have the same recommendation result but the first has score 5 and the second score 10, the latter will be two times more significant)',
                    style={'margin': '0.5rem 0', 'display': 'inline-block'},
                ),
                html.Br(),
                'scaled ones introduces intuitively more logical approach — titles with scores from 2 to 5 are probably not much better (or not much different) compared to ones with 1 scores. And vice versa, for scores from 7 to 10.',
            ],
            style={'margin-bottom': '1rem', 'display': 'inline-block'},
        ),
        dbc.Checklist(
            options=scaled_options,
            value=[],
            id=IdHolder.is_scaled.name,
            style={'cursor': 'pointer'},
        ),
    ],
    id=IdHolder.scaled_container.name,
)

score_container = dbc.AccordionItem(
    [
        weighted_container,
        scaled_container,
        dbc.Container(
            [
                html.P('', id=IdHolder.score_description.name),
                dcc.Graph(id=IdHolder.graph.name),
                dcc.RangeSlider(
                    min=-10,
                    max=10,
                    value=[-5, 4],
                    id=IdHolder.scale_slider.name,
                    updatemode='drag',
                    tooltip={'placement': 'bottom', 'always_visible': True},
                    allowCross=False,
                    pushable=0.5,
                    step=0.5,
                    marks={i: str(i) for i in range(-10, 11, 2)},
                ),
                html.Div(
                    dbc.Button(
                        'Reset',
                        id=IdHolder.reset_graph_button.name,
                        size='sm',
                        class_name='',
                    ),
                    className='reset-button-container',
                ),
            ],
            id=IdHolder.graph_container.name,
            style={'display': 'none', 'padding': '0'},
        ),
    ],
    title='Score',
    id=IdHolder.score_container.name,
)

apply_button = html.Div(
    dbc.Button(
        'Apply',
        color='primary',
        id=IdHolder.apply_button.name,
        style={
            'position': 'relative',
            'margin-left': 'auto',
            'margin-top': '1rem',
            'float': 'right',
        },
    ),
    className='apply-button-container',
)

parameters = dbc.Row(
    [
        dbc.Accordion(
            [
                recommender_type,
                user_lists_container,
                included_features,
                score_container,
            ],
            always_open=True,
            start_collapsed=False,
        ),
        apply_button,
    ],
    style={'background-color': 'white', 'width': '100%', 'margin-top': '1.5rem'},
)

settings = dbc.Col(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    header,
                    parameters,
                ],
            ),
            style={'background-color': 'white', 'height': '100%'},
        ),
    ],
    style={'background-color': 'white', 'height': '100%'},
    width=4,
)

########################################################################################################################
########################################################################################################################
########################################################################################################################

app.layout = dbc.Card(
    dbc.CardBody(
        [
            dbc.Row(
                [
                    main,
                    settings,
                    dbc.Button(
                        html.I(
                            className='bi bi-info-lg',
                            style={'font-weight': 'bold'},
                        ),
                        id=IdHolder.info_button.name,
                        color='primary',
                        n_clicks=0,
                        style={
                            'position': 'fixed',
                            'bottom': '25px',
                            'left': '25px',
                            'border-radius': '50%',
                            'width': '3rem',
                            'height': '3rem',
                            'z-index': '1000',
                        },
                    ),
                    dbc.Toast(
                        html.P(
                            [
                                html.B('Anilist: '),
                                html.A(
                                    'AlimU',
                                    href='https://anilist.co/user/AlimU/',
                                    target='_blank',
                                ),
                                html.Br(),
                                html.B('GitHub: '),
                                html.A(
                                    'Anime-Recommender',
                                    href='https://github.com/AlimU11/Anime-Recommender',
                                    target='_blank',
                                ),
                                html.Br(),
                                html.I(
                                    'you can give me a star on GitHub if you like a project or open an issue if you found a bug or have any suggestions',
                                    style={'font-size': '0.8rem'},
                                ),
                            ],
                            style={'margin-bottom': '0'},
                        ),
                        id=IdHolder.info_container.name,
                        header='Contacts',
                        is_open=False,
                        dismissable=True,
                        # icon="info",
                        style={
                            'position': 'fixed',
                            'bottom': '5rem',
                            'left': '5rem',
                            'width': 350,
                            'z-index': '1003',
                            'background-color': 'rgba(255,255,255)',
                        },
                    ),
                ],
                style={'height': '100%'},
                align='center',
            ),
            dbc.Modal(
                [
                    modal_body('', ''),
                ],
                id=IdHolder.modal_notification.name,
                is_open=False,
            ),
        ],
    ),
    style={
        'height': '100vh',
        'margin-left': '5vw',
        'margin-right': '0',
        'border': 'none',
    },
)
