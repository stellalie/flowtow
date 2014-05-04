'''
Created on Mar 3, 2014

@author: steve
'''
import unittest

from selenium import webdriver


from urllib.request import urlopen
import mock


class Level1FunctionalTests(unittest.TestCase):

    base_url = 'http://localhost:8000/'
    
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(3)

    def tearDown(self):
        self.driver.close()

    def testHomepage(self):
        """As a visitor to the site, when I load the
         home page I see a banner with "Welcome to FlowTow"."""

        driver = self.driver
        driver.get(self.base_url)
        self.assertIn("Welcome to FlowTow", driver.find_element_by_tag_name('body').text)
        

    def testImagesPresent(self):
        """As a visitor to the site, when I load the home page I 
        see three images displayed, each
        labelled with a date, a user name and a title. """

        driver = self.driver
        driver.get(self.base_url)
        
        images = driver.find_elements_by_tag_name('img')
        
        # expect to find three images
        self.assertEqual(3, len(images), "Wrong number of images found")
        
        flowtows = driver.find_elements_by_class_name('flowtow')
        
        image_list = mock.list_images(3)
        
        self.assertEqual(3, len(flowtows))
        
        # each contains the image, date, author and comments
        for index in range(3):
            div = flowtows[index]
            (path, date, user, comments) = image_list[index]
            
            self.assertIn(date, div.text)
            self.assertIn(user, div.text)
            for c in comments:
                self.assertIn(c, div.text)
                
            # look for just one image
            img = div.find_elements_by_tag_name('img')
            self.assertEqual(1, len(img))
            
            # can we actually get the image 
            # find the URL
            url = img[0].get_attribute('src')
            # try requesting it and test the content-type header returned
            h = urlopen(url)
            self.assertEqual('image/jpeg', h.getheader('content-type'))
            h.close()
            
    def testImageCommentForms(self):
        """As a visitor to the site, when I load the home page I see a comment form below each
image with the placeholder text "Enter your comment here" and a button labelled "Submit"
        """
        
        driver = self.driver
        driver.get(self.base_url)
        
        flowtows = driver.find_elements_by_class_name('flowtow')
         
        # each contains the form for comments
        for div in flowtows:
            # look for two inputs
            inputs = div.find_elements_by_tag_name('input')
            self.assertGreater(len(inputs), 1, "Expected at least two input fields (comment and submit)")
            
            # check that the required inputs have the right attributes
            for i in inputs:
                if i.get_attribute('type') == 'submit':
                    self.assertEqual('Submit', i.get_attribute('value'))
                elif i.get_attribute('name') == 'comment':
                    self.assertEqual('Enter your comment here', i.get_attribute('placeholder'))
            
            
            
    def testAboutSiteLink(self):
        """As a visitor to the site, when I load the home page I see a link to another page
called "About this site".
"""
    
    
        driver = self.driver
        driver.get(self.base_url)
        links = driver.find_elements_by_tag_name('a')
        
        self.assertTrue(any(['About' in l.text for l in links]), "Can't find 'About this site' link")
        
        
        
    def testAboutSitePage(self):
        """As a visitor to the site, when I click on the link "About this site" I am taken to 
a page that contains the site manifesto, including the words "FlowTow is a new, exciting, 
photo sharing service like nothing you've seen before!"
        """
        
        message = "FlowTow is a new, exciting, photo sharing service like nothing you've seen before!"
        
        driver = self.driver
        driver.get(self.base_url)
        
        link = driver.find_element_by_link_text("About")
        
        link.click()
        
        # now look for our message in the page
        self.assertIn(message, driver.find_element_by_tag_name('body').text)
        
    def testPageCSS(self):
        """As a visitor to the site, I notice that all the pages on the site have the same
design with the same colours and fonts used throughout. 
        Interpret this as having a CSS file linked in the pages"""

        driver = self.driver
        driver.get(self.base_url)
        links = driver.find_elements_by_tag_name('link')
         
        self.assertTrue(any([l.get_attribute('rel') == 'stylesheet' for l in links]), "Didn't find a link to a stylesheet")




if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()