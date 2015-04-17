from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, ValidationError
from app.models import User
from app import db
from werkzeug.security import check_password_hash

class LoginForm(Form):
  username = StringField('Username', validators = [DataRequired()])
  password = PasswordField('Password', validators = [DataRequired(), Length(min = 8)])
  remember_me = BooleanField('Remember Me', default = False)

  def validate_username(self, field):
    user = db.session.query(User).filter_by(username=self.username.data).first()
    if user == None:
      raise ValidationError('User does not exist')

  def validate_password(self, field):
    user = db.session.query(User).filter_by(username=self.username.data).first()
    if user != None:
      if not check_password_hash(user.password, self.password.data):
        raise ValidationError('Password is incorrect')
  
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

class NewPost(Form):
  title = StringField('Title', validators = [DataRequired("Please enter a title!")])
  post_body = TextAreaField('Post Body', validators = [DataRequired("Please enter a post body!")])
  tags = StringField('Tags', validators = [DataRequired("Please enter post tags!")])
  