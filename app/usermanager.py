#!/usr/bin/python3.5
import crypt

def encode_password(password: str, rounds: int = None, scheme: str = None) -> str:
    if scheme is None:
        scheme = "SHA512"
    method = getattr(crypt, "METHOD_%s" % scheme)
    prefix = "$%s$" % method.ident
    if rounds is not None:
        prefix += "rounds=%d$" % rounds
    return "{%s-CRYPT}%s" % (scheme, crypt.crypt(password, prefix + crypt.mksalt().rsplit("$", 1)[-1]))

import sys
import subprocess
import psycopg2

def adduser(username, password, realname):
    psql_user = 'mailreader'
    host = '::1'
    psql_password = 'rOhd2tHrJt927I8e'

    psy_args = "dbname='mails' user='{pu}' host='{h}' password='{pw}'".format(pu=psql_user, h=host, pw=psql_password)
    conn = psycopg2.connect(psy_args)
    cur = conn.cursor()
    cur.execute("""SELECT(EXISTS(SELECT * FROM USERS WHERE userid = %s))""", (username,))
    exists_already = cur.fetchone()[0]
    #print(exists_already)
    if exists_already:
        print('User exists already')
        sys.exit(0)
    cur.close()
    conn.close()

    args = ''
    uid = 0
    with open('/var/mail/vmail/usertable') as f:
        users = set(map(int, f.readlines()))
        iter = (i for i in range(100001, 4*10**9) if i not in users)
        uid = next(iter)

    args = ['--disabled-login', '--gecos', '""', '--ingroup', 'vmail', '--uid',  str(uid), '--lastuid', '4000000000', '--home', '/var/mail/vmail/u' + str(uid - 10**5), 'mailuser' + str(uid - 10**5)]
    #print(['adduser'] + args)

    completed_process = subprocess.run(['adduser'] + args)
    print(completed_process.stdout)
    with open('/var/mail/vmail/usertable', 'a') as f:
        f.write(str(uid) + '\n')

    psql_user = 'mailwriter'
    host = '::1'
    psql_password = 'lhOuGDQbZg2ww4D0'

    pass_db = encode_password(password)
    psy_args = "dbname='mails' user='{pu}' host='{h}' password='{pw}'".format(pu=psql_user, h=host, pw=psql_password)
    conn = psycopg2.connect(psy_args)
    cur = conn.cursor()

    cur.execute(
    """
    INSERT INTO users
    (userid, password, realname, home, uid)
    VALUES (%s, %s, %s, %s, %s);
    """,
    (username, pass_db, realname, 'u' + str(uid - 10**5), uid))
    conn.commit()
    cur.close()
    conn.close()

import shutil

def deluser(username):
    psql_user = 'mailreader'
    host = '::1'
    psql_password = 'rOhd2tHrJt927I8e'

    psy_args = "dbname='mails' user='{pu}' host='{h}' password='{pw}'".format(pu=psql_user, h=host, pw=psql_password)
    conn = psycopg2.connect(psy_args)
    cur = conn.cursor()
    cur.execute("SELECT uid FROM USERS WHERE userid = %s", (username,))
    uid = cur.fetchone()[0]
    cur.close()
    conn.close()

    if uid is None:
        print('Invalid username')
        return None
    args = ['mailuser' + str(uid - 100000)]


    completed_process = subprocess.run(['deluser'] + args)
    print(completed_process.stdout)
    with open('/var/mail/vmail/usertable', 'r+') as f:
        d = f.readlines()
        f.seek(0)
        for i in d:
            f.write(i if i != str(uid)+'\n' else '')
            f.truncate()

    psql_user = 'mailwriter'
    host = '::1'
    psql_password = 'lhOuGDQbZg2ww4D0'

    psy_args = "dbname='mails' user='{pu}' host='{h}' password='{pw}'".format(pu=psql_user, h=host, pw=psql_password)
    conn = psycopg2.connect(psy_args)
    cur = conn.cursor()

    cur.execute("DELETE FROM users WHERE userid = %s;", (username,))
    print(cur.statusmessage)
    conn.commit()
    cur.close()
    conn.close()

    shutil.rmtree('/var/mail/vmail/u' + str(uid-100000))
    return True
