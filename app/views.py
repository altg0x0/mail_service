from app import app
from pathlib import Path
import flask_login
from flask_login import current_user
from flask import request, render_template, redirect
from app import user
from app import usermanager
from app import mail
from glob import glob
from datetime import datetime
from app import sendmail
import os

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"

@app.route('/auth', methods=['POST'])
def auth():
    f = request.form
    username = f['user']
    password = f['pswd']
    remember = 'remember' in f.keys()
    u = user.auth(username, password)
    if u is not None:
        flask_login.login_user(user=u)
        return redirect("https://altg0x0.tk/inbox?first=0&count=25")

    return "u: {}\nr: {}\nu: {}".format(username, remember, u)

@app.route('/create_user', methods=['POST'])
def register():
    f = request.form
    username = f['user']
    password = f['pswd']
    realname = f['realname']
    if user.get_user(username) is not None:
        return 'User with this username already exists!'
    if not user.validate_username(username):
        return """Username must be 3-40 symbols long.
        It can only contain alphanumeric symbols
        and '-_ (not as first or last symbol)."""
    if not user.validate_realname(realname):
        return """You real name must be 2-255 symbols long. It
        can only contain word charcters, spaces and following symbols:
        '-,"""
    if len(password) > 1000:
        return """You password must be no longer than 1000 symbols."""
    if password != f['pswd_r']:
        return """Passwords you entered do not match."""
    usermanager.adduser(username, password, realname)
    return """Registration successful!"""

#@app.route('/login')
#def login():
    #flask_login.login_user(user=user.u)
#    return Path('app/static/login.html').read_text()

@app.route('/secret')
@flask_login.login_required
def secret():
    return """
    Privetstvyu, moy povelitel ({})!
    """.format(flask_login.current_user.get_id())

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return 'Logout successful'

@app.route('/inbox')
@flask_login.login_required
def inbox():
    firstm = int(trygetarg('first', 0))
    count = min(200, int(trygetarg('count', 25)))
    countm = count
    count = max(count, 0)
    home = current_user.home

    message_files = sorted(glob(home + '/cur/*') + glob(home + '/new/*'), reverse=True)
    l = len(message_files)
    firstm = min(l - 1, firstm)
    firstm = max(firstm, 0)
    count = min(count, l - firstm)

    messages = [mail.letter(x) for x in message_files[firstm: firstm + count]]
    return render_template('inbox.html',
    messages=messages, user=current_user, date_now=datetime.now().strftime('%H:%M:%S %d.%m.%Y'),
    total_count = l, first=firstm, count=count, countm=countm, folder='inbox', folder_id='in')

@app.route('/sent')
@flask_login.login_required
def sent():
    firstm = int(trygetarg('first', 0))
    count = min(200, int(trygetarg('count', 25)))
    countm = count
    count = max(count, 0)
    home = current_user.home

    message_files = sorted(glob(home + '/.Sent/cur/*') + glob(home + '/.Sent/new/*'), reverse=True)
    l = len(message_files)
    firstm = min(l - 1, firstm)
    firstm = max(firstm, 0)
    count = min(count, l - firstm)

    messages = [mail.letter(x) for x in message_files[firstm: firstm + count]]
    return render_template('inbox.html',
    messages=messages, user=current_user, date_now=datetime.now().strftime('%H:%M:%S %d.%m.%Y'),
    total_count = l, first=firstm, count=count, countm=countm, folder='sent', folder_id='sent')

@app.route('/messages/<type>/<id>')
@flask_login.login_required
def show_message(type, id):
    home = current_user.home
    paths = []
    if type == 'in':
        paths = sorted(glob(home + '/cur/*') + glob(home + '/new/*'), reverse=True)
    elif type == 'sent':
        paths = sorted(glob(home + '/.Sent/cur/*') + glob(home + '/.Sent/new/*'), reverse=True)
    try:
        msg = mail.letter(paths[int(id)])
        return render_template("show.html",
        message=msg, date=msg.date_received.strftime('%d.%m.%Y'),
        time=msg.date_received.strftime('%H:%M:%S'), id=id)
    except IndexError:
        return """Message not found"""

@app.route('/del/<type>/<id>')
@flask_login.login_required
def del_message(type, id):
    home = current_user.home
    paths = []
    if type == 'in':
        paths = sorted(glob(home + '/cur/*') + glob(home + '/new/*'), reverse=True)
    elif type == 'sent':
        paths = sorted(glob(home + '/.Sent/cur/*') + glob(home + '/.Sent/new/*'), reverse=True)
    try:
        os.remove(paths[int(id)])
        return redirect("https://altg0x0.tk/inbox?first=0&count=25")
    except IndexError:
        return """Message not found"""

@app.route('/del/<type>/', methods=['POST'])
@flask_login.login_required
def del_messages(type):
    home = current_user.home
    selected = request.form.getlist('selected')
    paths = []
    if type == 'in':
        paths = sorted(glob(home + '/cur/*') + glob(home + '/new/*'), reverse=True)
    elif type == 'sent':
        paths = sorted(glob(home + '/.Sent/cur/*') + glob(home + '/.Sent/new/*'), reverse=True)
    try:
        for id in selected:
            os.remove(paths[int(id)])
        return redirect("https://altg0x0.tk/inbox?first=0&count=25")
    except IndexError:
        return """Message not found"""

@app.route('/new')
@flask_login.login_required
def new():
    subj = trygetarg('subject', '')
    to = trygetarg('to', '')
    return render_template('new.html',
    user=current_user, subject=subj, to=to)

@app.route('/send', methods=['POST'])
@flask_login.login_required
def send():
    f = request.form
    try:
        to = f['to']
        subject = f['subject']
        body = f['body']
        sendmail.send(to, current_user._id + "@altg0x0.tk",
        subject, body)
    except Exception:
        return """Error"""
    return redirect("https://altg0x0.tk/inbox?first=0&count=25")

def trygetarg(name, default):
    try:
        r = request.args.get(name)
        return r if r else default
    except Exception:
        return default
