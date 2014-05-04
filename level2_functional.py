'''
Created on Mar 3, 2014

@author: steve
'''
import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import datetime

import interface
from urllib.request import urlopen

class Level2FunctionalTests(unittest.TestCase):

    base_url = 'http://localhost:8000/'
    
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(3)

    def tearDown(self):
        self.driver.close()

    def testSubmitCommentForms(self):
        """As a visitor to the site, when I load the home page I see a comment form below each
image with the placeholder text "Enter your comment here" and a button labelled "Submit"
        """
        
        testcomment = "This is a TEST Comment %s" % datetime.datetime.today()
        
        driver = self.driver
        driver.get(self.base_url)
        
        div = driver.find_elements_by_class_name('flowtow')[0]
        
        # find the first form
        forms = div.find_elements_by_tag_name('form')
        myform = forms[0]
        
        # find the text input
        textbox = myform.find_element_by_name("comment")
        
        textbox.send_keys(testcomment)
 
        # submit the form
        myform.submit()
            
        # check that the comment is in the first flowtow div in the returned page
        
        divs = driver.find_elements_by_class_name('flowtow')
        
        self.assertEqual(3, len(divs), "wrong number of flowtow divs in page")

        # look for the comment in the first
        self.assertIn(testcomment, divs[0].text)
        
    
    def testCommentMarkupQuoted(self):
        """As a visitor to the site, when I enter a comment that contains some HTML markup,
            the comment appears on the page with the HTML markup in quoted form.
        """
        
        testcomment = "Comment with <a href='http://example.com'>some markup</a> %s" % datetime.datetime.today()
        
        driver = self.driver
        driver.get(self.base_url)
        
        div = driver.find_elements_by_class_name('flowtow')[0]
        
        # find the first form
        forms = div.find_elements_by_tag_name('form')
        myform = forms[0]
        
        # find the text input
        textbox = myform.find_element_by_name("comment")
        
        textbox.send_keys(testcomment)
 
        # submit the form
        myform.submit()
            
        # check that the comment is in the first flowtow div in the returned page
        
        divs = driver.find_elements_by_class_name('flowtow')
        
        self.assertEqual(3, len(divs), "wrong number of flowtow divs in page")

        # look for the comment in the first, should see the exact string since markup should be quoted
        self.assertIn(testcomment, divs[0].text)
        
        
       

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()