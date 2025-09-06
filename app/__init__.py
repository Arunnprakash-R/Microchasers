import os
from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from .database import db

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Load the default configuration
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:///microchasers.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)
    login = LoginManager(app)
    login.login_view = 'auth.login'

    from . import models

    from .auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from .main import bp as main_bp
    app.register_blueprint(main_bp)

    from .api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    @login.user_loader
    def load_user(id):
        return models.User.query.get(int(id))

    return app
