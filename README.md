# rehabstudio Gallery App

Simple Gallery app which demonstrates the usage of Google App Engine and 
Google Cloud Storage.

Users are able to log in and upload an image and some image information to the Gallery. 
Users can define an image as being Public or Private. If an image is Public, it will appear 
on the landing page and the landing page of every logged in user. If an image is set as Private, 
it will only appear on the landing page of that logged in user who uploaded it.

## Tech used

As requested in the requirements, this pojects is based on:
 - Python 2.7 on Google App Engine with the webapp2 framework
 - Google Cloud Storage to store the images
 - Cloud Datastore with the NDB client to store details of the image
 
I was hoping to implement a React frontend to interact with this app Restfully, but time 
constraints led me to simply adding the lightweight Bulma CSS library to style the index.html landing page.

## Unit test

Basic Unit test and End to end tests are implemented in the main_test.py file.

## Other notes

This app showcases basic functionality, some noticable imrpovements are as follows 
if this was a project put into production without time constraints:

 - Restful API backend
 - React/other JS framework serving the frontend
 - Profile functionality for users to manage their uploads
 - Server side validation: form values, image type, image size
 - Image optimisation on upload. EG: resizing, minification
 - Pagination or dynamic 'show more', currently we are just fetching the latest 20 images
 - Use a framework such as Django or Flask
 - Use Google App Engine Flexible environment to support Python 3 and Dockerfiles
 - Enable caching: disabled for this testing instance so that we see the uploaded images straight after upload redirect