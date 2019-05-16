from datetime import datetime
from blog import db

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column('id', db.Integer, index=True, primary_key=True)
    name = db.Column('name', db.String(64), unique=True)
    email = db.Column('email', db.String(120), unique=True)
    password = db.Column('password',db.String(128))
    user_approval = db.Column('user_approval', db.String(32))
    user_auth = db.Column('user_auth', db.String(32))
    message = db.Column('message', db.String(256))

    def __repr__(self):
        return '<User {}>'.format(self.email)

class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column('id', db.Integer, primary_key=True)
    author_id = db.Column('author_id', db.Integer, db.ForeignKey(User.id))
    author = db.Column('author', db.String(64))
    created = db.Column('created', db.DateTime, default=datetime.utcnow)
    real_date = db.Column('real_date', db.DateTime)
    title = db.Column('title', db.String(64))
    preview = db.Column('preview', db.String(140))
    preview_photo = db.Column('preview_photo', db.String())
    body = db.Column('body', db.String(5000))
    section = db.Column('section', db.String(20))
    post_auth = db.Column('post_auth', db.String(20))

    def __repr__(self):
        return '<Post {}>'.format(self.id)

class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column('id', db.Integer, primary_key=True)
    author_id = db.Column('author_id', db.Integer, db.ForeignKey(User.id))
    created = db.Column('created', db.DateTime, default=datetime.utcnow)
    body = db.Column('body', db.String(500))
    section = db.Column('section', db.String(20))
    article = db.Column('article', db.String(40))
    approval = db.Column('approval', db.String(20))

    def __repr__(self):
        return '<Comment {}>'.format(self.body)
