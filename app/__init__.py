from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from config import config

db = SQLAlchemy()
mail = Mail()
moment = Moment()
bootstrap = Bootstrap()


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

    # Registers Blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
