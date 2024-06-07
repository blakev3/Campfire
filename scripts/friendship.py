from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Friendship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', foreign_keys=[user_id])
    friend = db.relationship('User', foreign_keys=[friend_id])

    def __init__(self, user_id, friend_id):
        self.user_id = user_id
        self.friend_id = friend_id
