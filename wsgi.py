# This file contains the WSGI configuration required to serve up web application

import os
import sys

import yaml

project_home = '/home/AlimU/anime_recommender'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# load config variables to environment variables
with open('global_config.yaml', 'r') as f:
    config = yaml.safe_load(f)
    for key in config:
        os.environ[key] = str(config[key])

# import flask app but need to call it "application" for WSGI to work
from main import app as application  # noqa # isort:skip

from main import app  # isort:skip

application = app.server
