from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from .models import User
from .forms import RegisterForm
from app import app, db, lm
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/')
@app.route('/index')
def index():
  return None
  
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