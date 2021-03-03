from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, MultipleFileField, FileField, RadioField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from app.models import User, Post, Photo


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email= StringField('Email', validators=[DataRequired(), Email(), Length(min=6, max=35)])
    password =  PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password', message='Must Match Password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('This username is used already. Please choose a different username.')

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email is not None:
            raise ValidationError('This email is used already. Please choose a different email address.')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = StringField('About Me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs): # allow validation if username is untouched in edit
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username=original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('This username is used already. Please choose a different username.')

class EditProfilePictureForm(FlaskForm):
    photo = FileField('Change Profile Picture', validators=[DataRequired()])
    edit_submit = SubmitField('Change')

class PostForm(FlaskForm):
    post = TextAreaField("What's on your mind?", validators=[DataRequired(), Length(min=1,max=1000)])
    post_submit = SubmitField('Post')

class PhotoTitleForm(FlaskForm):
    title = TextAreaField("Photo Title", validators=[DataRequired(), Length(min=1,max=1000)])
    title_submit = SubmitField('Update')

class VideoTitleForm(FlaskForm):
    title = TextAreaField("Video Title", validators=[DataRequired(), Length(min=1,max=1000)])
    title_submit = SubmitField('Update')

class CommentForm(FlaskForm):
    post = TextAreaField('Comment', validators=[DataRequired(), Length(min=1,max=1000)])
    comment_submit = SubmitField('Comment')

class PhotoForm(FlaskForm):
    post = TextAreaField("What's on your mind?", validators=[Optional(), Length(max=1000)])
    files = MultipleFileField('Upload Photos', validators=[DataRequired()])
    photo_submit = SubmitField('Upload')

class VideoForm(FlaskForm):
    title = TextAreaField("Video title", validators=[DataRequired(), Length(min=1, max=100)])
    files = MultipleFileField('Upload Video', validators=[DataRequired()])
    video_submit = SubmitField('Upload')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Reset Password Request')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    repeat_password = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    reset_submit = SubmitField('Reset')

class VerificationForm(FlaskForm):
    choices1 = RadioField('What is the name of the platform?', choices=[('choice1', 'Go up'), ('choice2', 'Goleft'), ('choice3', 'Goup'), ('choice4', 'Goright')])
    choices2 = RadioField('What is 1+1=?', choices=[('choice1', '2'), ('choice2', '4'), ('choice3', '5'), ('choice4', '0')])
    choices3 = RadioField('What is the capital of USA?', choices=[('choice1', 'California'), ('choice2', 'Washington D.C'), ('choice3', 'New York'), ('choice4', 'Chicago')])
    submit = SubmitField('Verify')

class EditPost(FlaskForm):
    edit_submit = SubmitField('Edit')