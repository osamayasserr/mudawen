from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_login import LoginManager
from flask_pagedown import PageDown
from config import config

db = SQLAlchemy()
mail = Mail()
moment = Moment()
bootstrap = Bootstrap()
pagedown = PageDown()

# Initializes flask-login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'


# Application factory function
def create_app(environment):
    # Creates and configures the flask app
    app = Flask(__name__)
    app.config.from_object(config[environment])
    config[environment].init_app(app)

    # Initializes flask extensions
    bootstrap.init_app(app)
    db.init_app(app)
    moment.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)

    # Registers the main blueprint
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Registers the auth blueprint
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
