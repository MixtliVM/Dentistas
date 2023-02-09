import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTS_PER_PAGE = 10

    #MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_SERVER = 'smtp.gmail.com'
    #MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_PORT = 465
    #MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    #MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_USERNAME = 'luceromtzbonilla@gmail.com'
    #MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_PASSWORD = 'fcwbjltgrzbyechx'
    ADMINS = 'luceromtzbonilla@gmail.com'
