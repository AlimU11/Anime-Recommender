import os

import dash_bootstrap_components as dbc
from dash import dcc, html

from ..storage import LocalStorage
from . import AppData
from .utils.dcw import DCWDash
from .utils.IdHolder import IdHolder as ID
from .utils.UserInterfaceEN import UserInterfaceEN as UI

app = DCWDash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
    title=UI.title_main,
    assets_folder=os.getcwd() + '/assets',
)

app_data = AppData()
app_data.storage = LocalStorage()


RESULT_AMOUNT = int(os.environ.get('RESULT_AMOUNT'))
INCLUDED_LISTS = ['Completed']
EXCLUDED_LISTS = ['Dropped', 'Watching', 'Rewatching', 'Planning', 'Paused']

by_popularity = app_data.storage.info.sort_values(by='popularity', ascending=False)
app_data.storage.info.sort_values(by='id', ascending=True, inplace=True)

language_options = [
    dbc.DropdownMenuItem(UI.lang_dropdown_en, id=ID.english),
    dbc.DropdownMenuItem(UI.lang_dropdown_rj, id=ID.romaji),
    dbc.DropdownMenuItem(UI.lang_dropdown_na, id=ID.native),
]

source_options = [
    dbc.DropdownMenuItem(UI.source_dropdown_anilist, id=ID.Anilist),
]

tooltip = lambda text, id, placement='auto': dbc.Tooltip(
    text,
    target=id,
    autohide=False,
    placement=placement,
)

question_mark = lambda id: html.Sup(
    html.I(className='bi bi-question-circle-fill'),
    id=id,
    className='question-mark',
)

alert = lambda: dbc.Alert(
    [
        html.I(className='bi bi-exclamation-triangle-fill'),
        html.Span(
            [
                UI.not_found_alert_text_start,
                html.A(
                    f'https://anilist.co/user/{app_data.username_searchbar}/',
                    href=f'https://anilist.co/user/{app_data.username_searchbar}/',
                    target='_blank',
                    className='alert-link',
                ),
                UI.not_found_alert_text_end,
            ],
        ),
    ],
    color='danger',
    id=ID.not_found_alert,
)


def option_template(options: list[int], language: str = 'english'):
    return [
        {
            'label': html.Div(
                [
                    html.Div(
                        style={
                            'background-color': row.color,
                            'background-image': f'url({row.img_small})',
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
                            html.Div(
                                [row.startDate_year, ' ', row.format],
                                className='dropdown-info',
                            ),
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
        for row in by_popularity.query('id in @options').itertuples()
    ]


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
                                'color': f"""{'white' if s.color else 'black'}""",
                            },
                            className='probability-score',
                        ),
                        style={
                            'background-color': f"""{s.color if s.color else 'white'}""",
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
                            html.Div(
                                [
                                    html.Span(
                                        f'{s.meanScore*10:.1f}{"" if s.meanScore else "N/A"}',
                                        style={'margin-right': '0.25rem'},
                                    ),
                                    html.I(
                                        className='bi bi-star-fill',
                                    ),
                                ],
                                style={
                                    'background-color': f'{s.color if s.color else "white"}',
                                    'color': f"""{'white' if s.color else 'black'}""",
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
                                    f"""{s[app_data.language][:title_len]}{'...' if len(s[app_data.language]) > title_len else ''}""",
                                    href=f"""https://anilist.co/anime/{int(s['id'])}""",
                                    target='_blank',
                                    style={
                                        'color': f"""{s.color if s.color else 'black'}""",
                                    },
                                    id=f"""tooltip-title-{s['id']}""",
                                    className='card-title',
                                ),
                                style={
                                    'margin': '0',
                                    'display': 'inline-block',
                                },
                            ),
                            html.P(
                                f"""{int(s.startDate_year)} {s.format}""",
                                style={
                                    'margin': '0',
                                    'color': f"""{s.color if s.color else 'black'}""",
                                    'font-size': '0.8rem',
                                    'margin-top': '-0.25rem',
                                },
                            ),
                            html.P(
                                f'{s.description}',
                                className='card-description',
                            ),
                        ],
                        className='mt-auto card-text-container',
                    ),
                    tooltip(s[app_data.language], f"""tooltip-title-{s['id']}""", 'top')
                    if len(s[app_data.language]) > title_len
                    else '',
                    html.A(
                        className='stretched-link',
                        href=f"""https://anilist.co/anime/{int(s['id'])}""",
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
            UI.button_close,
            id=ID.close_button,
            className='ms-auto',
            n_clicks=0,
        ),
    ),
]

