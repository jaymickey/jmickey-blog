from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, ValidationError
from app.models import User, Post
from app import bcrypt
from unidecode import unidecode
from sqlalchemy import func
import re


class LoginForm(Form):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=8)])
    remember_me = BooleanField('Remember Me', default=False)

    def validate_username(self, field):
        user = User.query.filter(func.lower(User.username) ==
                                 self.username.data.lower()).first()
        if user is None:
            raise ValidationError('User does not exist')

    def validate_password(self, field):
        user = User.query.filter(func.lower(User.username) ==
                                 self.username.data.lower()).first()
        if user:
            if not bcrypt.check_password_hash(user.password,
                                              self.password.data):
                raise ValidationError('Password is incorrect')


class RegisterForm(Form):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

    def validate_username(self, field):
        if User.query.filter(func.lower(User.username) ==
                             self.username.data.lower()).count() > 0:
            raise ValidationError('Username already exists.')

    def validate_email(self, field):
        if User.query.filter(func.lower(User.email) ==
                             self.email.data.lower()).count() > 0:
            raise ValidationError('Email already in use.')


class PostForm(Form):
    title = StringField('Title',
                        validators=[DataRequired("Please enter a title!")])
    post_short = TextAreaField('Short Post')
    post_body = TextAreaField('Post Body',
                              validators=[DataRequired("Please enter a post body!")])
    tags = StringField('Tags',
                       validators=[DataRequired("Please enter post tags!")])

    def generate_slug(self, title):
        title_slug = re.sub(r'\W+', '-',
                            unidecode(title).lower().rstrip(r' .?!(),[]{}'))
        if Post.query.filter_by(title_slug=title_slug).count() > 0:
            raise ValidationError('Title is already taken')
        return title_slug


class EditUser(Form):
    first_name = StringField('First Name',
                             validators=[DataRequired("First name is required!")])
    last_name = StringField('Last Name',
                            validators=[DataRequired("Last name is required!")])
    username = StringField('Username',
                           validators=[DataRequired("Username is required!")])
    email = StringField('Email Address',
                        validators=[DataRequired("Email is required!"), Email()])
    about_me = TextAreaField('About Me',
                             validators=[Length(max=200, message="About me must be less than 200 characters!")])

    def __init__(self, orig_user, orig_email, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.orig_user = orig_user
        self.orig_email = orig_email

    def validate_username(self, field):
        if self.orig_user and self.username.data.lower() == self.orig_user.lower():
            return True
        if User.query.filter(func.lower(User.username) ==
                             self.username.data.lower()).count() > 0:
            raise ValidationError('Username is taken.')

    def validate_email(self, field):
        if self.orig_email and self.email.data.lower() == self.orig_email.lower():
            return True
        if User.query.filter(func.lower(User.email) ==
                             self.email.data.lower()).count() > 0:
            raise ValidationError('Email already exists.')


class PageForm(Form):
    title = StringField('Page Title',
                        validators=[DataRequired("Page must have a title")])
    content = TextAreaField('Page Content',
                            validators=[DataRequired("Page must have content")])

    def generate_slug(self, title):
        title_slug = re.sub(r'\W+', '-',
                            unidecode(title).lower().rstrip(r' .?!(),[]{}'))
        if Page.query.filter_by(title_slug=title_slug).count() > 0:
            raise ValidationError('Title is already taken')
        return title_slug
