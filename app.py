import os
from datetime import datetime
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

# Initialize the main flask application object
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or os.urandom(32)

# Initialize flask extensions
bootstrap = Bootstrap(app)
moment = Moment(app)


class NameForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Submit')


# Define a route that maps '/' -> index
@app.route('/', methods=['GET', 'POST'])
def index():
    name = session.get('name')
    form = NameForm()
    if form.validate_on_submit():
        if form.name.data != name and name is not None:
            flash('Looks like you have changed your name!')
        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=name)


# Define a route that maps '/user/<name>' -> user
@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500
