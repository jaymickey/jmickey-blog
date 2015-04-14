from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from .models import User
from .forms import RegisterForm, LoginForm
from app import app, db, lm
from werkzeug.security import generate_password_hash, check_password_hash

@lm.user_loader
def load_user(id):
  return User.query.get(int(id))

@app.route('/')
@app.route('/index')
def index():
  g.user = current_user
  return render_template('index.html', title='Blog Home')
  
@app.route('/register', methods=['GET', 'POST'])
def register():
  form = RegisterForm()
  if form.validate_on_submit():
    user = User(first_name=form.first_name.data, last_name=form.last_name.data, username=form.username.data, email=form.email.data)
    user.password = generate_password_hash(form.password.data)
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('index'))
  return render_template('register.html', title='Register', form = form)

@app.route('/login', methods = ['GET', 'POST'])
def login():
  form = LoginForm()
  if form.validate_on_submit():
    user = User.query.filter_by(username=form.username.data).first()
    login_user(user, remember=form.remember_me.data)
    return redirect(request.args.get('next') or url_for('index'))
  return render_template('login.html',title='Login', form=form)
  
@app.route('/logout', methods = ['GET'])
def logout():
  logout_user()
  return redirect(url_for('index'))