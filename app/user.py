import psycopg2
#import verify
from app import verify
import re

def get_user(username):
    psql_user = 'mailreader'
    host = '::1'
    psql_password = 'rOhd2tHrJt927I8e'
    psy_args = "dbname='mails' user='{pu}' host='{h}' password='{pw}'".format(pu=psql_user, h=host, pw=psql_password)
    conn = psycopg2.connect(psy_args)
    cur = conn.cursor()
    cur.execute("""SELECT userid, password, home, realname FROM USERS WHERE userid = %s LIMIT 1;""", (username,))
    try:
        usr = cur.fetchone()
        if usr is None:
            return None
    except TypeError:
        return None
    cur.close()
    conn.close()
    return usr

def getuser(username):
    usr = get_user(username)
    return user(username, usr[2], usr[3])

def auth(username, passwd):
    usr = get_user(username)
    if usr is None:
        return None
    correct = verify.verify(passwd, usr[1])
    return user(username, usr[2], [3]) if correct else None

def validate_username(username):
    return re.fullmatch(r"^[a-zA-Z0-9][a-zA-Z0-9_'-]{1,38}[a-zA-Z0-9]", username)

def validate_realname(realname):
    return re.fullmatch(r"^[\w\- ,']{2,50}", realname)

class user(object):
    _id = 'Lucifer'
    home =''
    realname = ''

    def __init__(self, username, hom, realname):
        self._id = username
        self.home = '/var/mail/vmail/' + hom
        self.realname = realname

    @property
    def is_authenticated(self):
        return True
    @property
    def is_active(self):
        return True
    @property
    def is_anonymous(self):
        return False
    def get_id(self):
        return self._id
