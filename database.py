'''
Created on Mar 26, 2012

@author: steve
'''

import sqlite3

class COMP249Db():
    '''
    Provide an interface to the database for a COMP249 web application
    '''


    def __init__(self, dbname="comp249.db"):
        '''
        Constructor
        '''
        
        self.dbname = dbname
        self.conn = sqlite3.connect(self.dbname)
        ### ensure that results returned from queries are strings rather
        # than unicode which doesn't work well with WSGI
        self.conn.text_factory = str
        
    def cursor(self):
        """Return a cursor on the database"""
        
        return self.conn.cursor()
    
    def commit(self):
        """Commit pending changes"""
        
        self.conn.commit()
        
    def delete(self):
        """Destroy the database file"""
        pass
        
        
    def crypt(self, password):
        """Return a one-way hashed version of the password suitable for
        storage in the database"""
        
        import hashlib
        
        return hashlib.sha1(password.encode()).hexdigest()
        

    def create_tables(self):
        """Create and initialise the database tables
        This will have the effect of overwriting any existing
        data."""
        
        
        sql = """
DROP TABLE IF EXISTS users;
CREATE TABLE users (
           email text unique primary key,
           password text,
           nick text,
           avatar text
);

DROP TABLE IF EXISTS sessions;
CREATE TABLE sessions (
            sessionid text unique primary key,
            useremail text,
            FOREIGN KEY(useremail) REFERENCES users(email)
);

DROP TABLE IF EXISTS images;
CREATE TABLE images (
            filename text unique primary key,
            date text,
            useremail text,
            FOREIGN KEY(useremail) REFERENCES users(email)
);

DROP TABLE IF EXISTS comments;
CREATE TABLE comments (
            filename text,
            comment text,
            FOREIGN KEY(filename) REFERENCES images(filename)
);"""

        self.conn.executescript(sql)
        self.conn.commit()
        
    
    def sample_data(self):
        """Generate some sample data for testing the web
        application. Erases any existing data in the
        database"""
        
                #  email,         pass,   nick             avatar
        users = [('bob@here.com', 'bob', 'Bob Bobalooba', 'bob'),
                 ('jim@there.com', 'jim', 'The Jimbulator', 'default'),
                 ('mary@where.com', 'mary', 'Mary, Contrary', 'mary')]


        # filename, date, useremail, comments
        images = [ 
                   ('cycling.jpg',     '2014-01-14', 'bob@here.com', ['cool photo', 'thx']),
                   ('window.jpg',      '2014-01-12', 'jim@there.com', []),
                   ('hang-glider.jpg', '2013-11-18', 'bob@here.com', ['much wave', 'wow']),
                   ('seashell.jpg',    '2013-07-01', 'mary@where.com', ['ahh, seashell!'])
                 ]
        
        
        # create one entry per unit for each user
        cursor = self.cursor()
        for email, password, nick, avatar in users:
            sql = "INSERT INTO users VALUES (?, ?, ?, ?)"
            cursor.execute(sql, (email, self.crypt(password), nick, avatar))
            
        for fname, date, useremail, comments in images:
            sql = 'INSERT INTO images VALUES (?, ?, ?)'
          
            # now create the database entry for this image
            cursor.execute(sql, (fname, date, useremail))
            # and create some comments
            sql = "INSERT INTO comments VALUES (?, ?)"
            for comment in comments:
                cursor.execute(sql, (fname, comment))
                
        # commit all updates to the database
        self.commit()
    

if __name__=='__main__':
    # if we call this script directly, create the database and make sample data
    db = COMP249Db()
    db.create_tables()
    db.sample_data()