from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate

app = Flask(__name__)
app.config.update(
    SECRET_KEY = 'Thisisasecret',
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db',
    SQLALCHEMY_TRACK_MODIFICATIONS = False,
    MAIL_SERVER = 'smtp.googlemail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USERNAME = 'noreply.coolhr@gmail.com',
    MAIL_PASSWORD = 'Helloitsme',
    ADMINS = ['noreply.coolhr@gmail.com']
)
mail = Mail(app)
db: SQLAlchemy = SQLAlchemy(app)
migrate = Migrate(app, db)

from coolhr import routes
