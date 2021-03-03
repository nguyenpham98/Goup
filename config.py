import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False



    SECRET_KEY=os.environ.get('SECRET_KEY') or 'it-is-a-secret'

    MAIL_SERVER='smtp.mailtrap.io'
    MAIL_PORT = 2525
    MAIL_USERNAME='6a213db6bf4103'
    MAIL_PASSWORD = '2561f1bafde38b'
    MAIL_USE_TLS = True
    ADMINS = ['admin@example.com']
    POSTS_PER_PAGE = 3

    UPLOADS_DEFAULT_DEST = 'app/static/uploads'
