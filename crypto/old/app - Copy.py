from flask import (Flask, render_template,
url_for, g,
request,
redirect,
session)
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from key import encrypt, decrypt
from cryptography.fernet import Fernet


app = Flask(__name__)
app.secret_key = "d67e871f54b62c64b6a07b476765698c"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(170), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(1000), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)
    key = db.Column(db.String(1000), nullable=False)

    def __repr__(self):
        return "%r" % self.username

appname = "cryptohunters"

# BEFORE REQUEST
'''@app.before_request
def before_request():
    if 'user' in session:
        g.user = session['user']
    g.user = ""'''

# LANDING
@app.route('/signin', methods=['POST', 'GET'])
def signin():
    if request.method == "POST":
        session.pop('username', None)
        usern = request.form['username']
        pwd = request.form['password']
        user = User.query.filter_by(username=usern).first()
        # Verifying password provided against database password        
        decry = decrypt(user.key, user.password)

        if pwd != decry:
            return render_template('dist/auth-login.html', user=usern)
        else:
            # Establishing session
            session['email'] = user.id
            return session['email']
    else:
        return render_template('dist/auth-login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        user = {'username' : request.form['username'], 'email': request.form['email'], 'password': request.form['password']}

        # Checking if password and confirm password equivalence
        # should be javascript optimized
        if user['password'] != request.form['con-pwd']:
            return render_template("dist/auth-register.html", username=user['username'], email=user['email'])

        # Encrypting password
        enc = encrypt(user['password'])

        # Creating new User object
        new_user = User(username=user['username'], email=user['email'], password=enc[0], key=enc[1])

        # Attempting insertion of new user into database
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect('/')
        except:
            return render_template('dist/error-404.html')
    else:
        return render_template('dist/auth-register.html')

@app.route('/')
def index():
    if g.user != "":
        return render_template('dist/index.html')
    else:
        return render_template('crypto-master/index.html', appname=appname)

# DASHBOARD
@app.route('/wallet')
def wallet():
    return render_template('dist/wallet.html', appname=appname)

@app.route('/portfolio')
def portfolio():
    return render_template('dist/portfolio.html', appname=appname)


if __name__ == "__main__":
    app.run(debug=True)