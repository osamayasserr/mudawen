from flask import Flask

# Initialize the main flask application object
app = Flask(__name__)


# Define a route that maps '/' -> index
@app.route('/')
def index():
    return '<h1>Hello, World!</h1>'


# Define a route that maps '/user/<name>' -> user
@app.route('/user/<name>')
def user(name):
    return f'<h1>Hello, {name.title()}!</h1>'
