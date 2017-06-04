from google.appengine.ext import ndb


class GalleryUser(ndb.Model):

    """
    Model for representing a user uploading images
    """

    user_id = ndb.StringProperty()
    email = ndb.StringProperty(indexed=False)


class GalleryImage(ndb.Model):

    """
    Model for representing an uploaded image
    """

    gallery_user = ndb.StructuredProperty(GalleryUser)
    title = ndb.StringProperty()
    location = ndb.StringProperty()
    description = ndb.TextProperty(indexed=False)
    image_url = ndb.BlobProperty(indexed=False)
    image_content_type = ndb.StringProperty(indexed=False)
    image_filename = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
    is_public = ndb.BooleanProperty(default=True)
