from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from .models import User, Post
from .forms import RegisterForm, LoginForm, NewPost, EditUser
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
    post_body =  form.post_body.data.replace('\n', '<br />')
    title_slug = form.generate_slug(form.title.data)
    post = Post(title=form.title.data, title_slug=title_slug, body=post_body, timestamp = datetime.utcnow(), user_id=current_user.id)
    db.session.add(post)
    db.session.commit()
    flash("New post created successfully", "alert-success")
    return redirect(url_for('admin'))
  return render_template('new_post.html', title='Create New Post', form=form)
  
@app.route('/admin/edit_post/<id>', methods = ['GET', 'POST'])
@login_required
def edit_post(id):
  post = Post.query.get(id)
  form = NewPost(title=post.title, post_body=post.body)
  if form.validate_on_submit():
    post.title = form.title.data
    post.title_slug = form.generate_slug(form.title.data)
    post.body = form.post_body.data.replace('\n', '<br />')
    db.session.commit()
    return redirect(url_for('admin'))
  return render_template('edit_post.html', title = 'Edit Post', form=form)

@app.route('/admin/delete_post/<id>', methods = ['GET', 'POST'])
@login_required
def delete_post(id):
  post = Post.query.get(id)
  if request.method == 'POST':
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully!', 'alerlt-success')
    return redirect(url_for('admin'))
  return render_template('delete_post.html', title = 'Delete Post', post=post)
  
@app.route('/profile/<username>', methods=['GET'])
def user_profile(username):
  user = User.query.filter_by(username=username).first()
  return render_template('user.html', title=user.username+' Profile', user=user)

@app.route('/profile/<username>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(username):
  user = User.query.filter_by(username=username).first()
  form = EditUser(obj=user, orig_user=user.username, orig_email=user.email)
  if current_user.id != user.id:
    flash('Can only edit own profile!', 'alert-warning')
    return redirect(url_for('index'))
  if form.validate_on_submit():
    form.populate_obj(user)
    db.session.commit()
    flash('Profile edited successfully!', 'alert-success')
    return redirect(url_for('user_profile', username = user.username))
  return render_template('edit_user.html', title='Edit Profile: '+user.username, user=user, form=form)
  
@app.route('/post/<title_slug>')
def single_post(title_slug):
  post = Post.query.filter_by(title_slug = title_slug).first()
  return render_template('single_post.html', title=post.title+' - Blog', post=post)