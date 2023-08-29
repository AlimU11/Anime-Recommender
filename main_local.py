"""Local version of the app. Run this file to start the app locally."""

from anime_recommender.ui.app import app  # noqa

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=True, port=8050)
