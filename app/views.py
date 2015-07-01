from flask import (render_template, flash, redirect,
                   url_for, request, g)
from flask.ext.login import (login_user, logout_user,
                             current_user, login_required)
from wtforms.validators import ValidationError
from .models import User, Post, Tag, Page
from .forms import RegisterForm, LoginForm, PostForm, EditUser, PageForm
from app import app, db, lm, bcrypt
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


@app.context_processor
def get_all_tags():
    tags = Tag.query.order_by(Tag.name)
    return dict(all_tags=tags)


@app.context_processor
def get_all_pages():
    pages = Page.query.order_by(Page.id)
    return dict(all_pages=pages)


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
    posts = Post.query.filter_by(user_id=g.user.id)
    posts = posts.order_by(Post.id.desc())
    return render_template('admin.html', title='Admin Home', posts=posts)


@app.route('/admin/new_post', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post_title = form.title.data.lstrip().rstrip()
        post_short = form.post_short.data
        post_body = form.post_body.data
        try:
            title_slug = form.generate_slug(post_title)
        except ValidationError:
            form.title.errors.append('Title is already taken.')
        else:
            post = Post(title=post_title,
                        title_slug=title_slug,
                        short=post_short,
                        body=post_body,
                        timestamp=datetime.utcnow(),
                        user_id=g.user.id)
            tags = form.tags.data.split(', ')
            for tag in tags:
                if not Tag.query.filter(func.lower(Tag.name) ==
                                        tag.lower()).first():
                    new_tag = Tag(name=tag)
                    db.session.add(new_tag)
                    db.session.commit()
                get_tag = Tag.query.filter(func.lower(Tag.name) ==
                                           tag.lower()).first()
                post.tags.append(get_tag)
            db.session.add(post)
            db.session.commit()
            flash("New post created successfully", "alert-success")
            return redirect(url_for('admin'))
    return render_template('post_form.html',
                           title='Create New Post',
                           form=form)


@app.route('/admin/edit_post/<id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get(id)
    form = PostForm(title=post.title,
                    post_short=post.short,
                    post_body=post.body,
                    tags=', '.join([tag.name for tag in post.tags]))
    if form.validate_on_submit():
        try:
            post_title = form.title.data.lstrip().rstrip()
            if not post_title.lower() == post.title.lower():
                post.title_slug = form.generate_slug(post_title)
        except:
            form.title.errors.append('Title is already taken.')
        else:
            post.title = post_title
            post.short = form.post_short.data
            post.body = form.post_body.data
            tags = form.tags.data.split(', ')
            for tag in tags:
                if not Tag.query.filter(func.lower(Tag.name) ==
                                        tag.lower()).first():
                    new_tag = Tag(name=tag)
                    db.session.add(new_tag)
                    db.session.commit()
                tag = Tag.query.filter(func.lower(Tag.name) ==
                                       tag.lower()).first()
                if tag not in post.tags:
                    post.tags.append(tag)
            db.session.commit()
            flash("Edited post successfully", "alert-success")
            return redirect(url_for('admin'))
    return render_template('post_form.html', title='Edit Post', form=form)


@app.route('/admin/delete_post/<id>', methods=['GET', 'POST'])
@login_required
def delete_post(id):
    post = Post.query.get(id)
    if request.method == 'POST':
        db.session.delete(post)
        db.session.commit()
        if post.tags:
            for tag in post.tags:
                if not tag.posts.count():
                    db.session.delete(tag)
                    db.session.commit()
        flash('Post deleted successfully!', 'alert-success')
        return redirect(url_for('admin'))
    return render_template('delete_post.html', title='Delete Post', post=post)


@app.route('/profile/<username>')
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
    user = User.query.filter(func.lower(User.username) ==
                             username.lower()).first()
    form = EditUser(obj=user, orig_user=user.username, orig_email=user.email)
    if not g.user.id == user.id and not g.user.is_admin:
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


@app.route('/admin/new_page', methods=['GET', 'POST'])
@login_required
def new_page():
    form = PageForm()
    if form.validate_on_submit():
        page = Page()
        form.populate_obj(page)
        try:
            page.title_slug = form.generate_slug(form.title.data)
        except ValidationError:
            form.title.errors.append('Title is already taken.')
        else:
            db.session.add(page)
            db.session.commit()
            flash('Page created successfully!', 'alert-success')
            return redirect(url_for('admin'))
    return render_template('page_form.html',
                           title='New Page',
                           form=form)


@app.route('/admin/edit_page/<id>', methods=['GET', 'POST'])
def edit_page(id):
    page = Page.query.get(id)
    form = PageForm(obj=page)
    if form.validate_on_submit():
        if not form.title.data.lower() == page.title.lower():
            pass
    return render_template('page_form.html',
                           title='Edit Page',
                           form=form)


@app.route('/page/<page_slug>')
def page(page_slug):
    page = Page.query.filter(func.lower(Page.title_slug) ==
                             page_slug.lower()).first()
    return render_template('page.html',
                           title=page.title,
                           page=page)
