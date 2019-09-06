from .factory import FlaskFactory

db = FlaskFactory.create_db()


class MessageModel(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    message_body = db.Column(db.String(420))
    hash = db.Column(db.String(80))
