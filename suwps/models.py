import passlib.hash
from flask_login import UserMixin

from suwps import db


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(32), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)

    def verify_password(self, password):
        return passlib.hash.pbkdf2_sha256.verify(password, self.password)

    def __repr__(self):
        return '<User {}>'.format(self.username)
