'''
Created on Mar 28, 2014

@author: steve
'''
import datetime


def list_comments(db, filename):
    """Return a list of the comments stored for this image filename"""
    cursor = db.cursor().execute('SELECT comment FROM comments WHERE filename IS ?', [filename])
    result = cursor.fetchall()
    return [elt[0] for elt in result]


def add_comment(db, filename, comment):
    """Add this comment to the database for this image filename"""
    db.cursor().execute('INSERT INTO comments VALUES (?, ?)', [filename, comment])
    db.commit()


def list_images(db, n):
    """Return a list of tuples for the first 'n' images in 
    order of date.  Tuples should contain (filename, date, useremail, comments)."""
    query = 'SELECT filename, date, useremail ' \
            'FROM images ' \
            'ORDER BY date desc ' \
            'LIMIT ?'
    cursor = db.cursor().execute(query, [str(n)])
    images_tuple = cursor.fetchall()
    return [image + (list_comments(db, image[0]),) for image in images_tuple]


def add_image(db, filename, useremail):
    """Add this image to the database for the given user"""
    now = datetime.date.today()
    db.cursor().execute('INSERT INTO images VALUES (?, ?, ?)', [filename, now, useremail])
    db.commit()


def list_only_images(db, n):
    """Return a list of tuples for the first 'n' images in
    order of date.  Tuples should contain (filename, date, useremail)."""
    query = 'SELECT filename, date, useremail ' \
            'FROM images ' \
            'ORDER BY date desc ' \
            'LIMIT ?'
    cursor = db.cursor().execute(query, [str(n)])
    images_tuple = cursor.fetchall()
    return list(images_tuple)


def list_images_for_user(db, useremail):
    """Return a list of tuples for the images belonging to this user.
      Tuples should contain (filename, date, useremail)."""
    query = 'SELECT filename, date, useremail ' \
            'FROM images ' \
            'WHERE useremail IS ?' \
            'ORDER BY date desc '
    cursor = db.cursor().execute(query, [useremail])
    images_tuple = cursor.fetchall()
    return list(images_tuple)
