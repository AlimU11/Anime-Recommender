import os

import yaml

from anime_recommender.anilist_etl import AnilistExtractor

# load config variables to environment variables
with open('global_config.yaml', 'r') as f:
    config = yaml.safe_load(f)
    for key in config:
        os.environ[key] = str(config[key])


if __name__ == '__main__':
    extractor = AnilistExtractor()
    extractor.extract()
