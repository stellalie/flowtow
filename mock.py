'''
Created on Mar 24, 2014

@author: Steve Cassidy
'''

mock_image_list = [
                   ('cycling.jpg', '2014-01-14', 'bob@here.com', ['cool photo', 'thx']),
                   ('window.jpg', '2014-01-12', 'jim@there.com', []),
                   ('hang-glider.jpg', '2013-11-18', 'bob@here.com', ['much wave', 'wow'])
                   ]

def list_images(n):
    """Return a list of image tuples for testing, each tuple
    contains (filename, date, useremail, comments)."""
    
    return mock_image_list[:n]

