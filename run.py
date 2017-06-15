#!/usr/bin/env python3
from app import app, user, verify
from flask_login import LoginManager

login_manager = LoginManager()

@login_manager.user_loader
def load_user(id):
    return user.getuser(id)
app.secret_key = 'NbbRKjz2qMD/wLBpW08lAQga'
login_manager.init_app(app)
app.run(debug = True)
