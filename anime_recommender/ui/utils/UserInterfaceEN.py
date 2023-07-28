from .StrEnum import StrEnum


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

    user_lists_desc_1 = 'User lists to include or exclude from recommendations. Entries from '
    user_lists_desc_2 = 'Included'
    user_lists_desc_3 = ' take part in calculation recommendations. Entries from '
    user_lists_desc_4 = 'Excluded'
    user_lists_desc_5 = ' do not participate in calculation, but simply excluded from recommendation results. '

    rec_engine_desc_1 = (
        'Recommendation engine stands for the algorithm used to generate recommendations. Standard (linear kernel) is the default engine and works good for most cases. Experimental (rbf kernel) is awful for large number of titles, but can give some interesting results for individual one(s).',
    )

    features_desc_1 = (
        'Each title has individual features that make it unique and distinguish from others. Those features could be included in calculation and potentially affect recommendation results. The further information about each feature is presented below.',
    )
    features_desc_2 = ('Tags: list of tags that title belongs to with their respective scores.',)
    features_desc_3 = 'Genres: list of genres that title belongs to.'
    features_desc_4 = 'Average Score: average score of title.'
    features_desc_5 = 'Format: format of title (TV, Movie, etc...).'
    features_desc_6 = 'Number of Episodes: number of episodes in title.'
    features_desc_7 = 'Duration: duration of each episode in minutes.'
    features_desc_8 = 'Source: source of title (Manga, Light Novel, etc...).'
    features_desc_9 = 'Origin: origin of title (Japan, China, etc...).'
    features_desc_10 = ('Season: season of release (Winter, Spring, etc...).',)
    features_desc_11 = 'Is Adult: whether title is adult or not.'
    features_desc_12 = 'Favorites: number of users that added title to their favorites.'
    features_desc_13 = 'Popularity: AniList popularity score.'
    features_desc_14 = 'Studios: list of studios that worked on title.'
    features_desc_15 = ('Producers: list of producers that worked on title.',)

    weighted_desc_1 = (
        'Whether to include user scores in calculation or not. Each score applies as a coefficient to the corresponding title that user watched.',
    )

    scaled_desc_1 = 'While usual scores make a linear effect on the results,'
    scaled_desc_2 = '(e.g. if two titles have the same recommendation result but the first has score 5 and the second score 10, the latter will be two times more significant)'
    scaled_desc_3 = 'scaled ones introduces intuitively more logical approach — titles with scores from 2 to 5 are probably not much better (or not much different) compared to ones with 1 scores. And vice versa, for scores from 7 to 10.'

    toast_desc_1 = 'Anilist: '
    toast_desc_2 = 'AlimU'
    toast_desc_3 = 'GitHub: '
    toast_desc_4 = 'Anime-Recommender'
    toast_desc_5 = (
        'you can give me a star on GitHub if you like a project or open an issue if you found a bug or have any suggestions',
    )
