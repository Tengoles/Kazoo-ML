import os
#import logging
from flask import Flask, request, jsonify
#import time
#import json
#import model_settings

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        #DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    #if test_config is None:
        # load the instance config, if it exists, when not testing
        #app.config.from_pyfile('config.py', silent=True)
    #else:
        # load the test config if passed in
    #app.config.from_mapping(test_config)

    # ensure the instance folder exists
    #try:
    #    os.makedirs(app.instance_path)
    #except OSError:
    #    pass
    from . import posts
    app.register_blueprint(posts.bp)
#    import logging
#    logging.basicConfig(filename=model_settings.LOG_FILE, level=logging.DEBUG)
    # here goes the routes
    @app.route("/home")
    def hello():
        return "Hello World!"
    return app

#app = create_app()

#if __name__ == "__main__":
    #app = create_app()
 #   app.run(host='0.0.0.0')
