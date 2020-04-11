# Contains the APP factory and tells flask that app should be treated as a package 
import os

from flask import Flask

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=b'%&\xf6\xb6\xf4u\xd0Z\x89\x99\x92\x98\x00)\xa3\xed',
        DATABASE=os.path.join(app.instance_path, 'workojo.sqlite'),
    )
        
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db, auth, log
    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(log.bp)

    @app.route('/')
    @app.route('/hello')
    def hello():
        return 'Welcome to workojo!'
    
    return app