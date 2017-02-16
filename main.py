#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)


class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)
		
	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)
		
	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class BlogPost(db.Model):
	title = db.StringProperty(required = True)
	blogPost = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
		
class ViewPostHandler(webapp2.RequestHandler):
	def get(self, id):
		postedBlog = BlogPost.get_by_id(int(id))
		
		if postedBlog:
			self.response.write(postedBlog.blogPost)
		else:
			self.response.write("There is no post for that id")
			
class NewPost(Handler):
	def render_newpost(self, title="", blogPost="", error=""):
		self.render("newpost.html", title=title, blogPost=blogPost, error=error)
	
	def get(self):
		self.render_newpost()
		
	def post(self):
		title = self.request.get("title")
		blogPost = self.request.get("blogPost")
		
		if title and blogPost:
			a = BlogPost(title = title, blogPost = blogPost)
			a.put()
			
			self.redirect("/blog/" + str(a.key().id()))
		
		else:
			error = "we need both a title and a blog post!"
			self.render_newpost(title, blogPost, error)

		
class MainPage(Handler):
	def render_front(self, title="", blogPost="", error=""):
		blogPosts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC LIMIT 5")
		
		self.render("blog.html", title=title, blogPost=blogPost, error=error, blogPosts=blogPosts)
	
	def get(self):
		self.render_front()
		
	# def post(self):
		# title = self.request.get("title")
		# blogPost = self.request.get("blogPost")
		
		# if title and blogPost:
			# a = BlogPost(title = title, blogPost = blogPost)
			# a.put()
			
			# self.redirect("/blog")
		# else:
			# error = "we need both a title and a blogPost!"
			# self.render_front(title, blogPost, error)
			

app = webapp2.WSGIApplication([("/", MainPage), ('/blog', MainPage), ("/newpost", NewPost), webapp2.Route('/blog/<id:\d+>', ViewPostHandler)], debug=True)
