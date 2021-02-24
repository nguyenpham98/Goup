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
    post = TextAreaField("What's on your mind?", validators=[Optional(), Length(max=1000)])
    files = MultipleFileField('Upload Photos', validators=[Optional()])
    post_submit = SubmitField('Post')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Reset Password Request')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    repeat_password = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    reset_submit = SubmitField('Reset')

class VerificationForm(FlaskForm):
    choices = RadioField('Choices', choices=[('choice1', 'Go up'), ('choice2', 'Goleft'), ('choice3', 'Goup'), ('choice4', 'Goright')])
    submit = SubmitField('Verify')