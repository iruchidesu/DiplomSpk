import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
#from flask_mail import Mail
from config import UPLOAD_FOLDER#, basedir#, ADMINS #, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD
from app.momentjs import momentjs

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
lm.login_message = 'Пожалуйста, авторизуйтесь'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.jinja_env.globals['momentjs'] = momentjs

#mail = Mail(app)

##if not app.debug:
##    import logging
##    from logging.handlers import SMTPHandler
##    credentials = None
##    if MAIL_USERNAME or MAIL_PASSWORD:
##        credentials = (MAIL_USERNAME, MAIL_PASSWORD)
##    mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), 'no-reply@' + MAIL_SERVER, ADMINS, 'microblog failure', credentials)
##    mail_handler.setLevel(logging.ERROR)
##    app.logger.addHandler(mail_handler)

##if not app.debug:
##    import logging
##    from logging.handlers import RotatingFileHandler
##    path_log = os.path.join(basedir, 'tmp')
##    file_handler = RotatingFileHandler(path_log + '/spk.log', 'a', 1 * 1024 * 1024, 10)
##    file_handler.setLevel(logging.INFO)
##    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
##    app.logger.addHandler(file_handler)
##    app.logger.setLevel(logging.INFO)
##    app.logger.info('system startup')

from app import views, models

