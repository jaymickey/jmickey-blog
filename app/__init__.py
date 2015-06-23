from flask import Flask
from flask.ext.markdown import Markdown
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.moment import Moment
from flask.ext.bcrypt import Bcrypt

app = Flask(__name__)
app.config.from_object('config')
moment = Moment(app)
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
md = Markdown(app)

from app import views, models