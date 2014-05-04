'''
Created on Mar 3, 2014

@author: steve
'''
import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import datetime

import interface
from urllib.request import urlopen

class Level3FunctionalTests(unittest.TestCase):

    base_url = 'http://localhost:8000/'
    
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(3)

    def tearDown(self):
        self.driver.close()
            
    def doLogin(self, email, password):
        """Perform a login with some validation along the way"""
        
        driver = self.driver
        
        # there is a form with id='loginform'
        try:
            loginform = driver.find_element_by_id('loginform')
        except NoSuchElementException:
            self.fail("no form with id='loginform' found")
 
        # login form action should be /login
        self.assertEqual(self.base_url + 'login', loginform.get_attribute('action'), "login form action should be '/login'")
 
        # the form has an email field
        try:
            emailfield = loginform.find_element_by_name('email')
        except NoSuchElementException:
            self.fail("no email field found for login form")
        
        # and a password field
        try: 
            passwordfield = loginform.find_element_by_name('password')
        except NoSuchElementException:
                self.fail("no password field found for login form")
                
        self.assertEqual(passwordfield.get_attribute('type'), 'password', "Password field should have type='password'")                
                
        emailfield.send_keys(email)
        passwordfield.send_keys(password)
        # submit the form
        loginform.submit()
        
                        
                
    def testLoginForms(self):
        """As a visitor to the site, when I load the home page, 
        I see a form with entry boxes for email and password and a button labelled Login."""
        
        driver = self.driver
        driver.get(self.base_url)
         
        # fill out the form
        email = 'bob@here.com'
        password = 'bob'
                
        # As a registered user, when I enter my email address (bob@here.com) and password 
        # (bob) into the login form and click on the Login button, the page I get in 
        # response is a version of the home page with the login form replaced by the message
        # "Logged in as bob@here.com" and a button labelled Logout.    
        
        self.doLogin(email, password)
        
        # expect to see user email address in returned page
        text = driver.find_element_by_tag_name('body').text
        
        self.assertIn("Logged in as %s" % email, text)
        
        try:
            logouts = driver.find_element_by_name('logout')
        except NoSuchElementException:
                self.fail("no logout button found")
        
        # The response also includes a cookie with the name 
        # sessionid that contains some kind of random string.

        all_cookies = driver.get_cookies()
        self.assertEqual(1, len(all_cookies))
        cookie = all_cookies[0]
        self.assertEqual(cookie['name'], 'sessionid')

    def testLoginError(self):
        """As a registered user, when I enter my email address but get my 
        password wrong and click on the Login button, the page I get in 
        response contains a message "Login Failed, please try again". 
        The page also includes another login form."""
        
        driver = self.driver
        driver.get(self.base_url)
         
        # fill out the form
        email = 'bob@here.com'
        password = 'wrong password'
 
        self.doLogin(email, password)
        
        # expect to see login failed message in the page
        text = driver.find_element_by_tag_name('body').text
        
        self.assertIn("Login Failed, please try again", text)

    def testMyImages(self):
        """As a registered user, once I have logged in, on the home 
        page I see a new link called "My Images". When I click on this 
        link the page I get in response contains all of the images that 
        I have uploaded listed in order of date (newest first). Each 
        image is displayed as on the home page with my name, the date 
        and a list of comments. Each image also has a comment form."""

        driver = self.driver
        driver.get(self.base_url)
         
        # fill out the form
        email = 'bob@here.com'
        password = 'bob'
        
        self.doLogin(email, password)
        
        # expect to see link to my images
        try:
            imagelink = driver.find_element_by_link_text('My Images')        
        except NoSuchElementException:
            self.fail("can't find link to My Images page")
            
        imagelink.click()
        
        # on the page returned I expect to see all my images
        
        flowtows = driver.find_elements_by_class_name('flowtow')
        
        # each contains the username and an image
        for div in flowtows:
            
            # our email address should be mentioned
            self.assertIn(email, div.text)
            
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
            
            # is there a comment form
            try:
                div.find_elements_by_tag_name('form')
            except NoSuchElementException:
                self.fail("No form found in flowtow div")
                
    
    def testNameInAllPages(self):
        """As a registered user, once I have logged in,
         every page that I request contains my name and the logout button."""
        
        driver = self.driver
        driver.get(self.base_url)
         
        # fill out the form
        email = 'bob@here.com'
        password = 'bob'
                
        # As a registered user, when I enter my email address (bob@here.com) and password 
        # (bob) into the login form and click on the Login button, the page I get in 
        # response is a version of the home page with the login form replaced by the message
        # "Logged in as bob@here.com" and a button labelled Logout.    
        
        self.doLogin(email, password)
        
        # get another page
            
        driver.find_element_by_link_text('About').click()
        
        # expect to see user email address in returned page
        text = driver.find_element_by_tag_name('body').text
    
        self.assertIn("Logged in as %s" % email, text, "Logged in message not found in About page")
    
        try:
            logouts = driver.find_element_by_name('logout')
        except NoSuchElementException:
                self.fail("no logout button found in About page")
    


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main(warnings='ignore')