'''
Created on Mar 3, 2014

@author: Steve Cassidy

Version 2: adds test for list_only_images, a simplified version of list_images

'''
import unittest
import datetime

import interface
from database import COMP249Db


class LevelAUnitTests(unittest.TestCase):
    
    
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


    def test_list_comments(self):
        """Test that list_comments returns all comments on an image"""
        
        
        # list comments should return the three comments we inserted
        for image in self.images:
            comments = interface.list_comments(self.db, image[0])
            
            if image[0] == 'seashell.jpg':
                # should have no comments
                self.assertEqual([], comments)
            else:
                self.assertEqual(len(self.comments), len(comments), "wrong number of comments")
                # check that all comments are present
                self.assertTrue(all([c in comments for c in self.comments]), "didn't find all comments")
            
        

    def test_add_comment(self):
        """Test that add_comment is able to add new comments"""
        
        image = 'seashell.jpg'
        testcomment = 'she sells sea shells on the sea shore'

        interface.add_comment(self.db, image, testcomment)
        
        # use list_comments to retrieve the comments, this assumes that list_comments works
        
        comments = interface.list_comments(self.db, image)
        self.assertEqual(1, len(comments), "expected just one comment for seashell.jpg")
        self.assertEqual(testcomment, comments[0])
        
        

    def test_list_images(self):
        """Test that list_images returns the right list of images"""
        
        # get the four most recent image entries
        image_list = interface.list_images(self.db, 4)
        
        self.assertEqual(4, len(image_list))
        # and all entries are four elements long
        self.assertTrue(all([len(i) == 4 for i in image_list]))
        
        refimages = self.images
        
        # check that the images are in the right order
        self.assertListEqual([img[0] for img in refimages], [img[0] for img in image_list])
        
        # and the dates are right
        self.assertListEqual([img[1] for img in refimages], [img[1] for img in image_list])
        
        # and the owners
        self.assertListEqual([img[2] for img in refimages], [img[2] for img in image_list])
        
        # now check the comments, should all be the same except the last one
        for image in image_list[:3]:
            self.assertListEqual(self.comments, image[3])
        
        self.assertEqual([], image_list[3][3], 'comment on last image should be empty')
       

    def test_list_only_images(self):
        """Test that list_only_images returns the right list of images
        Similar to list_images but does not include the comments.
        """
        
        # get the four most recent image entries
        image_list = interface.list_only_images(self.db, 4)
        
        self.assertEqual(4, len(image_list))
        # and all entries are three elements long
        self.assertTrue(all([len(i) == 3 for i in image_list]))
        
        refimages = self.images
        
        # check that the images are in the right order
        self.assertListEqual([img[0] for img in refimages], [img[0] for img in image_list])
        
        # and the dates are right
        self.assertListEqual([img[1] for img in refimages], [img[1] for img in image_list])
        
        # and the owners
        self.assertListEqual([img[2] for img in refimages], [img[2] for img in image_list])


    
    def test_add_image(self):
        """Test that add_image updates the database properly"""
        
        imagename = 'new.jpg'
        useremail = 'carol@everywhere.com'
        interface.add_image(self.db, imagename, useremail)
        
        # check with a raw SQL query
        cursor = self.db.cursor()
        cursor.execute("select filename, date from images where useremail=?", (useremail,))
        result = cursor.fetchall()
        self.assertEqual(1, len(result), 'expected one image for carol')
        self.assertEqual(imagename, result[0][0], 'wrong image name after add_image')
        # date should be todays
        today = datetime.datetime.today().strftime("%Y-%m-%d")
        date = result[0][1]
        self.assertEqual(today, date)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()