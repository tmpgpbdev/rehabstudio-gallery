import unittest
import webtest

from google.appengine.api import users
from google.appengine.ext import testbed
from google.appengine.ext import ndb


from models import GalleryImage
import main

# For this demo and testing, lets turn off datastore caching
ndb.get_context().set_cache_policy(False)


class BaseTestClass(unittest.TestCase):

    """
    Base test case class to hold commen functionality
    """

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_user_stub()
        self.testbed.init_memcache_stub()

    def loginUser(self, email='gary@example.com', user_id='123'):
        self.testbed.setup_env(
            user_email=email,
            user_id=user_id,
            user_is_admin='0',
            overwrite=True)

    def tearDown(self):
        self.testbed.deactivate()


class MainUnitTestCase(BaseTestClass):

    """
    Core unit tests to ensure functionality works as expected
    """

    def testLogin(self):
        # Log in a user
        self.assertFalse(users.get_current_user())
        self.loginUser()
        self.assertEquals(users.get_current_user().email(), 'gary@example.com')

    def test_create(self):
        # Try and write an image to datastore
        GalleryImage().put()
        self.assertEqual(1, len(GalleryImage.query().fetch(2)))

    def test_filter(self):
        # Test our important filter query works as expected
        GalleryImage(is_public=True).put()
        GalleryImage(is_public=False).put()

        private_images = GalleryImage.query().filter(GalleryImage.is_public == False).fetch(2)
        public_images = GalleryImage.query().filter(GalleryImage.is_public == True).fetch(2)

        self.assertEqual(1, len(private_images))
        self.assertEqual(1, len(public_images))


class MainIntegrationTestCase(BaseTestClass):

    """
    Core end to end tests to ensure functionality works as expected
    """

    def setUp(self):
        super(MainIntegrationTestCase, self).setUp()

        self.testbed.init_app_identity_stub()
        self.testbed.init_urlfetch_stub()
        self.testbed.init_blobstore_stub()
        self.testbed.init_images_stub()
        self.test_app = webtest.TestApp(main.app)

        self.insert_values = {'title': 'My Test Gallery Image', 'location': 'London',
                              'is_public': '1', 'description': 'Test'}

    def test_load_landing_page(self):
        # Just test the landing pages loads
        response = self.test_app.get('/')
        assert response.status_int == 200

    def test_upload_image(self):
        # Log in default user
        self.loginUser()

        # Upload image
        response = self.test_app.post('/upload',
                                      params=self.insert_values,
                                      upload_files=[('image', 'test', 'test', 'image/jpeg')])
        assert response.status_int == 302

        # Test the uploaded image appears on the landing page
        landing_page_response = response.follow()
        assert landing_page_response.status_int == 200
        assert 'My Test Gallery Image' in landing_page_response.body

    def test_upload_private_image(self):
        # Log in default user
        self.loginUser()

        # Set private values
        self.insert_values['title'] = 'My Private Image'
        self.insert_values['is_public'] = False

        # Upload image
        response = self.test_app.post('/upload',
                                      params=self.insert_values,
                                      upload_files=[('image', 'test', 'test', 'image/jpeg')])
        assert response.status_int == 302

        # Test the uploaded image appears on the landing page
        landing_page_response = response.follow()
        assert landing_page_response.status_int == 200
        assert 'My Private Image' in landing_page_response.body

        # Log out user and test we do not see the private image
        self.loginUser('', '')
        no_user_response = self.test_app.get('/')
        assert 'My Private Image' not in no_user_response.body

        # Log in a different user and test we do not see the private image
        self.loginUser('another.user@example.com', '111')
        new_user_response = self.test_app.get('/')
        assert 'My Private Image' not in new_user_response.body


if __name__ == '__main__':
    unittest.main()
