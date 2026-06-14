import os

from dotenv import load_dotenv

from flask import Flask, render_template
from flask_login import LoginManager, login_required

load_dotenv()

login_manager = LoginManager()
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.get_by_id(user_id)


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY"),
        DATABASE=os.path.join(app.instance_path, 'db.sqlite3'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    @app.route('/')
    @login_required
    def main_page():
        return render_template('index.html')

    from . import db
    db.init_app(app)
    
    from . import auth
    app.register_blueprint(auth.auth_bp)

    from . import main
    app.register_blueprint(main.main_bp)

    from app.commands import create_user, populate_database
    app.cli.add_command(create_user)
    app.cli.add_command(populate_database)
    
    login_manager.init_app(app)

    return app
