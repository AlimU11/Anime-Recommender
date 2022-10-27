> Just notes that point out some interesting for myself features that was implemented so far.

## Media info requests and memoization (removed)

![img_2.png](assets/img_2.png)

Initially, the card info, such as `image url` or `description` was not stored locally. To display the card with title info, the app had to make API requests. Each title sent individual request that looked as follows:

### `media_query` at `client.queries`
```graphql
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
```

Since the limitation to display only top 20 results was introduced from the beginning, that meant that the app had to
make 20 requests. In order to reduce the number of requests, the memoization was introduced. The idea was to store media
info for titles that were already recommended, and thus, for which the app already made requests in `AppData` class.

### `recommend_content()` at `ui.utils`
```python

# get recommendations
# return type: DataFrame
df = app_data.recommender.recommend()

# save columns from `app_data.df`, since it has all columns compared to `df` in its current state
cols = app_data.df.columns

# find out what indexes (this column renamed to `id` further update) are already in `app_data.df`
shared_index = np.intersect1d(app_data.df['index'].values, df['index'].values)

if len(shared_index) > 0:
    # Find out what titles are already in `app_data.df`. For those title we don't need to make API requests.
    # However recommendation probability should be updated according to the new recommendations.
    no_media_update_df = df[df['index'].isin(shared_index)].sort_values(by='index')
    no_media_update_utils = app_data.df[app_data.df['index'].isin(shared_index)].sort_values(by='index')[
        ['cover_image', 'color', 'description', 'title']
    ]

    # delete titles that are already in `app_data.df` from both `df` and `app_data.df`
    df = df[~df['index'].isin(shared_index)]
    app_data.df = app_data.df[~app_data.df['index'].isin(shared_index)]

    # since `ignore_index=True` in pd.concat with `axis=1` affecting columns rather than row indexes, this
    # the only way to concatenate data horizontally correctly is to reindex dataframes beforehand. Otherwise,
    # even dataframes with the same length will be concatenated incorrectly. Refer to
    # https://stackoverflow.com/questions/32801806/pandas-concat-ignore-index-doesnt-work
    # This and further reindexing is introduced in order to avoid this behaviour.

    no_media_update_df.index = np.arange(len(no_media_update_df))
    no_media_update_utils.index = np.arange(len(no_media_update_utils))
    df.index = np.arange(len(df))
    app_data.df.index = np.arange(len(app_data.df))

    # concatenate dataframes horizontally
    no_media_update = pd.concat([no_media_update_df, no_media_update_utils], axis=1, ignore_index=True)
    no_media_update.columns = cols

else:
    no_media_update = pd.DataFrame(columns=cols)

# concatenate prediction with requested data
df = pd.merge(
    df,
    pd.DataFrame(
        pd.DataFrame(df['index'].apply(lambda x: AnilistClient.get_media_info(x)))
        if len(df)
        else pd.DataFrame(columns=['cover_image', 'color', 'description', 'title']),
    ),
    left_index=True,
    right_index=True,
    how='outer',
)


if 'description' in df.columns:
    df.description = df.description.apply(lambda x: app_data.text_processor(x).remove_html_tags())

# concatenate df with no_media_update. This will give a dataframe with all titles to display
df = pd.concat([df, no_media_update], axis=0, ignore_index=True)
df.columns = cols
# update `app_data.df` with new data
app_data.df = pd.concat([app_data.df, df], axis=0, ignore_index=True)
app_data.df.columns = cols

# create cards with info
cards = df.sort_values(by='proba', ascending=False).apply(card, axis=1).tolist()
```

The most unexpected in this implementation was to find out that the `pd.concat` function does not work properly without [reindexing](https://stackoverflow.com/questions/32801806/pandas-concat-ignore-index-doesnt-work).

The above approach could reduce waiting time in case when further recommendation results are similar to previous ones. However, the initial call, as well as calls with completely different recommendations, still had to make the maximum number of requests, which is, consequently, increased waiting time. To solve this, separate requests were replaced with one dynamic request.

Dynamic request for each media:

### `media` at `client.queries`
```graphql
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
```

This also changed parameter for method `get_media_info()` from `int` to `list[int]`:

### `recommend_content()` at `ui.utils`
```python
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
```

Removed after [56b55c4](https://github.com/AlimU11/Anime-Recommender/tree/56b55c4725feb15d7baa8398787a5ac45b32bb36).

To be continued...
