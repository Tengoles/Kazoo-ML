import os
#import logging
from flask import Flask, request, jsonify
#import model_settings

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        #DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    from . import posts
    app.register_blueprint(posts.bp)
#    import logging
#    logging.basicConfig(filename=model_settings.LOG_FILE, level=logging.DEBUG)
    # here goes the routes
    @app.route("/home")
    def hello():
        return "Plataforma de Machine Learning de Kazoo"
    return app
