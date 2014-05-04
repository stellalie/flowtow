'''
Created on Mar 26, 2012

@author: steve
'''

import unittest

from database import COMP249Db
from http.cookies import SimpleCookie

# import the module to be tested
import users
import interface 

class Test(unittest.TestCase):

    
    def setUp(self):
        # open an in-memory database for testing
        self.db = COMP249Db(':memory:')
        self.db.create_tables()

                #  email,         pass,   first,  last 
        self.users = [('bob@here.com', 'bob', 'Bob', 'Bobalooba'),
                 ('jim@there.com', 'jim', 'Jim', 'Jimminy'),
                 ('mary@where.com', 'mary', 'Mary', 'Mary'),
                 ('carol@everywhere.com', 'carol', 'Oh', 'Carol')]

                # filename, date, useremail
        self.images = [ 
                   ('cycling.jpg',     '2014-01-14', 'bob@here.com'),
                   ('window.jpg',      '2014-01-12', 'jim@there.com'),
                   ('hang-glider.jpg', '2013-11-18', 'bob@here.com'),
                   ('seashell.jpg',    '2013-07-01', 'mary@where.com')
                 ]

        self.comments = ['one', 'two', 'three']

        # create sample data for testing
        cursor = self.db.cursor()
        for email, password, first, last in self.users:
            sql = "INSERT INTO users VALUES (?, ?, ?, ?)"
            cursor.execute(sql, (email, self.db.crypt(password), first, last))
            
        for fname, date, useremail in self.images:
            sql = 'INSERT INTO images VALUES (?, ?, ?)'
          
            # now create the database entry for this image
            cursor.execute(sql, (fname, date, useremail))
            # and create some comments unless this is seashell
            # which gets no comments so we can test that
            if fname != 'seashell.jpg':
                sql = "INSERT INTO comments VALUES (?, ?)"
                for comment in self.comments:
                    cursor.execute(sql, (fname, comment))
                
        # commit all updates to the database
        self.db.commit()
        

    def test_list_images_user(self):
        """Test that list_images_for_user returns the right list of images for a user"""
        
        for user in self.users:
            email = user[0]
        
            # get the four most recent image entries
            image_list = interface.list_images_for_user(self.db, email)
        
            # and all entries are three elements long
            self.assertTrue(all([len(i) == 3 for i in image_list]))
        
            refimages = [i for i in self.images if i[2] == email]
        
            # check that the images are in the right order
            self.assertListEqual([img[0] for img in refimages], [img[0] for img in image_list])
        
            # and the dates are right
            self.assertListEqual([img[1] for img in refimages], [img[1] for img in image_list])
        
            # and the owners
            self.assertListEqual([img[2] for img in refimages], [img[2] for img in image_list])
        

    def test_check_login(self):

        for email, password, nick, avatar in self.users:
            # try the correct password
            self.assertTrue(users.check_login(self.db, email, password), "Password check failed for email %s" % email)

            # and now incorrect
            self.assertFalse(users.check_login(self.db, email, "badpassword"), "Bad Password check failed for email %s" % email)

        # check for an unknown email
        self.assertFalse(users.check_login(self.db, "user@here.com", "badpassword"), "Bad Password check failed for unknown email")


    def test_generate_session(self):
        """The generate_session procedure makes a new session cookie
        to be returned to the client
        If there is already a session active for this user, return the
        same session key in the cookie"""

        # run tests for all test users
        for email, password, nick, avatar in self.users:
            cookie = users.generate_session(self.db, email)

            self.assertIsInstance(cookie, SimpleCookie, "Return value of generate_session is not a cookie")

            # look for the cookie
            self.assertTrue(users.COOKIE_NAME in cookie, "Cookie from generate_session has no entry for defined cookie name")

            # get the value and verify that it is in the sessions table
            sessionid = cookie[users.COOKIE_NAME].value

            cursor = self.db.cursor()
            cursor.execute('select useremail from sessions where sessionid=?', (sessionid,))

            query_result =  cursor.fetchone()
            if query_result == None:
                self.fail("No entry for session id %s in sessions table" % (sessionid,))

            self.assertEqual(email, query_result[0])

            # now try to make a new session for one of the users

            cookie2 = users.generate_session(self.db, email)

            self.assertIsInstance(cookie2, SimpleCookie, "Return value of generate_session is not a cookie for second call")

            # look for the cookie
            self.assertTrue(users.COOKIE_NAME in cookie2, "Cookie from generate_session has no entry for defined cookie name")

            # sessionid should be the same as before

            self.assertEqual(cookie2[users.COOKIE_NAME].value, sessionid)

        # try to generate a session for an invalid user

        cookie = users.generate_session(self.db, "user@here.com")
        self.assertEqual(cookie, None, "Invalid user should return None from generate_session")


    def test_delete_session(self):
        """The delete_session procedure should remove all sessions for
        a given user in the sessions table.
        Test relies on working generate_session"""

        # run tests for all test users
        for email, password, first, last in self.users:
            cookie = users.generate_session(self.db, email)

            self.assertIsInstance(cookie, SimpleCookie, "generate_session failing, can't run delete_session tests")

            # get the value and verify that it is in the sessions table
            sessionid = cookie[users.COOKIE_NAME].value

            # now remove the session
            users.delete_session(self.db, email)

            # now check that the session is not present

            cursor = self.db.cursor()
            cursor.execute('select sessionid from sessions where useremail=?', (email,))

            rows = cursor.fetchall()
            self.assertEqual(rows, [], "Expected no results for sessions query from deleted session, got %s" % (rows,))




    def test_user_from_cookie(self):
        """The user_from_cookie procedure finds the name of the logged in
        user from the session cookie if present

        Test relies on working generate_cookie
        """
  
        # first test with no cookie
        environ = dict()
        email_from_cookie = users.user_from_cookie(self.db, environ)
        self.assertEqual(email_from_cookie, None, "Expected None in case with no cookie, got %s" % str(email_from_cookie))


        cookie = SimpleCookie()
        cookie[users.COOKIE_NAME] = 'fake sessionid'
        environ = {'HTTP_COOKIE': cookie[users.COOKIE_NAME].OutputString()}

        email_from_cookie = users.user_from_cookie(self.db, environ)

        self.assertEqual(email_from_cookie, None, "Expected None in case with invalid session id, got %s" % str(email_from_cookie))


        # run tests for all test users
        for email, password, nick, avatar in self.users:

            cookie = users.generate_session(self.db, email)

            self.assertIsInstance(cookie, SimpleCookie, "generate_session failing, can't run user_from_cookie tests")

            environ = {'HTTP_COOKIE': cookie[users.COOKIE_NAME].OutputString()}

            email_from_cookie = users.user_from_cookie(self.db, environ)

            self.assertEqual(email_from_cookie, email)





if __name__ == "__main__":
    unittest.main()