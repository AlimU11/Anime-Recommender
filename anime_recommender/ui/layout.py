import os

import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc, html

from ..storage import LocalStorage
from . import AppData

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
    title='Anime Recommender',
    assets_folder=os.getcwd() + '/assets',
)

app_data = AppData()
app_data.storage = LocalStorage()

INCLUDED_LISTS = ['Completed']
EXCLUDED_LISTS = ['Dropped', 'Watching', 'Rewatching', 'Planning', 'Paused']

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

card = lambda s: dbc.Card(
    [
        dbc.CardBody(
            [
                html.Div(
                    html.Div(
                        f'{s.proba:.0%}',
                        style={
                            'position': 'absolute',
                            'top': '50%',
                            'left': '50%',
                            'transform': 'translate(-50%, -50%)',
                            'color': f'''{'white' if s.color else 'black'}''',
                        },
                    ),
                    style={
                        'text-align': 'right',
                        'background-color': f'''{s.color if s.color else 'white'}''',
                        'border-radius': '50%',
                        'width': '40px',
                        'height': '40px',
                        'color': 'white',
                        'font-size': '0.85rem',
                        'font-weight': 'bold',
                        'display': 'block',
                        'position': 'relative',
                        'margin-left': 'auto',
                        'margin-right': '15px',
                        'margin-top': '15px',
                        'box-shadow': '0 0 10px 0 rgba(0, 0, 0, 0.8)',
                    },
                ),
                html.Div(
                    [
                        html.H6(
                            html.A(
                                f'''{s.title[:24]}{'...' if len(s.title) > 24 else ''}''',
                                href=f'''https://anilist.co/anime/{s['index']}''',
                                target='_blank',
                                style={
                                    'color': f'''{s.color if s.color else 'black'}''',
                                    'text-decoration': 'none',
                                    'z-index': '999',
                                    'position': 'relative',
                                },
                                id=f'''tooltip-title-{s['index']}''',
                                className='card-title',
                            ),
                        ),
                        html.P(
                            f'{s.description}',
                            className='card-text',
                            style={
                                'height': '115px',
                                'overflow-y': 'auto',
                                'width': '100%',
                                'word-wrap': 'break-word',
                                'z-index': '999',
                                'position': 'relative',
                            },
                        ),
                        # dbc.Button(
                        #    f'''Explore''',
                        #    color="primary",
                        #    href=f'''https://anilist.co/anime/{s['index']}''',
                        #    target='_blank'
                        # ),
                    ],
                    style={
                        'margin': '0px',
                        'padding': '10px',
                        'width': '100%',
                        'height': '50%',
                        'background-color': 'white',
                        'overflow': 'hidden',
                        'text-overflow': 'ellipsis',
                    },
                    className='mt-auto',
                ),
                tooltip(s.title, f'''tooltip-title-{s['index']}''', 'top') if len(s.title) > 24 else '',
                html.A(
                    className='stretched-link',
                    href=f'''https://anilist.co/anime/{s['index']}''',
                    target='_blank',
                ),
            ],
            style={
                'padding': '0px',
                'background-image': f'url({s.cover_image})',
                'background-repeat': 'no-repeat',
                'background-position': 'bottom',
                'background-size': '100% auto',
                'object-fit': 'cover',
                'overflow': 'hidden',
                'text-overflow': 'ellipsis',
                'border-radius': '12px',
                'padding': '0px',
                'box-shadow': '0 6px 10px rgba(0,0,0,.08), 0 0 6px rgba(0,0,0,.05)',
                'transition': '.3s transform cubic-bezier(.155,1.105,.295,1.12),.3s box-shadow,.3s '
                '-webkit-transform cubic-bezier(.155,1.105,.295,1.12)',
            },
            className='flex-column d-flex content-card',
        ),
    ],
    style={
        'width': '16rem',
        'height': '20rem',
        'margin-bottom': '3rem',
        'border-radius': '12px',
        'padding': '0px',
        'box-shadow': '0 6px 10px rgba(0,0,0,.08), 0 0 6px rgba(0,0,0,.05)',
        'transition': '.3s transform cubic-bezier(.155,1.105,.295,1.12),.3s box-shadow,.3s '
        '-webkit-transform cubic-bezier(.155,1.105,.295,1.12)',
    },
)

modal_body = lambda header, text: [
    dbc.ModalHeader(dbc.ModalTitle(header)),
    dbc.ModalBody(text),
    dbc.ModalFooter(dbc.Button('Close', id='close-button', className='ms-auto', n_clicks=0)),
]

user_lists = lambda lists: [
    html.H4('User lists'),
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
        id='checklist-included',
    ),
    html.H5('Excluded:'),
    dbc.Checklist(
        options=lists,
        value=EXCLUDED_LISTS,
        id='checklist-excluded',
    ),
]

########################################################################################################################
#                                                  Main layout                                                         #
########################################################################################################################

search_switch = dbc.Col(
    [
        dbc.Switch(
            id='search-switch',
            label='By username',
            value=False,
        ),
        # html.Div("By username")
    ],
    align='center',
    width=2,
    style={'width': '170px'},
)

search_input = dbc.Col(
    [
        dbc.InputGroup(
            [
                dbc.InputGroupText('@'),
                dbc.Input(
                    placeholder='Anilist Username, e.g. "AlimU"',
                    id='search-user-input',
                    type='text',
                ),
            ],
            style={'height': '100%', 'margin': '0px'},
        ),
    ],
    style={'background-color': 'white', 'margin-left': '2rem'},
    id='search-user-input-container',
    align='center',
)

