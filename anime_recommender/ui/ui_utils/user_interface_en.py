"""
English localization for the user interface of an Anime Recommender application.

This module provides the `UserInterfaceEN` enumeration, which contains
string constants for various UI components in the English language.

Attributes
----------
StrEnum : class
    Base enumeration class from which `UserInterfaceEN` is derived.

Classes
-------
UserInterfaceEN
    Enumeration defining English localized strings for various UI components.

Author
------
AlimU
"""

from anime_recommender.ui.ui_utils.str_enum import StrEnum


class UserInterfaceEN(StrEnum):
    """User interface in English."""

    title_main = 'Anime Recommender'
    title_parameters = 'Parameters'
    title_user_lists = 'User Lists'
    title_rec_engine = 'Recommendation Engine'
    title_features = 'Included Features'
    title_features_desc = 'Features Description'
    title_score = 'Score'
    title_weigted = 'Weighted'
    title_scaled = 'Scaled'

    lang_dropdown_en = 'english'
    lang_dropdown_rj = 'romaji'
    lang_dropdown_na = 'native'

    source_dropdown_anilist = 'Anilist'

    not_found_alert_text_start = 'Username not found. Are you sure that '
    not_found_alert_text_end = ' is exist?'

    included_list_title = 'Included:'
    excluded_list_title = 'Excluded:'

    feature_selection_aleart = 'At least one feature must be selected'

    by_username = 'By username'
    by_title = 'By title'

    at = '@'

    placeholder_username = 'Username'
    placeholder_items = 'Type to search'

    button_generate = 'Generate'
    button_apply = 'Apply'
    button_close = 'Close'
    button_reset = 'Reset'

    user_lists_desc1 = 'User lists to include or exclude from recommendations. Entries from '

    user_lists_desc2 = 'Included'
    user_lists_desc3 = ' take part in calculation recommendations. Entries from '
    user_lists_desc4 = 'Excluded'
    user_lists_desc5 = ' do not participate in calculation, but simply excluded from recommendation results. '

    rec_engine_desc1 = (
        'Recommendation engine stands for the algorithm used to generate recommendations. Standard (linear kernel) is '
        + 'the default engine and works good for most cases. Experimental (rbf kernel) is awful for large number of '
        + 'titles, but can give some interesting results for individual one(s).',
    )

    features_desc1 = (
        'Each title has individual features that make it unique and distinguish from others. Those features could be '
        + 'included in calculation and potentially affect recommendation results. The further information about each '
        + 'feature is presented below.',
    )
    features_desc2 = ('Tags: list of tags that title belongs to with their respective scores.',)
    features_desc3 = 'Genres: list of genres that title belongs to.'
    features_desc4 = 'Average Score: average score of title.'
    features_desc5 = 'Format: format of title (TV, Movie, etc...).'
    features_desc6 = 'Number of Episodes: number of episodes in title.'
    features_desc7 = 'Duration: duration of each episode in minutes.'
    features_desc8 = 'Source: source of title (Manga, Light Novel, etc...).'
    features_desc9 = 'Origin: origin of title (Japan, China, etc...).'
    features_desc10 = 'Season: season of release (Winter, Spring, etc...).'
    features_desc11 = 'Is Adult: whether title is adult or not.'
    features_desc12 = 'Favorites: number of users that added title to their favorites.'
    features_desc13 = 'Popularity: AniList popularity score.'
    features_desc14 = 'Studios: list of studios that worked on title.'
    features_desc15 = 'Producers: list of producers that worked on title.'

    weighted_desc1 = (
        'Whether to include user scores in calculation or not. Each score applies as a coefficient to the '
        + 'corresponding title that user watched.',
    )

    scaled_desc1 = 'While usual scores make a linear effect on the results,'
    scaled_desc2 = (
        '(e.g. if two titles have the same recommendation result but the first has score 5 and the second '
        + 'score 10, the latter will be two times more significant)'
    )
    scaled_desc3 = (
        'scaled ones introduces intuitively more logical approach — titles with scores from 2 '
        + 'to 5 are probably not much better (or not much different) compared to ones with 1 scores. And vice versa, '
        + 'for scores from 7 to 10.'
    )

    toast_desc1 = 'Anilist: '
    toast_desc2 = 'AlimU'
    toast_desc3 = 'GitHub: '
    toast_desc4 = 'Anime-Recommender'
    toast_desc5 = (
        'you can give me a star on GitHub if you like a project or open an issue if you found a bug or have any '
        + 'suggestions',
    )
