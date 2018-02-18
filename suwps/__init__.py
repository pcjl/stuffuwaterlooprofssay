import os

from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_sslify import SSLify


app = Flask(__name__)
app.config.from_object('config')
app.url_map.strict_slashes = False

if 'DYNO' in os.environ:
    sslify = SSLify(app)

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

from suwps import models, views


@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(user_id)


@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('get_login'))
