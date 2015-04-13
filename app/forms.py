from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Length, Email, ValidationError
from app.models import User
from app import db

class LoginForm(Form):
  username = StringField('username', validators = [DataRequired()])
  password = StringField('password', validators = [DataRequired(), Length(min = 8)])
  remember_me = BooleanField('remember_me', default = False)
  
class RegisterForm(Form):
  first_name = StringField('First Name', validators = [DataRequired()])
  last_name = StringField('Last Name', validators = [DataRequired()])
  username = StringField('Username', validators = [DataRequired()])
  email = StringField('Email Address', validators = [DataRequired(), Email()])
  password = PasswordField('Password', validators = [DataRequired()])
  
  def validate_username(self, field):
    if db.session.query(User).filter_by(username=self.username.data).count() > 0:
      raise ValidationError('Username already exists.')
  
  def validate_email(self, field):
    if db.session.query(User).filter_by(email=self.email.data).count() > 0:
      raise ValidationError('Email already in use.')