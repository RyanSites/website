import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

TITLE = 'BR Graphic Design LLC'
CSRF_ENABLED = True
SECRET_KEY = '2A4CB5553BFA81EFC37A291AE69C6'
POSTS_PER_PAGE = 5