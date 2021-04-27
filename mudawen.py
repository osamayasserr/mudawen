import os
from app import create_app, db
from flask_migrate import Migrate
from app.models import User, Role, Permission, Post

# Creates the application instance by invoking the factory function
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


# Makes db, User & role available in flask shell
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, Permission=Permission, Post=Post)


# Creates a cli command 'flask test' to run unittests
@app.cli.command()
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
