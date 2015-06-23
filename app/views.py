from flask import (render_template, flash, redirect,
                   session, url_for, request, g)
from flask.ext.login import (login_user, logout_user,
                             current_user, login_required)
from wtforms.validators import ValidationError
from .models import User, Post, Tag
from .forms import RegisterForm, LoginForm, NewPost, EditUser
from app import app, db, lm, md, bcrypt
from datetime import datetime
from sqlalchemy import func


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/')
@app.route('/index')
def index():
    posts = Post.query.order_by(Post.id.desc())
    return render_template('index.html',
                           title='Blog Home',
                           posts=posts)


@app.before_request
def before_request():
    g.user = current_user


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User()
        form.populate_obj(user)
        user.password = bcrypt.generate_password_hash(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration Successful, you can now login', 'alert-success')
        return redirect(url_for('index'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data.lower()
        user = User.query.filter(func.lower(User.username) ==
                                 username.lower()).first()
        login_user(user, remember=form.remember_me.data)
        return redirect(request.args.get('next') or url_for('index'))
    return render_template('login.html', title='Login', form=form)


@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/admin')
@login_required
def admin():
    posts = Post.query.filter_by(user_id=current_user.id)
    posts = posts.order_by(Post.id.desc())
    return render_template('admin.html', title='Admin Home', posts=posts)


@app.route('/admin/new_post', methods=['GET', 'POST'])
@login_required
def new_post():
    form = NewPost()
    if form.validate_on_submit():
        post_short = form.post_short.data
        post_body = form.post_body.data
        try:
            title_slug = form.generate_slug(form.title.data)
        except ValidationError:
            form.title.errors.append('Title is already taken.')
        else:
            post = Post(title=form.title.data,
                        title_slug=title_slug,
                        short=post_short,
                        body=post_body,
                        timestamp=datetime.utcnow(),
                        user_id=current_user.id)
        tags = form.tags.data.split(', ')
        for tag in tags:
            if Tag.query.filter(func.lower(Tag.name) == tag.lower()).first():
                pass
            else:
                new_tag = Tag(name=tag)
                db.session.add(new_tag)
                db.session.commit()
            tag = Tag.query.filter(func.lower(Tag.name) == tag.lower()).first()
            post.tags.append(tag)
        db.session.add(post)
        db.session.commit()
        flash("New post created successfully", "alert-success")
        return redirect(url_for('admin'))
    return render_template('new_post.html', title='Create New Post', form=form)


@app.route('/admin/edit_post/<id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get(id)
    form = NewPost(title=post.title,
                   post_short=post.short,
                   post_body=post.body,
                   tags=', '.join([tag.name for tag in post.tags]))
    if form.validate_on_submit():
        if form.title.data.lower() != post.title.lower():
            post.title = form.title.data
            post.title_slug = form.generate_slug(form.title.data,
                                                 orig_title=post.title)
        post.short = form.post_short.data
        post.body = form.post_body.data
        tags = form.tags.data.split(', ')
        for tag in tags:
            if Tag.query.filter(func.lower(Tag.name) == tag.lower()).first():
                pass
            else:
                new_tag = Tag(name=tag)
                db.session.add(new_tag)
                db.session.commit()
            tag = Tag.query.filter(func.lower(Tag.name) == tag.lower()).first()
            if tag in post.tags:
                continue
            post.tags.append(tag)
        db.session.commit()
        flash("Edited post successfully", "alert-success")
        return redirect(url_for('admin'))
    return render_template('edit_post.html', title='Edit Post', form=form)


@app.context_processor
def get_all_tags():
    tags = Tag.query.order_by(Tag.name)
    return dict(all_tags=tags)


@app.route('/admin/delete_post/<id>', methods=['GET', 'POST'])
@login_required
def delete_post(id):
    post = Post.query.get(id)
    if request.method == 'POST':
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted successfully!', 'alerlt-success')
        return redirect(url_for('admin'))
    return render_template('delete_post.html', title='Delete Post', post=post)


@app.route('/profile/<username>', methods=['GET'])
def user_profile(username):
    user = User.query.filter(func.lower(User.username) ==
                             username.lower()).first()
    posts = Post.query.filter_by(user_id=user.id)
    return render_template('user.html',
                           title=user.username+' Profile',
                           user=user,
                           posts=posts)


@app.route('/profile/<username>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(username):
    user = User.query.filter(func.lower(username) == username.lower()).first()
    form = EditUser(obj=user, orig_user=user.username, orig_email=user.email)
    if current_user.id != user.id:
        flash('Can only edit own profile!', 'alert-warning')
        return redirect(url_for('index'))
    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.commit()
        flash('Profile edited successfully!', 'alert-success')
        return redirect(url_for('user_profile', username=user.username))
    return render_template('edit_user.html',
                           title='Edit Profile: '+user.username,
                           user=user,
                           form=form)


@app.route('/post/<title_slug>')
def single_post(title_slug):
    post = Post.query.filter_by(title_slug=title_slug).first()
    return render_template('single_post.html',
                           title=post.title+' - Blog',
                           post=post)


@app.route('/tag/<tag>')
def tag(tag):
    tag = Tag.query.filter(func.lower(Tag.name) == tag.lower()).first()
    return render_template('tag.html', title='Posts under '+tag.name, tag=tag)
