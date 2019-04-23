import logging
from flask import Flask

from http_handler.views import auth, main, photos
log = logging.getLogger(__name__)


def create_http_app(config):
    """
    Create new http application with selected config

    :param config: Object config for app
    :return: Http application
    """
    app = Flask(__name__)
    app.config.from_object(config)

    if app.debug:
        from flask_debugtoolbar import DebugToolbarExtension
        _ = DebugToolbarExtension(app)

    app.register_blueprint(main.blueprint)
    app.register_blueprint(auth.blueprint)
    app.register_blueprint(photos.blueprint, url_prefix="/myphotos")
    return app
