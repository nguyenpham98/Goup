from app import app, db, images, clips
from flask import render_template, request, redirect, url_for, flash, send_from_directory, current_app
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, ResetPasswordRequestForm, ResetPasswordForm, EditProfilePictureForm, VerificationForm, VideoForm
from app.models import User, Post, Photo, Video
import os
from app.email import send_password_reset_email
from datetime import datetime
from flask_uploads import UploadNotAllowed
from functools import wraps

@app.before_request # insert code before view function
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow() # update the time
        db.session.commit()

def verified_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.verified != 1:
            flash('You are not a verified user yet.')
            return redirect(url_for('verification'))

        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html', title='About')

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
        # set user.profile_picture to something...
        user.profile_picture = 'defaults/default.jpg'

        db.session.add(user)
        db.session.commit()
        flash('You are now a register user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()

    posts = Post.query.filter_by(user_id=user.id).order_by(Post.timestamp.desc()).all()

    photos = Photo.query.all()

    return render_template('user.html', title=username, user=user, posts=posts, photos=photos)

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

@app.route('/edit_profile_picture', methods=['GET', 'POST'])
@login_required
def edit_profile_picture():
    edit_profile_picture_form = EditProfilePictureForm()
    if edit_profile_picture_form.validate_on_submit():

        post = Post(body='Profile Picture Changed',author=current_user)
        try:
            filename = images.save(edit_profile_picture_form.photo.data, folder='profile/'+current_user.username)
            current_user.profile_picture = filename
            photo = Photo(filename=filename, post=post, public=0)
            db.session.add(photo)
        except UploadNotAllowed:
            flash('File Format Not Allowed.')
            return redirect(url_for('profile', username=current_user.username))
        db.session.commit()
        flash('Profile Picture Changed')
        return redirect(url_for('profile', username=current_user.username))
    elif request.method == 'GET':
        edit_profile_picture_form.photo.data = current_user.profile_picture

    return render_template('edit_profile_picture.html', title='Edit Profile Picture', edit_profile_picture_form=edit_profile_picture_form)

@app.route('/discussion', methods=['GET','POST'])
@login_required
@verified_required
def discussion():
    post_form=PostForm()

    if post_form.post_submit.data and post_form.validate_on_submit():
        if not (request.files['files'].filename!='' or post_form.post.data):
            flash('At least one field must have a value.')
            return redirect(url_for('discussion'))
        else:
            post = Post(body=post_form.post.data, author=current_user)
            if request.files['files'].filename!='': # photo is optional. Check if file requested in form is not blank
                for file in post_form.files.data:
                    try:
                        filename = images.save(file)
                        photo = Photo(filename=filename, post=post, public=1)
                        db.session.add(photo)
                    except UploadNotAllowed:
                        flash('File Format Not Allowed.')
                        return redirect(url_for('discussion'))

            db.session.add(post)
            db.session.commit()
            flash('Your post is now live!')
            return redirect(url_for('discussion'))

    posts = Post.query.filter(Post.body != 'Profile Picture Changed').order_by(Post.timestamp.desc()).all()
    photos = Photo.query.filter(Photo.public==1).order_by(Photo.timestamp.desc()).all()
    videos = Video.query.order_by(Video.timestamp.desc()).all()

    return render_template('discussion.html', title='Discussion', posts=posts, post_form=post_form, photos=photos, videos=videos)

@app.route('/media', methods=['GET','POST'])
@login_required
@verified_required
def media():

    post_form = PostForm()
    if post_form.validate_on_submit():

        if not (request.files['files'].filename!='' or post_form.post.data):
            flash('At least one field must have a value.')
            return redirect(url_for('media'))
        else:
            post = Post(body='',author=current_user)
            for file in post_form.files.data:

                try:
                    filename = images.save(file)
                    photo = Photo(filename=filename, post=post, public=1)
                    db.session.add(photo)
                    db.session.commit()
                    flash('Photo(s) Uploaded.')
                    return redirect(url_for('media'))
                except UploadNotAllowed:
                    flash('File Format Not Allowed.')
                    return redirect(url_for('media'))


    photos = Photo.query.filter(Photo.public==1).order_by(Photo.timestamp.desc()).all()

    return render_template('media.html', title='Media', post_form=post_form, photos=photos)


@app.route('/video', methods=['GET','POST'])
@login_required
@verified_required
def video():
    video_form = VideoForm()
    if video_form.validate_on_submit():
        post=Post(body=video_form.title.data, author=current_user)
        for file in video_form.files.data:
            try:

                filename = clips.save(file)
                video = Video(title=video_form.title.data, filename=filename, post=post)
                db.session.add(video)
                db.session.commit()
                flash('Video Uploaded.')
                return redirect(url_for('video'))
            except UploadNotAllowed:
                flash('File Format Not Allowed.')
                return redirect(url_for('video'))
    videos = Video.query.order_by(Video.timestamp.desc()).all()
    return render_template('video.html', title='Videos', videos=videos, video_form=video_form)


@app.route('/members')
@login_required
@verified_required
def members():
    return ''

@app.route('/verification', methods=['GET','POST'])
@login_required
def verification():
    verification_form=VerificationForm()
    if verification_form.validate_on_submit():
        value = verification_form.choices1.data
        choices = dict(verification_form.choices1.choices)
        label1 = choices[value]

        value = verification_form.choices2.data
        choices = dict(verification_form.choices2.choices)
        label2 = choices[value]

        value = verification_form.choices3.data
        choices = dict(verification_form.choices3.choices)
        label3 = choices[value]

        if label1 == 'Goup' and label2=='2' and label3=='Washington D.C':
            current_user.verified = 1
            db.session.commit()
            flash('You are now a verified user.')
        else:
            flash('Wrong answer(s). Please answer again.')
            return redirect(url_for('verification'))
        return redirect(url_for('discussion'))
    return render_template('verification.html', title='Verification',verification_form=verification_form)

@app.route('/delete-post/<id>', methods=['GET','POST'])
@login_required
@verified_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()
    photos = Photo.query.filter(Photo.post_id==id).all()
    for photo in photos:
        db.session.delete(photo)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.')
    return redirect(url_for('discussion'))

@app.route('/edit/<id>', methods=['GET','POST'])
@login_required
@verified_required
def edit_post(id):
    post = Post.query.filter_by(id=id).first()
    post_form = PostForm()
    if post_form.validate_on_submit():
        post.body = post_form.post.data
        if request.files['files'].filename != '':
            for file in post_form.files.data:
                try:
                    filename = images.save(file)
                    photo = Photo(filename=filename, post=post, public=1)
                    db.session.add(photo)
                    db.session.commit()
                    flash('Photo(s) Uploaded')
                    return redirect(url_for('edit_post', id=id))
                except UploadNotAllowed:
                    flash('File Format Not Allowed.')
                    return redirect(url_for('edit_post', id=id))

        db.session.commit()
        flash('Post edited successfully.')
        return redirect(url_for('discussion'))
    elif request.method=='GET':
        post_form.post.data=post.body
    photos = Photo.query.filter_by(post_id=post.id).order_by(Photo.timestamp.desc()).all()
    return render_template('edit_post.html', title='Edit Post', post_form=post_form, photos=photos)

@app.route('/delete-photo/<id>', methods=['GET','POST'])
@login_required
@verified_required
def delete_photo(id):
    photo = Photo.query.filter(Photo.id==id).first()
    post_id = photo.post_id
    db.session.delete(photo)
    db.session.commit()
    flash('Photo deleted.')
    return redirect(url_for('edit_post', id=post_id))

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
