'''
Created on Mar 26, 2012

@author: steve
'''
from http.cookiejar import Cookie

from http.cookies import SimpleCookie

# this variable MUST be used as the name for the cookie used by this application
import uuid

COOKIE_NAME = 'sessionid'


def check_login(db, useremail, password):
    """returns True if password matches stored"""
    import hashlib

    cursor = db.cursor().execute('SELECT password FROM users WHERE email IS ?', [useremail])
    result = cursor.fetchone()
    if result:
        return result[0] == hashlib.sha1(password.encode()).hexdigest()
    return False


def generate_session(db, useremail):
    """create a new session, return a cookie obj with session key
    user must be a valid user in the database, if not, return None
    There should only be one session per user at any time, if there
    is already a session active, the cookie should use the existing
    sessionid
    """
    user = db.cursor().execute('SELECT email FROM users WHERE email IS ?', [useremail]).fetchone()
    if user:
        existing_session = db.cursor().execute('SELECT sessionid FROM sessions WHERE useremail IS ?',
                                               [user[0]]).fetchone()
        if existing_session:
            cookie = SimpleCookie()
            cookie[COOKIE_NAME] = existing_session[0]
            return cookie
        else:
            key = str(uuid.uuid4())
            db.cursor().execute('INSERT INTO sessions VALUES (?, ?)', [key, useremail])
            db.commit()
            cookie = SimpleCookie()
            cookie[COOKIE_NAME] = key
            return cookie
    return None


def delete_session(db, useremail):
    """remove all session table entries for this user"""
    db.cursor().execute('DELETE FROM sessions WHERE useremail IS ?', [useremail])
    db.commit()


def user_from_cookie(db, environ):
    """check whether HTTP_COOKIE set, if it is,
    and if our cookie is present, try to
    retrieve the user email from the sessions table
    return useremail or None if no valid session is present"""
    if 'HTTP_COOKIE' in environ:
        cookie = SimpleCookie(environ['HTTP_COOKIE'])
        if COOKIE_NAME in cookie:
            sessionkey = cookie[COOKIE_NAME].value
            cur = db.cursor()
            cur.execute('SELECT useremail FROM sessions WHERE sessionid IS ?', (sessionkey,))
            result = cur.fetchone()

            if result is not None:
                return result[0]
    return None
