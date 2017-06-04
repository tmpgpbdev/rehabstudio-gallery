from cgi import FieldStorage
import os
import uuid

from google.appengine.ext import blobstore
from google.appengine.api import images
from google.appengine.ext import ndb
from google.appengine.api import users

import cloudstorage as gcs
import jinja2
import webapp2

from models import GalleryImage, GalleryUser


# Set up Jinja config
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


# Our Google Cloud Storage bucket name
BUCKET_NAME = os.environ['GCS_BUCKET']


# Cloud storage retries
gcs.set_default_retry_params(
    gcs.RetryParams(
        initial_delay=0.2, max_delay=5.0, backoff_factor=2, max_retry_period=15))


# For this demo and testing, lets turn off datastore caching
ndb.get_context().set_cache_policy(False)


class MainPage(webapp2.RequestHandler):

    """
    Main page here handes login/logout, uploading of images and
    viewing the gallery
    """

    def get_auth_vars(self, user):
        if user:
            auth_url = users.create_logout_url(self.request.uri)
            auth_url_text = 'Logout'
        else:
            auth_url = users.create_login_url(self.request.uri)
            auth_url_text = 'Login'
        return auth_url, auth_url_text

    def get_gallery_images(self, user):
        if user:
            # If user is logged in, show all public images and the users private images
            gallery_images = GalleryImage \
                .query() \
                .filter(ndb.OR(GalleryImage.is_public == True,
                               GalleryImage.gallery_user.user_id == users.get_current_user().user_id()))
        else:
            # If user is not logged in, show only public images
            gallery_images = GalleryImage \
                .query() \
                .filter(GalleryImage.is_public == True)

        gallery_images.order(-GalleryImage.date)
        gallery_images.fetch(20)

        return gallery_images

    def get(self):
        user = users.get_current_user()
        auth_url, auth_url_text = self.get_auth_vars(user)

        gallery_images = self.get_gallery_images(user)

        template_values = {
            'images': gallery_images,
            'user': user,
            'auth_url': auth_url,
            'auth_url_text': auth_url_text,
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


class ImageUpload(webapp2.RequestHandler):

    """
    ImageUpload class handles the upload of images from the form and into
    Google Cloud Storage. A public serving image URL is created to store into our DB
    """

    def post(self):
        # User must be logged in to upload an image
        if users.get_current_user():
            # Create new Gallery Image
            gallery_image = GalleryImage()
            gallery_image.title = self.request.get('title')
            gallery_image.location = self.request.get('location')
            gallery_image.description = self.request.get('description')
            gallery_image.is_public = True if self.request.get('is_public', 'public') == 'public' else False

            # Save user info
            gallery_image.gallery_user = GalleryUser(
                user_id=users.get_current_user().user_id(),
                email=users.get_current_user().email())

            # Using self.request.POST here so we get the upload as FieldStorage object
            image_upload = self.request.POST.get('image')

            # Make sure we have an image to upload before processing
            if isinstance(image_upload, FieldStorage):
                image_type = image_upload.type

                if 'image' in image_type:
                    # Create a unique filename
                    filename = str(uuid.uuid4())

                    # Upload image to Google Cloud Storage
                    upload_location = '/{}/{}'.format(BUCKET_NAME, filename)
                    gcs_image = gcs.open(upload_location, 'w', content_type=image_type)
                    gcs_image.write(image_upload.file.read())
                    gcs_image.close()

                    # Create a blobstore gs key so we can get our image URL
                    blobstore_filename = '/gs/{}/{}'.format(BUCKET_NAME, filename)
                    blob_key = blobstore.create_gs_key(blobstore_filename)

                    # Public image URL
                    image_url = images.get_serving_url(blob_key)

                    # Save image data
                    gallery_image.image_url = str(image_url)
                    gallery_image.image_content_type = image_upload.type
                    gallery_image.image_filename = filename

            # Write Gallery Image to datastore
            gallery_image.put()

        self.redirect('/')


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/upload', ImageUpload)], debug=True)
