from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.admin import Admin
from .admin import *
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

admin = Admin(app, index_view=AdminIndex())

from app import views, models