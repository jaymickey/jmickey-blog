from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from .models import User, Post
from .forms import RegisterForm, LoginForm, NewPost
from app import app, db, lm, md
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

@lm.user_loader
def load_user(id):
  return User.query.get(int(id))

@app.route('/')
@app.route('/index')
def index():
  g.user = current_user
  posts = Post.query.order_by(Post.id.desc())
  return render_template('index.html', title='Blog Home', posts=posts)
  
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
  
@app.route('/admin')
@login_required
def admin():
  posts = Post.query.filter_by(user_id = current_user.id)
  posts = posts.order_by(Post.id.desc())
  return render_template('admin.html', title='Admin Home', posts = posts)
  
@app.route('/admin/new_post', methods = ['GET', 'POST'])
@login_required
def new_post():
  form = NewPost()
  if form.validate_on_submit():
    post = Post(title=form.title.data, body=form.post_body.data, timestamp = datetime.utcnow(), user_id=current_user.id)
    db.session.add(post)
    db.session.commit()
    new_post_message = flash("New post created successfully")
    return redirect(url_for('admin'))
  return render_template('new_post.html', title='Create New Post', form=form)
  
@app.route('/admin/edit_post/<id>', methods = ['GET', 'POST'])
@login_required
def edit_post(id):
  post = Post.query.get(id)
  form = NewPost(title=post.title, post_body=post.body)
  if form.validate_on_submit():
    post.title = form.title.data
    post.body = form.post_body.data
    db.session.commit()
    return redirect(url_for('admin'))
  return render_template('edit_post.html', form=form)