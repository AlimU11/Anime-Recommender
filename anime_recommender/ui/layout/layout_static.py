"""Static components for layout."""
import dash_bootstrap_components as dbc
from dash import dcc, html

from anime_recommender.config import config
from anime_recommender.ui.app_data import app_data
from anime_recommender.ui.layout.layout_dynamic import option_template, user_lists
from anime_recommender.ui.ui_utils.id_holder import IdHolder as ID
from anime_recommender.ui.ui_utils.user_interface_en import UserInterfaceEN as UI

language_options = [
    dbc.DropdownMenuItem(UI.lang_dropdown_en, id=ID.english),
    dbc.DropdownMenuItem(UI.lang_dropdown_rj, id=ID.romaji),
    dbc.DropdownMenuItem(UI.lang_dropdown_na, id=ID.native),
]

source_options = [
    dbc.DropdownMenuItem(UI.source_dropdown_anilist, id=ID.anilist),
]

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
    ),
)

title_search = dcc.Dropdown(
    option_template(app_data.by_popularity.id.values[: config.dropdown_item_count]),
    placeholder=UI.placeholder_items,
    multi=True,
    id=ID.item_searchbar,
    maxHeight=400,
    optionHeight=65,
    persistence=True,
    persistence_type='local',
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

header_main = html.Div(
    [
        html.H2(UI.title_main),
        # button for mobile view
        dbc.Button(
            [
                html.Span(UI.title_parameters),
                html.I(className='bi bi-arrow-right'),
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
    dbc.Spinner(dbc.Col(id=ID.output_container)),
    className='output-container',
)

main = dbc.Col(
    dbc.Card(
        dbc.CardBody(
            [
                header_main,
                searchbar,
                output_container,
            ],
        ),
    ),
    width=8,
    class_name='main-column',
)

header_parameters = dbc.Row(
    html.H2(
        html.Div(
            [
                html.Div(UI.title_parameters),
                html.Div(html.I(className='bi bi-sliders2')),
            ],
        ),
    ),
)

recommender_type = dbc.AccordionItem(
    [
        html.P(UI.title_rec_engine, className='title-mobile'),
        html.P(html.I(UI.rec_engine_desc1)),
        dbc.RadioItems(
            options=[
                {'label': 'Standard', 'value': 'linear_kernel'},
                {'label': 'Experimental', 'value': 'rbf_kernel'},
            ],
            value='linear_kernel',
            id=ID.recommender_type,
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
        html.P(html.I(UI.features_desc1)),
        dbc.Accordion(
            dbc.AccordionItem(
                [
                    html.Ol(
                        [
                            html.Li(UI.features_desc2),
                            html.Li(UI.features_desc3),
                            html.Li(UI.features_desc4),
                            html.Li(UI.features_desc5),
                            html.Li(UI.features_desc6),
                            html.Li(UI.features_desc7),
                            html.Li(UI.features_desc8),
                            html.Li(UI.features_desc9),
                            html.Li(UI.features_desc10),
                            html.Li(UI.features_desc11),
                            html.Li(UI.features_desc12),
                            html.Li(UI.features_desc13),
                            html.Li(UI.features_desc14),
                            html.Li(UI.features_desc15),
                        ],
                    ),
                ],
                title=UI.title_features_desc,
                class_name='feature-description',
            ),
            start_collapsed=True,
        ),
        html.Div([], id=ID.features_alert),
        dbc.Checklist(options=feature_options, value=['tags'], id=ID.features_list),
    ],
    title=UI.title_features,
)

weighted_container = dbc.Container(
    [
        html.H5(UI.title_weigted),
        html.I(UI.weighted_desc1),
        dbc.Checklist(options=weighted_options, value=[True], id=ID.is_weighted),
    ],
    id=ID.weighted_container,
)

scaled_container = dbc.Container(
    [
        html.H5(UI.title_scaled),
        html.I(
            [
                UI.scaled_desc1,
                html.Br(),
                html.Span(UI.scaled_desc2),
                html.Br(),
                UI.scaled_desc3,
            ],
        ),
        dbc.Checklist(options=scaled_options, value=[], id=ID.is_scaled),
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
                    marks={slider_val: str(slider_val) for slider_val in range(-10, 11, 2)},
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
        ),
    ],
    title=UI.title_score,
    id=ID.score_container,
)

apply_button = html.Div(
    dbc.Button(UI.button_apply, color='primary', id=ID.apply_button),
    className='apply-button-container',
)

parameters_body = dbc.Row(
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
    class_name='settings-accordion',
)

settings = dbc.Col(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    header_parameters,
                    parameters_body,
                ],
            ),
            class_name='settings-card',
        ),
    ],
    width=4,
    class_name='settings-column',
)

info_button = [
    dbc.Button(
        html.I(className='bi bi-info-lg'),
        id=ID.info_button,
        color='primary',
        n_clicks=0,
    ),
    dbc.Toast(
        html.P(
            [
                html.B(UI.toast_desc1),
                html.A(
                    UI.toast_desc2,
                    href='https://anilist.co/user/AlimU/',
                    target='_blank',
                ),
                html.Br(),
                html.B(UI.toast_desc3),
                html.A(
                    UI.toast_desc4,
                    href='https://github.com/AlimU11/Anime-Recommender',
                    target='_blank',
                ),
                html.Br(),
                html.I(UI.toast_desc5),
            ],
        ),
        id=ID.info_container,
        header='Contacts',
        is_open=False,
        dismissable=True,
    ),
]
