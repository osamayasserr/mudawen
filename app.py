from flask import Flask, render_template
from flask_bootstrap import Bootstrap

# Initialize the main flask application object
app = Flask(__name__)

# Initialize flask extensions
bootstrap = Bootstrap(app)


# Define a route that maps '/' -> index
@app.route('/')
def index():
    return render_template('index.html')


# Define a route that maps '/user/<name>' -> user
@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)
