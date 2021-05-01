from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, Regexp
from wtforms import ValidationError, Label
from flask_pagedown.fields import PageDownField
from flask_login import current_user
from ..models import Role, User


# Flask-WTF renders the name form
class NameForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditProfileForm(FlaskForm):
    name = StringField('Name', validators=[Length(0, 64)],
                       render_kw={'placeholder': 'Full name'})
    location = StringField('Location', validators=[Length(0, 64)],
                           render_kw={'placeholder': 'City, Country'})
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),
                        Length(1, 64), Email()])
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or '
               'underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class PostForm(FlaskForm):
    body = PageDownField('What\'s on your mind?', validators=[DataRequired()])
    submit = SubmitField('Post')


class CommentForm(FlaskForm):
    body = StringField('', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, post, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.body.label = Label(self.body.id, f'Reply to {post.author.username}\'s post')
