import functools

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from blog import db, ALLOWED_EXTENSIONS, app
from blog.models import User, Post, Comment
import os
from datetime import date, time, datetime, timedelta
import time
import pytz
from pytz import timezone
from tzlocal import get_localzone
import re
import sys
from flask import Markup, send_from_directory
from werkzeug.utils import secure_filename


main = Blueprint('main', __name__, url_prefix="/")

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not session.user:
            flash("Page not accesible without author permissions")
            return redirect(url_for('main.display'))
        u = User.query.filter_by(email=session.user.email).first()
        if session.user.user_auth != 'dev':
            flash("Page not accesible without author permissions")
            return redirect(url_for('main.display'))
        elif session.user.user_approval == 'pending' or session.user.user_approval is None:
            flash("Page not accesible without registered account")
            return redirect(url_for('main.display'))
        return view(**kwargs)
    return wrapped_view

def author_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not session.user:
            flash("Page not accesible without author permissions")
            return redirect(url_for('main.display'))
        elif session.user.user_approval != 'author':
            flash("Page not accesible without author permissions")
            return redirect(url_for('main.display'))
        return view(**kwargs)
    return wrapped_view

def author_required_edit(edit):
    @functools.wraps(edit)
    def wrapped_view(**kwargs):
        p = Post.query.filter_by(title=kwargs['article']).first()
        if not session.user:
            flash("Page not accesible without author permissions")
            return redirect(url_for('main.display'))
        elif session.user.user_approval != 'author':
                flash("Page not accesible without author permissions")
                return redirect(url_for('main.display'))
        elif session.user.id != p.author_id and session.user.user_auth != 'dev':
            flash("Page not accesible without having created the post")
            return redirect(url_for('main.display'))
        return edit(**kwargs)
    return wrapped_view

@main.route('/', methods=('GET', 'POST'))
def display():
    if request.method == 'POST':
        if session.user is None:
            name = request.form['name']
            email = request.form['email']
        else:
            name = session.user.name
            email = session.user.email
        comment = request.form['comment']
        article = request.form['article']
        section = request.form['section']
        status = 'pending'
        error = None

        if not name:
            error = 'Please include your name.'
        elif not email:
            error = 'Please include your email.'
        elif not comment:
            error = 'Please include a comment.'
        elif not re.match("[^@]+@[^@]+", email): # regex based on javascript side
            error = 'Please correct email.'
        if error is None:
            existing_name = User.query.filter_by(email=email).first()
            if existing_name is None:
                user = User(name=name, email=email)
                db.session.add(user)
                db.session.commit()
                existing_name = User.query.filter_by(email=email).first()
            author_id = existing_name.id

            if session.user == None or session.user.user_approval == 'pending':
                flash("Comment awaiting approval")
            elif session.user.user_approval == 'author' or session.user.user_approval == 'approved':
                status = 'approved' # bypass comment approval if user is an author
                flash("Comment posted")
            comment_add = Comment(author_id=author_id,body=comment,section=section,article=article,approval=status)
            db.session.add(comment_add)
            db.session.commit()
            return redirect(url_for('main.display', category=section))

    articles = Post.query.filter_by(post_auth="approved").order_by(Post.created.desc()).limit(3).all()
    posts = User.query.join(Comment, Comment.author_id==User.id).add_columns(User.name, Comment.body, Comment.section, Comment.created, Comment.author_id, Comment.article, Comment.approval).order_by(Comment.created.desc()).all()
    local_tz = get_localzone()
    return render_template('page-dir/main.html', articles=articles, posts=posts, Markup=Markup, datetime=datetime, str=str, timezone=timezone, local_tz=local_tz)

@main.route('/users', methods=('GET', 'POST'))
@login_required
def users():
    if request.method == 'POST':
        user_status = request.form['approve_user']
        id = request.form['user']
        if user_status == "delete":
            user_to_del = User.query.filter_by(id=id).first()
            if user_to_del.user_auth == "dev":
                flash("Unable to delete master user")
            else:
                comments_to_del = Comment.query.filter_by(author_id=id).all()
                for c in comments_to_del:
                    db.session.delete(c)
                db.session.delete(user_to_del)
                flash("User deleted")
            db.session.commit()
        else:
            user_to_alter = User.query.filter_by(id=id).first()
            user_to_alter.user_approval = user_status
            db.session.commit()
            flash("User updated")

    users = User.query.order_by(User.name.asc()).all()

    return render_template('users.html', users=users)