user_lists = lambda lists: [
    html.P(UI.title_user_lists, className='title-mobile'),
    html.I(
        [
            UI.user_lists_desc_1,
            html.B(UI.user_lists_desc_2),
            UI.user_lists_desc_3,
            html.B(UI.user_lists_desc_4),
            UI.user_lists_desc_5,
        ],
        # style={"margin": "1rem 0", "display": "inline-block"},
        className='user-lists-description',
    ),
    html.H5(UI.included_list_title),
    dbc.Checklist(
        options=lists,
        value=INCLUDED_LISTS,
        id=ID.included_list,
    ),
    html.H5(UI.excluded_list_title),
    dbc.Checklist(
        options=lists,
        value=EXCLUDED_LISTS,
        id=ID.excluded_list,
    ),
]

alert_features = dbc.Alert(
    [
        html.I(className='bi bi-info-circle-fill me-2'),
        UI.feature_selection_aleart,
    ],
    color='info',
    className='d-flex align-items-center feature-alert',
    # style={
    #     "height": "fit-content",
    #     "font-size": "0.8em",
    #     "margin": "0px",
    #     "margin-bottom": "1rem",
    #     "padding": "2px 5px",
    # },
)

########################################################################################################################
#                                                  Main layout                                                         #
########################################################################################################################

search_type_switch = html.Div(
    [
        dbc.Switch(
            id=ID.search_type_switch,
            label=UI.by_username,
            value=False,
        ),
    ],
)

user_search = (
    dbc.DropdownMenu(source_options, label=UI.source_dropdown_anilist, id=ID.source),
    dbc.InputGroupText(UI.at, id=ID.input_group_text),
    dbc.Input(
        placeholder=UI.placeholder_username,
        id=ID.username_searchbar,
        type='text',
        # style={
        #     "display": "block",
        #     "width": "100%",
        # },
    ),
)

title_search = dcc.Dropdown(
    option_template(by_popularity.id.values[:RESULT_AMOUNT]),
    placeholder=UI.placeholder_items,
    multi=True,
    id=ID.item_searchbar,
    maxHeight=400,
    optionHeight=65,
    persistence=True,
    persistence_type='local',
    # style={"display": "none"},
)

search_input = dbc.Col(
    dbc.InputGroup(
        [
            *user_search,
            title_search,
            dbc.DropdownMenu(
                language_options,
                label=UI.lang_dropdown_en,
                id=ID.titles_language,
            ),
        ],
        id=ID.input_group,
    ),
    id=ID.searchbar_container,
)

generate_button = html.Div(
    dbc.Button(
        UI.button_generate,
        color='primary',
        id=ID.generate_button,
    ),
)

header = html.Div(
    [
        html.H2(UI.title_main),
        # button for mobile view
        dbc.Button(
            [
                html.Span(UI.title_parameters),
                html.I(
                    className='bi bi-arrow-right',
                    style={'font-weight': 'bold', 'margin-left': '0.5rem'},
                ),
            ],
        ),
    ],
    className='header-container',
)

searchbar = html.Div(
    [
        search_type_switch,
        html.Div(
            search_input,
            className='searchbar-container',
        ),
        generate_button,
    ],
    className='search-container',
)

output_container = dbc.Row(
    [
        dbc.Spinner(
            dbc.Col(
                [],
                id=ID.output_container,
            ),
        ),
    ],
    className='output-container',
)

main = dbc.Col(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    header,
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
    # style={"height": "100%"},
    class_name='main-column',
)

########################################################################################################################
#                                                  Parameters                                                          #
########################################################################################################################

