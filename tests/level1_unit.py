'''
Created on Mar 3, 2014

@author: Steve Cassidy
'''
import unittest
import tempfile
import os

from mock import list_images
import templating

class LevelAUnitTests(unittest.TestCase):


    def test_list_images(self):
        """Test the 'mock' database interface."""
        
        image_list = list_images(3)
        
        self.assertEqual(3, len(image_list))        
        self.assertEqual(('cycling.jpg', '2014-01-14', 'bob@here.com', ['cool photo', 'thx']), image_list[0])
        

    def test_render_from_string(self):
        """Test that the templating module render_from_string works ok"""
        
        
        template = ">>$one<< >>$two<< >>${three}<<"
        
        # render with all variables of different types
        d = {'one': 1, 'two': 'two', 'three': [3]}
        
        self.assertEqual([b">>1<< >>two<< >>[3]<<"], templating.render_from_string(template, d))
        
        # with missing values
        d = {'one': 1}
        
        self.assertEqual([b">>1<< >>$two<< >>${three}<<"], templating.render_from_string(template, d))


    def test_render(self):
        """Test that the templating render works rendering from a file"""
        
        template = ">>$one<< >>$two<< >>${three}<<"
        
        (handle, filepath) = tempfile.mkstemp(dir=templating.TEMPLATE_DIR)
        self.addCleanup(lambda: os.unlink(filepath))
        
        os.write(handle, template.encode())
        os.close(handle)
        
        templatename = os.path.basename(filepath)
        
        # render with all variables
        d = {'one': 1, 'two': 'two', 'three': [3]}
        
        self.assertEqual([b">>1<< >>two<< >>[3]<<"], templating.render(templatename, d))
        # with missing values
        d = {'one': 1}
        
        self.assertEqual([b">>1<< >>$two<< >>${three}<<"], templating.render_from_string(template, d))
        




if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()