search_input1 = dbc.Col(
    [
        dcc.Dropdown(
            app_data.storage.select(['title'], sort_by=['index'], axis=0).title.unique().tolist(),
            multi=True,
            id='search-titles-input',
        ),
    ],
    style={'background-color': 'white', 'margin-left': '2rem'},
    id='search-title-input-container',
)

search_button = dbc.Col(
    dbc.Button(
        'Generate',
        color='primary',
        id='generate-recommendations-button',
    ),
    width=2,
    style={'background-color': 'white'},
)

searchbar = dbc.Row(
    [
        dbc.Col(
            dbc.Row(
                [
                    search_switch,
                    search_input,
                    search_input1,
                ],
            ),
        ),
        search_button,
    ],
    style={'background-color': 'white', 'height': '100px'},
)

output = dbc.Row(
    [
        dbc.Spinner(
            dbc.Col(
                [],
                id='output',
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
                    output,
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

engine = dbc.AccordionItem(
    [
        #  question_mark('tooltip-engine'),
        #  tooltip('linear_kernel, rbf_kernel', 'tooltip-engine', 'right'),
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
            id='radio-input-engine',
            style={'cursor': 'pointer'},
        ),
    ],
    title='Recommendation Engine',
)

columns_container = dbc.AccordionItem(
    user_lists([]),
    title='User Lists',
    id='columns-container',
    className='user-lists-container',
)

feature_options = [
    {'label': 'Tags', 'value': 'tags'},
    {'label': 'Genres', 'value': 'genres'},
    {'label': 'Average Score', 'value': 'mean_score'},
    {'label': 'Format', 'value': 'format'},
    {'label': 'Number of Episodes', 'value': 'episodes'},
    {'label': 'Duration', 'value': 'duration'},
    {'label': 'Source', 'value': 'source'},
    {'label': 'Origin', 'value': 'origin'},
    {'label': 'Season', 'value': 'season'},
    {'label': 'Is Adult', 'value': 'is_adult'},
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
        #  question_mark('tooltip-features'),
        #  tooltip(
        #      'genres, tags, studios, description, average score, etc...',
        #      'tooltip-features',
        #      'right',
        #  ),
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
                            html.Li('Tags: list of tags that title belongs to with their respective scores.'),
                            html.Li('Genres: list of genres that title belongs to.'),
                            html.Li('Average Score: average score of title.'),
                            html.Li('Format: format of title (TV, Movie, etc...).'),
                            html.Li('Number of Episodes: number of episodes in title.'),
                            html.Li('Duration: duration of each episode in minutes.'),
                            html.Li('Source: source of title (Manga, Light Novel, etc...).'),
                            html.Li('Origin: origin of title (Japan, China, etc...).'),
                            html.Li('Season: season of release (Winter, Spring, etc...).'),
                            html.Li('Is Adult: whether title is adult or not.'),
                            html.Li('Favorites: number of users that added title to their favorites.'),
                            html.Li('Popularity: AniList popularity score.'),
                            html.Li('Studios: list of studios that worked on title.'),
                            html.Li('Producers: list of producers that worked on title.'),
                        ],
                    ),
                ],
                title='Feature description',
                class_name='feature-description',
            ),
            start_collapsed=True,
        ),
        html.Div([], id='alert-included-features'),
        dbc.Checklist(
            options=feature_options,
            value=['tags'],
            id='checklist-features',
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
                # question_mark('tooltip-weighted'),
                # tooltip('count user score', 'tooltip-weighted', 'right'),
            ],
        ),
        html.I(
            'Whether to include user scores in calculation or not. Each score applies as a coefficient to the corresponding title that user watched.',
            style={'margin': '0.5rem 0', 'display': 'inline-block'},
        ),
        dbc.Checklist(
            options=weighted_options,
            value=[True],
            id='checklist-weighted',
            style={'cursor': 'pointer'},
        ),
    ],
    id='container-weighted',
)

scaled_container = dbc.Container(
    [
        html.H5(
            [
                'Scaled',
                # question_mark('tooltip-scaled'),
                # tooltip('scale user scores', 'tooltip-scaled', 'right'),
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
            id='checklist-scaled',
            style={'cursor': 'pointer'},
        ),
    ],
    id='container-scaled',
)

score_container = dbc.AccordionItem(
    [
        weighted_container,
        scaled_container,
        dbc.Container(
            [
                html.P('', id='scale-text'),
                dcc.Graph(id='graph'),
                dcc.RangeSlider(
                    min=-10,
                    max=10,
                    value=[-5, 4],
                    id='scale-slider',
                    updatemode='drag',
                    tooltip={'placement': 'bottom', 'always_visible': True},
                    allowCross=False,
                    pushable=0.5,
                    step=0.5,
                    marks={i: str(i) for i in range(-10, 11, 2)},
                ),
                html.Div(
                    dbc.Button('Reset', id='reset-graph', size='sm', class_name=''),
                    className='reset-button-container',
                ),
            ],
            id='scale-graph-container',
            style={'display': 'none', 'padding': '0'},
        ),
    ],
    title='Score',
    id='score-container',
)

apply_button = html.Div(
    dbc.Button(
        'Apply',
        color='primary',
        id='apply-parameters-button',
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
                engine,
                columns_container,
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
                        id='positioned-toast-toggle',
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
                                html.A('AlimU', href='https://anilist.co/user/AlimU/', target='_blank'),
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
                        id='positioned-toast',
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
                id='modal',
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