header = dbc.Row(
    [
        html.H2(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                UI.title_parameters,
                            ],
                        ),
                        html.Div(
                            [
                                html.I(
                                    className='bi bi-sliders2',
                                    style={'font-weight': 'bold'},
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)

recommender_type = dbc.AccordionItem(
    [
        html.P(UI.title_rec_engine, className='title-mobile'),
        html.P(
            html.I(UI.rec_engine_desc_1),
            style={'margin-bottom': '1rem'},
        ),
        dbc.RadioItems(
            options=[
                {'label': 'Standard', 'value': 'linear_kernel'},
                {'label': 'Experimental', 'value': 'rbf_kernel'},
            ],
            value='linear_kernel',
            id=ID.recommender_type,
            style={'cursor': 'pointer'},
        ),
    ],
    title=UI.title_rec_engine,
)

user_lists_container = dbc.AccordionItem(
    user_lists([]),
    title=UI.title_user_lists,
    id=ID.user_lists,
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
        html.P(UI.title_features, className='title-mobile'),
        html.P(
            html.I(UI.features_desc_1),
            style={'margin-bottom': '1rem'},
        ),
        dbc.Accordion(
            dbc.AccordionItem(
                [
                    html.Ol(
                        [
                            html.Li(UI.features_desc_2),
                            html.Li(UI.features_desc_3),
                            html.Li(UI.features_desc_4),
                            html.Li(UI.features_desc_5),
                            html.Li(UI.features_desc_6),
                            html.Li(UI.features_desc_7),
                            html.Li(UI.features_desc_8),
                            html.Li(UI.features_desc_9),
                            html.Li(UI.features_desc_10),
                            html.Li(UI.features_desc_11),
                            html.Li(UI.features_desc_12),
                            html.Li(UI.features_desc_13),
                            html.Li(UI.features_desc_14),
                            html.Li(UI.features_desc_15),
                        ],
                    ),
                ],
                title=UI.title_features_desc,
                class_name='feature-description',
            ),
            start_collapsed=True,
        ),
        html.Div([], id=ID.features_alert),
        dbc.Checklist(
            options=feature_options,
            value=['tags'],
            id=ID.features_list,
            style={'cursor': 'pointer'},
        ),
    ],
    title=UI.title_features,
)

weighted_container = dbc.Container(
    [
        html.H5(UI.title_weigted),
        html.I(
            UI.weighted_desc_1,
            style={'margin': '0.5rem 0', 'display': 'inline-block'},
        ),
        dbc.Checklist(
            options=weighted_options,
            value=[True],
            id=ID.is_weighted,
            style={'cursor': 'pointer'},
        ),
    ],
    id=ID.weighted_container,
)

scaled_container = dbc.Container(
    [
        html.H5(UI.title_scaled),
        html.I(
            [
                UI.scaled_desc_1,
                html.Br(),
                html.Span(
                    UI.scaled_desc_2,
                    style={'margin': '0.5rem 0', 'display': 'inline-block'},
                ),
                html.Br(),
                UI.scaled_desc_3,
            ],
            style={'margin-bottom': '1rem', 'display': 'inline-block'},
        ),
        dbc.Checklist(
            options=scaled_options,
            value=[],
            id=ID.is_scaled,
            style={'cursor': 'pointer'},
        ),
    ],
    id=ID.scaled_container,
)

score_container = dbc.AccordionItem(
    [
        weighted_container,
        scaled_container,
        dbc.Container(
            [
                html.P('', id=ID.score_description),
                dcc.Graph(id=ID.graph),
                dcc.RangeSlider(
                    min=-10,
                    max=10,
                    value=[-5, 4],
                    id=ID.scale_slider,
                    updatemode='drag',
                    tooltip={'placement': 'bottom', 'always_visible': True},
                    allowCross=False,
                    pushable=0.5,
                    step=0.5,
                    marks={i: str(i) for i in range(-10, 11, 2)},
                ),
                html.Div(
                    dbc.Button(
                        UI.button_reset,
                        id=ID.reset_graph_button,
                        size='sm',
                        class_name='',
                    ),
                    className='reset-button-container',
                ),
            ],
            id=ID.graph_container,
            style={'display': 'none', 'padding': '0'},
        ),
    ],
    title=UI.title_score,
    id=ID.score_container,
)

apply_button = html.Div(
    dbc.Button(
        UI.button_apply,
        color='primary',
        id=ID.apply_button,
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
    class_name='settings-accordion',
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
            class_name='settings-card',
        ),
    ],
    style={'background-color': 'white', 'height': '100%'},
    width=4,
    class_name='settings-column',
)

########################################################################################################################
########################################################################################################################
########################################################################################################################

info_button = [
    dbc.Button(
        html.I(
            className='bi bi-info-lg',
            style={'font-weight': 'bold'},
        ),
        id=ID.info_button,
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
                html.B(UI.toast_desc_1),
                html.A(
                    UI.toast_desc_2,
                    href='https://anilist.co/user/AlimU/',
                    target='_blank',
                ),
                html.Br(),
                html.B(UI.toast_desc_3),
                html.A(
                    UI.toast_desc_4,
                    href='https://github.com/AlimU11/Anime-Recommender',
                    target='_blank',
                ),
                html.Br(),
                html.I(
                    UI.toast_desc_5,
                    style={'font-size': '0.8rem'},
                ),
            ],
            style={'margin-bottom': '0'},
        ),
        id=ID.info_container,
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
]

app.layout = html.Div(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            main,
                            settings,
                        ],
                        style={'height': '100%'},
                        align='center',
                    ),
                    dbc.Modal(
                        [
                            modal_body('', ''),
                        ],
                        id=ID.modal_notification,
                        is_open=False,
                    ),
                    html.Span(className='hidden', id=ID.hidden),
                ],
                class_name='main-card-body',
            ),
            style={
                'height': '100vh',
                'margin-left': '5vw',
                'margin-right': '0',
                'border': 'none',
            },
            class_name='main-card',
        ),
        dbc.Button(
            id=ID.trigger_modal_update,
            style={'display': 'none'},
        ),
        dbc.Button(
            id=ID.trigger_switch_update,
            style={'display': 'none'},
        ),
        *info_button,
    ],
)
