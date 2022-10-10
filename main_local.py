# version of main for local tests
import os

import yaml

# load config variables to environment variables
with open('global_config.yaml', 'r') as f:
    config = yaml.safe_load(f)
    for key in config:
        os.environ[key] = str(config[key])

from anime_recommender.ui import app  # noqa

if __name__ == '__main__':
    app.run_server(debug=True)
