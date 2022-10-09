id_query = '''
query ($name: String) {
    User(name: $name) {
        id,
        name
    }
}
'''
"""Query to get user id by user name."""

lists_query = '''
query ($id: Int) {
    MediaListCollection(userId: $id, type: ANIME, forceSingleCompletedList: true) {
        hasNextChunk
        user {
            id
        }
        lists {
            name,
            isCustomList,
            entries {
                mediaId,
                score
              }
        }
    }
}
'''
"""Query to get user's lists by user id."""

media_query = '''
query ($id: Int) {
    Media(id: $id) {
        coverImage {
          large,
          color
        }
        description,
        title {
            english,
            romaji
        }
    }
}
'''
"""Static query to get single media by id."""

media = lambda id: str.format(
    '''
    media_{0}: Media (id: $id_{0}) {{
        coverImage {{
          large,
          color
        }}
        description,
        title {{
            english,
            romaji
        }}
    }}
''',
    id,
)
"""Dynamic query to get single media by id."""

query = lambda idx: str.format(
    '''
query ({0}) {{
    {1}
}}
''',
    ', '.join([f'$id_{id}: Int' for id in idx]),
    ''.join([media(id) for id in idx]),
)
"""Dynamic query to get multiple media by id. Concatenate dynamic media queries."""

variables = lambda idx: {f'id_{id}': id for id in idx}
"""Variables for query to get multiple media by id."""
