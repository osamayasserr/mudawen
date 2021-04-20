from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from flask_login import current_user
from ..models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
                        DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[
                        DataRequired(), Length(1, 64), Email()])
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must only have letters, numbers, dots or '
               'underscores')])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email already registerd.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already taken.')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old password', validators=[DataRequired()])
    new_password = PasswordField('New password', validators=[DataRequired()])
    comfirm_new = PasswordField('Confirm password', validators=[
        DataRequired(), EqualTo('new_password', message='Passwords must match.')])
    submit = SubmitField('Update & Logout')

    def validate_old_password(self, field):
        if not current_user.verify_password(field.data):
            raise ValidationError('Incorrect password.')


class RequestPasswordResetForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(), Length(1, 64), Email()])
    submit = SubmitField('Send Mail')

    def validate_email(self, field):
        if not User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('The email you entered is not registered.')


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField('New password', validators=[DataRequired()])
    confirm_new = PasswordField('Confirm password', validators=[
        DataRequired(), EqualTo('new_password', message='Passwords must match')])
    submit = SubmitField('Update Password')


class ChangeEmailForm(FlaskForm):
    new_email = StringField('New email', validators=[
        DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_new_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email already registered.')
        if current_user.email == field.data:
            raise ValidationError('New email can not be the current one.')
