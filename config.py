import os
basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'you_secret_key'

UPLOAD_FOLDER = '/usr/local/www/spkstorage/uploads'

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost/storage_tm?init_command=set%20names%20%22utf8%22'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = True
