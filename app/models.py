from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(40))
    last_name = db.Column(db.String(40))
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(64))
    about_me = db.Column(db.String(200))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '%r' % (self.username)


post_tags = db.Table('tags',
                     db.Column('tag_id',
                               db.Integer,
                               db.ForeignKey('tag.id')),
                     db.Column('post_id',
                               db.Integer,
                               db.ForeignKey('post.id'))
                     )


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), index=True, unique=True)
    title_slug = db.Column(db.String(), unique=True)
    short = db.Column(db.String())
    body = db.Column(db.String())
    timestamp = db.Column(db.DateTime)
    tags = db.relationship('Tag', secondary=post_tags,
                           backref=db.backref('posts', lazy='dynamic'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Tag(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(24), unique=True)
