from flask import (render_template, flash,
url_for, g, request, redirect, session)
from crypto.models import User, Transaction
from crypto.forms import (RegistrationForm,
LoginForm, RequestReset, ResetPassword)
from crypto import app, db, bcrypt, mail
from flask_login import login_user, current_user, logout_user
from wtforms.validators import ValidationError
from flask_mail import Message

appname = "cryptohunters"
url = f"www.{appname}.com"
# LANDING

@app.route('/signup/<string:sup>')
@app.route('/signup-<string:em>')
@app.route('/signup', methods=['POST', 'GET'])
def signup(em=None, sup=None):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    form = RegistrationForm()

    if request.method == 'POST':
        # Storing user input
        username = form.username.data
        email = form.email.data
        #mobile = form.mobile.data
        
        mobile = f"{request.form['mobile']}"
        superior = f"{request.form['superior']}"


        # Encrypting password
        password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        # Creating user object
        if len(superior) > 0:
            user = User(username=username, email=email, password=password, mobile=mobile, superior=superior)
        else:
            user = User(username=username, email=email, password=password, mobile=mobile)
        
        db.session.add(user)
        db.session.commit()

        flash(f"Your account has been created successfully!", category="is-valid")
        return redirect(url_for('signin'))

    if em:
        return render_template('dist/auth-register.html', form=form, email=em)

    if sup:
        return render_template('dist/auth-register.html', form=form, superior=sup)
    
    return render_template('dist/auth-register.html', form=form)


@app.route('/signin/<string:em>')
@app.route('/signin', methods=['POST', 'GET'])
def signin(em=None):
    # Checking if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # Checking if Login form has submitted
    form = LoginForm()
    if request.method == 'POST':
        
        # Storing user input
        email = form.email.data
        inpass = form.password.data

        # Querying the database
        user = User.query.filter_by(email=email).first()

        # Getting user encrypted password
        pw_hash = user.password
           
        # Checking if password matches
        password = bcrypt.check_password_hash(pw_hash, inpass)

        # If bcrypt.password returns True
        if password:
            login_user(user, remember=form.remember.data)
            return redirect(url_for('index'))
        else:
            flash(f"Password is wrong!", category="is-invalid")
    
    if em:
        return render_template('dist/auth-login.html', form=form, email=em)
    
    return render_template('dist/auth-login.html', form=form)


@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('dist/wallet.html',  appname=appname, current_user=current_user)
    else:
        return render_template('crypto-master/index.html', appname=appname)

@app.route('/resetpassword/<string:token>', methods=['GET', 'POST'])
def resetPassword(token):
    # Checking if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    user = User.verify_reset_token(token)
    if user is None:
        flash("Token is invalid or expired, request for a new token", category="is-invalid")
        return redirect(url_for('requestReset'))

    form = ResetPassword()

    if form.validate_on_submit():
        password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = password
        db.session.commit()
        flash("Your password has been updated! You can now log in. Try not to forget your password again mate!", category="is-valid")
        return redirect(url_for('signin'))

    return render_template('dist/auth-reset-password.html', form=form)


@app.route('/requestpasswordreset', methods=['GET', 'POST'])
def requestReset():
    # Checking if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    form = RequestReset()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        token = user.get_reset_token()
        msg = Message("Password Reset Request",
        sender="conqueror_kazama@outlook.com",
        recipients=[user.email])

        msg.body = f'''To reset your password, visit the following link:
        {url_for('resetPassword', token=token, _external=True)}
        '''

        mail.send(msg)

        flash("An email has been sent with instructions on how to reset your password", category="is-valid")
        return redirect(url_for('signin'))
    return render_template('dist/auth-forgot-password.html', form=form)

@app.route('/signout')
def signout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template('crypto-master/about.html', appname=appname)

@app.route('/terms')
def terms():
    return render_template('crypto-master/terms.html', appname=appname, url=url)

@app.route('/privacy')
def privacy():
    return render_template('crypto-master/privacy.html', appname=appname, url=url)

@app.route('/home')
def home():
    return render_template('crypto-master/index.html', appname=appname)

@app.route('/get_started', methods=['GET', 'POST'])
def get_started():
    account = request.form['account']

    try:
        user = User.query.filter_by(email=account).first()
        return redirect(f"/signin/{user.email}")
    except AttributeError:
        return redirect(f"/signup-{account}")


# DASHBOARD
@app.route('/partners')
def partners():
    return render_template('dist/partners.html', appname=appname)

@app.route('/profile')
def profile():
    return render_template('dist/profile.html', appname=appname)