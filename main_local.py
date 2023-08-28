# version of main for local tests

import yaml

from anime_recommender.ui.app import app  # noqa

# load config variables to environment variables
# with open('global_config.yaml', 'r') as f:
#     config = yaml.safe_load(f)
#     for key in config:
#         os.environ[key] = str(config[key])


if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=True, port=8050)
