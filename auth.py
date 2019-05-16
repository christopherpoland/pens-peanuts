from blog import app
import functools
from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash
from blog import db
from blog.models import User
import sys

bp = Blueprint('auth', __name__, url_prefix='/')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        message = request.form['message']
        approval = "pending"
        user_auth = "peasant"
        error = None

        if not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        elif not name:
            error = 'Name is required.'
        elif User.query.filter_by(email=email).first() is not None: # there is an account with email
            if User.query.filter_by(email=email).password is None:
                user = User(name=name, email=email, password=generate_password_hash(password), user_approval=approval, user_auth=user_auth, message=message)
                db.session.add(user)
                db.session.commit()
            else: # already registered

                if User.query.filter_by(email=email).user_approval == 'pending':
                    error = 'Account waiting to be approved.'
                    flash(error)
                    return redirect(url_for('main.display'))
                elif User.query.filter_by(email=email).user_approval == 'approved':
                    error = 'Please Log In.'
                    return redirect(url_for('auth.login'))

        elif error is None:
            new_user = User(name=name, email=email, password=generate_password_hash(password), user_approval=approval, user_auth=user_auth, message=message)
            db.session.add(new_user)
            db.session.commit()
            flash("Account awaiting approval")
            return redirect(url_for('main.display'))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None
        user = User.query.filter_by(email=email).first()
        if user is None:
            error = 'Incorrect email.'
        elif not check_password_hash(user.password, password):
            error = 'Incorrect password.'
        elif user.user_approval == 'pending':
            error = 'Account waiting to be approved.'
        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('main.display'))
        flash(error)
    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        session.user = None
    else:
        session.user = User.query.filter_by(id=user_id).first()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.display'))
