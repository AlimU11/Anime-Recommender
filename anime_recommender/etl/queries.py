query = '''
query ($page: Int, $perPage: Int) {
    Page (page: $page, perPage: $perPage) {
        pageInfo {
            hasNextPage
        }
        media (sort: ID, type: ANIME) {
            id,

            title {
                romaji,
                english,
                native,
            },

            description,

            tags {
              name,
              rank,
            }

            isAdult,

            format,

            status,

            episodes,

            duration,

            season,

            startDate {
              year,
              month,
              day
            },

            endDate {
              year,
              month,
              day
            },

            meanScore,

            popularity,

            favourites,

            source,

            countryOfOrigin,

            genres,

            coverImage {
              extraLarge,
              medium,
              color
            }

            studios {
                nodes {
                    name,
                    isAnimationStudio,
                  }
                  edges {
                    isMain,

                  }
            }
        }
    }
}
'''