@main.route('/posts', methods=('GET', 'POST'))
@login_required
def posts():
    if request.method == 'POST':
        status = request.form['approve_post']
        id = request.form['id']
        if status == "delete":
            post_to_del = Post.query.filter_by(id=id).first()
            comments_to_del = Comment.query.filter_by(author_id=id).all()
            for c in comments_to_del:
                db.session.delete(c)
            if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], post_to_del.preview_photo)):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], post_to_del.preview_photo))
            db.session.delete(post_to_del)
            flash("Post deleted")
            db.session.commit()
        else:
            post_to_alter = Post.query.filter_by(id=id).first()
            post_to_alter.post_auth = status
            db.session.commit()
            flash("Post approved")

    posts_pend = Post.query.filter_by(post_auth="pending").order_by(Post.created.asc()).all()
    posts_app = Post.query.filter_by(post_auth="approved").order_by(Post.created.asc()).all()
    return render_template('posts.html', posts_pend=posts_pend, posts_app=posts_app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@main.route('/create', methods=('GET', 'POST'))
@author_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        author = session.user.name
        date = request.form['real-date']
        section = request.form['section']
        preview = request.form['create-preview']
        body = request.form['create-body']
        file = request.files['file']
        error = None

        if not title:
            error = 'Please include a title.'
        elif not date:
            error = 'Please include the date.'
        elif not preview:
            error = 'Please include a preview.'
        elif not body:
            error = 'Please include a body.'
        elif 'file' not in request.files:
            error = 'No file part'
        elif file.filename == '':
            error = 'No selected file'
        elif not allowed_file(file.filename):
            flash('Filetype not accepted')
            return redirect(request.url)
        if error is None:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                print(filename, file=sys.stderr)
            if session.user.user_auth == "peasant":
                post_auth = "pending"
                flash("Submission awaiting approval")
            elif session.user.user_auth == "dev":
                post_auth = "approved"
                flash("Submission Posted")
            post = Post(author_id=session.user.id, author=author, real_date=date, title=title,preview=preview,body=body,section=section,post_auth=post_auth, preview_photo=filename)
            db.session.add(post)
            db.session.commit()

            return redirect(url_for('page-dir.show', category=section))

    return render_template('create.html')

@main.route('/edit/<article>', methods=('GET', 'POST'))
@author_required_edit
def edit(article):
    post = Post.query.filter_by(title=article).first()
    print(os.path.join(app.config['UPLOAD_FOLDER'], post.preview_photo), file=sys.stderr)
    if request.method == 'POST':
        title = request.form['title']
        date = request.form['real-date']
        section = request.form['section']
        preview = request.form['create-preview']
        body = request.form['create-body']
        file = request.files['file']
        error = None
        if not title:
            error = 'Please include a title.'
        elif not date:
            error = 'Please include the date.'
        elif not preview:
            error = 'Please include a preview.'
        elif not body:
            error = 'Please include a body.'
        if file.filename != '':
            if 'file' not in request.files:
                error = 'No file part'
            elif not allowed_file(file.filename):
                flash('Filetype not accepted')
                #return redirect(request.url)
        if error is None:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], post.preview_photo)):
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], post.preview_photo))
                print(post.preview_photo, file=sys.stderr)
                post.preview_photo = filename
            post.title = title
            post.real_date = date
            post.section = section
            post.preview = preview
            post.body = body
            db.session.commit()
            flash("Post updated")
        return redirect(url_for('page-dir.show', category=section))
    data = Post.query.filter_by(title=article).first()

    return render_template('edit.html', data=data, str=str, datetime=datetime)

@main.route('/approve', methods=('GET', 'POST'))
@login_required
def approve():
    status = 'pending'

    if request.method == 'POST':
        result = request.form['approve_comment']
        id = request.form['id']
        error = None

        if error is None:
            id = request.form['id']
            if result == "approved":
                comment = Comment.query.filter_by(id=id).first()
                comment.approval = "approved"
            elif result == "delete":
                comment = Comment.query.filter_by(id=id).first()
                db.session.delete(comment)
            db.session.commit()

    posts = User.query.join(Comment, Comment.author_id==User.id).filter_by(approval="pending").add_columns(User.name, Comment.body, Comment.section, Comment.created, Comment.id, Comment.author_id, Comment.article, Comment.approval).order_by(Comment.created.desc()).all()


    return render_template('approve.html', posts=posts, users=users)


@main.route('/upload', methods=('GET', 'POST'))
@login_required
def upload():
    if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            elif not allowed_file(file.filename):
                flash('Filetype not accepted')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return redirect(url_for('main.uploaded_file', filename=filename))
    return render_template('upload.html')

@main.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

categories = Blueprint('page-dir', __name__, url_prefix='/<category>')
@categories.route('/', methods=('GET', 'POST'))
def show(category):
    if category != 'pens' and category != 'pages' and category != 'people' and category != 'places' and category != 'peanuts':
        return render_template('404.html')
    if request.method == 'POST':
        if session.user is None:
            name = request.form['name']
            email = request.form['email']
        else:
            name = session.user.name
            email = session.user.email
        comment = request.form['comment']
        article = request.form['article']
        status = 'pending'
        error = None

        if not name:
            error = 'Please include your name.'
        elif not email:
            error = 'Please include your email.'
        elif not comment:
            error = 'Please include a comment.'
        elif not re.match("[^@]+@[^@]+", email): # regex based on javascript side
            error = 'Please correct email.'
        if error is None:
            existing_name = User.query.filter_by(email=email).first()
            if existing_name is None:
                user = User(name=name, email=email)
                db.session.add(user)
                db.session.commit()
                existing_name = User.query.filter_by(email=email).first()
            author_id = existing_name.id

            if session.user == None or session.user.user_approval == 'pending':
                flash("Comment awaiting approval")
            elif session.user.user_approval == 'author' or session.user.user_approval == 'approved':
                status = 'approved' # bypass comment approval if user is an author
                flash("Comment posted")
            comment_add = Comment(author_id=author_id,body=comment,section=category,article=article,approval=status)
            db.session.add(comment_add)
            db.session.commit()
            return redirect(url_for('page-dir.show', category=category))
    articles = Post.query.filter_by(post_auth="approved",section=category).order_by(Post.created.desc()).all()
    posts = User.query.join(Comment, Comment.author_id==User.id).add_columns(User.name, Comment.body, Comment.section, Comment.created, Comment.author_id, Comment.article, Comment.approval).order_by(Comment.created.desc()).all()

    local_tz = get_localzone()

    return render_template('page-dir/pens.html', articles=articles, posts=posts, datetime=datetime, str=str, timezone=timezone, local_tz=local_tz, category=category, Markup=Markup)
