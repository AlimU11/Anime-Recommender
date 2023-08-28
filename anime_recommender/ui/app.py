"""Dash app initialization module."""

import os

import dash_bootstrap_components as dbc

from anime_recommender.ui.callbacks.callbacks_misc import cl, update_info_toast, update_modal
from anime_recommender.ui.callbacks.callbacks_parameters import (
    update_features_list,
    update_scaled,
    update_scaled_container,
    update_scaled_graph,
    user_lists_mutual_exclusion,
)
from anime_recommender.ui.callbacks.callbacks_search_output import (
    change_search_type,
    update_items_dropdown,
    update_output,
    update_titles_language,
)
from anime_recommender.ui.layout.layout import layout
from anime_recommender.ui.ui_utils.dcw import DCWDash
from anime_recommender.ui.ui_utils.user_interface_en import UserInterfaceEN as UI

app = DCWDash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
    title=UI.title_main,
    assets_folder='{path}/assets'.format(path=os.getcwd()),
)

app.layout = layout
