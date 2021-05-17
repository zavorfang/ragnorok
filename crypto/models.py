from datetime import datetime
from crypto import db, login_manager, app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique =True, nullable=False)
    email = db.Column(db.String(150),  unique =True, nullable=False)
    password = db.Column(db.String(70), nullable=False)
    mobile = db.Column(db.String(30), nullable=False)
    superior = db.Column(db.String(20), default="conqueror")
    image_file = db.Column(db.String(30), default="default.jpg")
    date = db.Column(db.DateTime, default=datetime.utcnow)
    transactions = db.relationship('Transaction', backref="holder", lazy=True)

    def get_reset_token(self, expires=1800):
        s = Serializer(app.config['SECRET_KEY'], expires)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}')"


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(15), default="btc")
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"User('{self.amount}', '{self.currency}', '{self.date}')"
