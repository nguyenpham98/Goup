from app import app, db, images
from flask import render_template, request, redirect, url_for, flash, send_from_directory, current_app
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models import User, Post, Photo
import os
from app.email import send_password_reset_email
from datetime import datetime
from flask_uploads import UploadNotAllowed

@app.before_request # insert code before view function
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow() # update the time
        db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data) # flask_login remember_me

        next_page = request.args.get('next') # handles login_required
        if not next_page or url_parse(next_page).netloc != '': # url_parse for security purposes
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form=RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You are now a register user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    # paginate
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.timestamp.desc()).paginate(page=page, per_page=app.config['POSTS_PER_PAGE'])
    # navigation
    next_url = url_for('profile', username=user.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('profile', username=user.username, page=posts.prev_num) if posts.has_prev else None

    return render_template('user.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url)

@app.route('/edit_profile', methods=['POST','GET'])
@login_required
def edit_profile():

    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        return redirect(url_for('profile', username=current_user.username))
    elif request.method=='GET': # current username and about_me
        form.username.data=current_user.username
        form.about_me.data=current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@app.route('/discussion', methods=['GET','POST'])
@login_required
def discussion():
    post_form=PostForm()

    if post_form.post_submit.data and post_form.validate_on_submit():
        post = Post(body=post_form.post.data, author=current_user)
        if request.files['files'].filename!='': # photo is optional. Check if file requested in form is not blank
            for file in post_form.files.data:
                try:
                    filename = images.save(file)
                    photo = Photo(filename=filename, post=post)
                    db.session.add(photo)
                except UploadNotAllowed:
                    flash('File Format Not Allowed.')
                    return redirect(url_for('discussion'))

        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('discussion'))

    posts = Post.query.order_by(Post.timestamp.desc()).all()
    photos = Photo.query.order_by(Photo.timestamp.desc()).all()


    return render_template('discussion.html', posts=posts, post_form=post_form, photos=photos)

@app.route('/media')
@login_required
def media():
    return ''

@app.route('/members')
@login_required
def members():
    return ''

@app.route('/favicon.ico')
def favicon():
    return ''

@app.route('/reset_password_request', methods=['GET','POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('discussion'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password.')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('discussion'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('discussion'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html',title='Set New Password', form=form)
