'''
Created on Mar 26, 2012

@author: steve
'''

from http.cookies import SimpleCookie

# this variable MUST be used as the name for the cookie used by this application
COOKIE_NAME = 'sessionid'

def check_login(db, useremail, password):
    """returns True if password matches stored"""


def generate_session(db, useremail):
    """create a new session, return a cookie obj with session key
    user must be a valid user in the database, if not, return None
    There should only be one session per user at any time, if there
    is already a session active, the cookie should use the existing
    sessionid
    """

def delete_session(db, useremail):
    """remove all session table entries for this user"""


def user_from_cookie(db, environ):
    """check whether HTTP_COOKIE set, if it is,
    and if our cookie is present, try to
    retrieve the user email from the sessions table
    return useremail or None if no valid session is present"""



