# api/models.py

from api import db


class User(db.Model):
    """This class represents the users table."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15))
    email = db.Column(db.String(255))
    #encrypted_account_number = db.Column(db.String(255))

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return User.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<User: {}>".format(self.username)