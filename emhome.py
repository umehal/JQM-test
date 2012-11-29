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

#Import Section
import cgi
import os
import uuid
import json
import hashlib
import datetime
import os.path
import gqljson
import webapp2
import urllib2

from google.appengine.api.labs import taskqueue
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.api import images
from webapp2_extras import sessions
import logging
from google.appengine.api import search
from gaesessions import get_current_session

#Basic Auth
from base64 import b64decode
from google.appengine.ext import webapp

#Import Section END

#Auth Section
class BaseSessionRequestHandler(webapp2.RequestHandler):
    def dispatch(self):
        self.session_store = sessions.get_store(request=self.request)
        try:
            webapp2.RequestHandler.dispatch(self)
        finally:
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        backend = self.session_store.config.get('default_backend','securecookie')
        return self.session_store.get_session(backend=backend)

class BasicAuthentication(BaseSessionRequestHandler):
  def get(self):
    
    if self.session.get('username',0):
      username = self.session.get('username',0)
      self.session['username'] = username
      path = os.path.join(os.path.dirname(__file__), 'login.html')
      template_values = {'username':username}
    else:
      path = os.path.join(os.path.dirname(__file__), 'index.html')
      template_values = {}
    
    self.response.out.write(template.render(path, template_values))

#Auth Section END

#Data Store Section
class Secret(db.Model):
  User_ID = db.StringProperty(multiline=False)
  name = db.StringProperty(multiline=False)
  pw = db.StringProperty(multiline=False)
  answer = db.StringProperty(multiline=False)
  wrong = db.IntegerProperty()
  admin = db.StringProperty(multiline=False)

class Member(db.Model):
  name = db.StringProperty(multiline=False)
  displayName = db.StringProperty(multiline=False)
  URL = db.StringProperty(multiline=False)
  introduction = db.TextProperty()
  commentsNum = db.StringProperty()
  img = db.StringProperty(multiline=False)
  question = db.StringProperty(multiline=False)
  date = db.DateTimeProperty(auto_now_add=True)

class Comments(db.Model):
  com_ID = db.StringProperty(multiline=False)
  name = db.StringProperty(multiline=False)
  displayName = db.StringProperty(multiline=False)
  title = db.StringProperty(multiline=False)
  body = db.StringProperty(multiline=True)
  date = db.DateTimeProperty(auto_now_add=True)
  category = db.StringProperty(multiline=False)
  views = db.IntegerProperty()
  rankingViews = db.IntegerProperty()
  bookmark = db.IntegerProperty()
  rankingBookmark = db.IntegerProperty()

class Bookmark(db.Model):
  name = db.StringProperty(multiline=False)
  com_ID = db.StringProperty(multiline=False)
  date = db.DateTimeProperty(auto_now_add=True)

#Data Store Section END

#API Section
class checkSession(BaseSessionRequestHandler):
  def post(self):  
    
    if self.session.get('username',0):
      username = self.session.get('username',0)
      self.session['username'] = username
      res = username
    else:
      res = "0"
    self.response.out.write(res)

class register(BaseSessionRequestHandler):
  def post(self):
  
    name = self.request.get('name').encode('UTF-8')
    displayName = self.request.get('displayName').encode('UTF-8')
    pw = self.request.get('pw').encode('UTF-8')
    introduction = self.request.get('introduction').encode('UTF-8')
    question = self.request.get('question').encode('UTF-8')
    answer = self.request.get('answer').encode('UTF-8')
    member = Member()
    user = Secret()
    users = db.GqlQuery("SELECT __key__ FROM Secret WHERE name = :1",name)
    if users.count() == 0:
      ID = str(uuid.uuid1())
      user.User_ID = ID
      user.name = name
      user.pw = hashlib.sha256(ID + pw).hexdigest()
      user.answer = hashlib.sha256(ID + answer).hexdigest()
      user.wrong = 0
      user.admin = "0"
      user.put()
      member.name = name
      member.displayName = displayName.decode('UTF-8')
      if displayName == "":
        member.displayName = name
      member.introduction = introduction.decode('UTF-8')
      member.commentsNum = "0"
      member.question = question.decode('UTF-8')
      member.put()
      res = "SUCCEEDED"
      self.session['username'] = name
    else:
      res = "0"
    self.response.out.write(res)
    
class login(BaseSessionRequestHandler):
  def post(self):

    name = self.request.get('name').encode('UTF-8')
    pw = self.request.get('pw').encode('UTF-8')
    users = db.GqlQuery("SELECT * FROM Secret WHERE name = :1 LIMIT 1",name)
    if users.count() != 0:
      user = users.get()
      shapw = hashlib.sha256(user.User_ID + pw).hexdigest()
      if shapw == user.pw:
        res = "1"
        self.session['username'] = name
      else:
        res = "0"
    else:
      res = "0"
    self.response.out.write(cgi.escape(unicode(res, 'UTF-8')))

class logout(BaseSessionRequestHandler):
  def post(self):

    if self.session.get('username',0):
      self.session['username'] = None
      self.response.out.write("0")

class existUserCheck(webapp.RequestHandler):
  def post(self):

    name = self.request.get('name').encode('UTF-8')
    users = db.GqlQuery("SELECT __key__ FROM Member WHERE name = :1",name)
    if users.count() == 0:
      res = "0"
    elif users.count() == 1:
      res = "1"                            
    self.response.out.write(cgi.escape(unicode(res, 'UTF-8')))

class postComment(BaseSessionRequestHandler):
  def post(self):
  
    comment = Comments()
    com_ID = str(uuid.uuid1())
    name = self.request.get('name').encode('UTF-8')
    if name == "":
      name = self.session.get('username',0)
    if name == None:
      res = "NOSESSION"
    else:
      displayName = self.request.get('displayName').encode('UTF-8')
      title =  self.request.get('title').encode('UTF-8')
      body =  self.request.get('body').encode('UTF-8')
      category = self.request.get('category').encode('UTF-8')
      comment.com_ID = com_ID.decode('UTF-8')
      comment.name = name.decode('UTF-8')
      if displayName:
        comment.displayName = displayName.decode('UTF-8')
      if title:
        comment.title = title.decode('UTF-8')
      if body:
        comment.body = body.decode('UTF-8')
      comment.category = category.decode('UTF-8')
      comment.views = 0
      comment.rankingViews = 0
      comment.bookmark = 0
      comment.rankingBookmark = 0
      comment.put()
      res = 'SUCCEEDED'
    json_results = gqljson.encode(res)
    self.response.out.write(cgi.escape(unicode(res, 'UTF-8')))

class getCategoryCommentList(BaseSessionRequestHandler):
  def post(self):

    comment = Comments()
    username = self.request.get('name').encode('UTF-8')
    category = self.request.get('category').encode('UTF-8')
    limit = self.request.get('limit').encode('UTF-8')
    offset = self.request.get('offset').encode('UTF-8')
    if username == "":
      username = self.session.get('username',0)
    if username == None:
      res = "NOSESSION"
    else:
      username = username.decode('UTF-8')
      if limit:
        if offset:
          comment = db.GqlQuery("SELECT * FROM Comments WHERE category = :1 ORDER BY date DESC",category).fetch(limit=int(limit),offset=int(offset))
        else:
          comment = db.GqlQuery("SELECT * FROM Comments WHERE category = :1 ORDER BY date DESC",category).fetch(limit=int(limit),offset=0)
      else:
        comment = db.GqlQuery("SELECT * FROM Comments WHERE category = :1 ORDER BY date DESC",category) 
      if comment:
        res = gqljson.GqlEncoder(ensure_ascii=False).encode(comment)
      else:
          res = "0"
    self.response.out.write(res)

class getUserCommentList(BaseSessionRequestHandler):
  def post(self):

    comment = Comments()
    username = self.request.get('name').encode('UTF-8')
    limit = self.request.get('limit').encode('UTF-8')
    offset = self.request.get('offset').encode('UTF-8')
    if username == "":
      username = self.session.get('username',0)
    if username == None:
      res = "NOSESSION"
    else:
      username = username.decode('UTF-8')
      if limit:
        if offset:
          comment = db.GqlQuery("SELECT * FROM Comments WHERE name = :1 ORDER BY date DESC",username).fetch(limit=int(limit),offset=int(offset))
        else:
          comment = db.GqlQuery("SELECT * FROM Comments WHERE name = :1 ORDER BY date DESC",username)
      else:
        comment = db.GqlQuery("SELECT * FROM Comments WHERE name = :1 ORDER BY date DESC",username)
      if comment:
        res = gqljson.GqlEncoder(ensure_ascii=False).encode(comment)
      else:
          res = "0"
    self.response.out.write(res)

class addView(webapp.RequestHandler):
  def post(self):

    com_ID = self.request.get('com_ID').encode('UTF-8')
    com_ID = com_ID.decode('UTF-8')
    taskqueue.add(url='/incrementView', params={'com_ID': com_ID})

class incrementView(webapp.RequestHandler):
  def post(self):

    comment = Comments()
    com_ID = self.request.get('com_ID').encode('UTF-8')
    comment = db.GqlQuery("SELECT * FROM Comments WHERE com_ID = :1",com_ID)

    commentData = comment.get()

    if commentData:
      if commentData.views > 0:
        viewNum = commentData.views
        viewNumInt = int(viewNum) + 1
        commentData.views = viewNumInt
        """
        viewNum = commentData.rankingViews
        viewNumInt = int(viewNum) + 1
        commentData.rankingViews = viewNumInt
        """
        rankNum = commentData.rankingBookmark
        rankNumInt = int(rankNum) + 1
        commentData.rankingBookmark = viewNumInt
        commentData.put()
      else:
        commentData.views = 1
        commentData.rankingBookmark = 1
        commentData.put()

class addBookmark(BaseSessionRequestHandler):
  def post(self):
  
    bookmark = Bookmark()
    name = self.request.get('name').encode('UTF-8')
    if name == "":
      name = self.session.get('username',0)
    if name == None:
      res = "NOSESSION"
    else:
      com_ID = self.request.get('com_ID').encode('UTF-8')
      bookmark.name = name.decode('UTF-8')        
      bookmark.com_ID = com_ID.decode('UTF-8')
      bookmarks = db.GqlQuery("SELECT __key__ FROM Bookmark WHERE name = :1 AND com_ID = :2",name,com_ID)
      if bookmarks.count():
        res = 'REGISTERED'
      else:
        bookmark.name = name.decode('UTF-8')        
        bookmark.com_ID = com_ID.decode('UTF-8')
        bookmark.put()
        taskqueue.add(url='/incrementBookmark', params={'com_ID': com_ID})
        res = 'SUCCEEDED'
    json_results = gqljson.encode(res)
    self.response.out.write(cgi.escape(unicode(res, 'UTF-8')))

class incrementBookmark(webapp.RequestHandler):
  def post(self):
  
    commentData = Comments()
    com_ID = self.request.get('com_ID').encode('UTF-8')
    comment = db.GqlQuery("SELECT * FROM Comments WHERE com_ID = :1 LIMIT 1",com_ID)
    commentData = comment.get()
    commentData.bookmark = commentData.bookmark + 1
    commentData.rankingBookmark = commentData.rankingBookmark + 1
    commentData.put()

"""
Delete Bookmark

class deleteBookmark(BaseSessionRequestHandler):
  def post(self):
  
    bookmark = Bookmark()
    name = self.request.get('name').encode('UTF-8')
    if name == "":
      
      name = self.session.get('username',0)
    if name == None:
      res = "NOSESSION"
    else:
      Novel_ID = self.request.get('Novel_ID').encode('UTF-8')
      bookmark = db.GqlQuery("SELECT __key__ FROM Bookmark WHERE name = :1 AND Novel_ID = :2",name,Novel_ID)
      if bookmark:
        if bookmark.count():
          db.delete(bookmark)
          res = "DELETED"
          taskqueue.add(url='/decrementBookmark', params={'Novel_ID': Novel_ID})
        else:
          res = "0"
      else:
        res = "0"
    self.response.out.write(res)

class decrementBookmark(webapp.RequestHandler):
  def post(self):
  
    novelData = Novel()
    Novel_ID = self.request.get('Novel_ID').encode('UTF-8')
    novel = db.GqlQuery("SELECT * FROM Novel WHERE Novel_ID = :1 LIMIT 1",_ID)
    novelData = novel.get()
    novelData.bookmark = novelData.bookmark - 1
    novelData.rankingBookmark = novelData.rankingBookmark - 1
    novelData.put()
"""

class getViewRanking(webapp.RequestHandler):
  def post(self):
  
    limit = self.request.get('limit').encode('UTF-8')
    offset = self.request.get('offset').encode('UTF-8')
    
    comment = None#memcache.get('dailyViewRanking')
    if comment is None:
        comments = db.GqlQuery("SELECT * FROM Comments WHERE rankingViews > 0 ORDER BY rankingViews DESC LIMIT 100")
        #comments = Comments.all().filter('publish = ', '1').filter('privacy = ', 'allview').order('-rankingViews').fetch(100)
        #res = gqljson.GqlEncoder(ensure_ascii=False).encode(comments)
        #memcache.add(key='dailyViewRanking', value=comments, time=100000)
        comment = comments
    if limit:
      if offset:
        comment = comment.fetch(limit=int(limit),offset=int(offset))
      else:
        comment = comment.fetch(limit=int(limit),offset=0)
    else:
      comment = comment.fetch(limit=3,offset=0)
      
    if comment:   
      res = gqljson.GqlEncoder(ensure_ascii=False).encode(comment)
    else:
        res = "0"
    self.response.out.write(res)

class getBookmarkRanking(webapp.RequestHandler):
  def post(self):
  
    comment = Comments()
    limit = self.request.get('limit').encode('UTF-8')
    offset = self.request.get('offset').encode('UTF-8')
    if limit:
      if offset:
        comment = db.GqlQuery("SELECT * FROM Comments WHERE rankingBookmark > 0 ORDER BY rankingBookmark DESC").fetch(limit=int(limit),offset=int(offset))
      else:
        comment = db.GqlQuery("SELECT * FROM Comments WHERE rankingBookmark > 0 ORDER BY rankingBookmark DESC LIMIT 3")
    else:
      comment = memcache.get('bookmarkRankingNovels')
      if comment is None:
        comment = db.GqlQuery("SELECT * FROM Comments WHERE rankingBookmark > 0 ORDER BY rankingBookmark DESC LIMIT 3")
        memcache.add(key='bookmarkRankingNovels', value=comment, time=600)
    if comment:   
      res = gqljson.GqlEncoder(ensure_ascii=False).encode(comment)
    else:
        res = "0"
    self.response.out.write(res)

#API Section END

#Handler Section
application = webapp.WSGIApplication([('/', BasicAuthentication),
  ('/checkSession', checkSession),
  ('/register', register),
  ('/login', login),
  ('/logout', logout),
  ('/existUserCheck', existUserCheck),
  ('/postComment', postComment),
  ('/getCategoryCommentList', getCategoryCommentList),
  ('/getUserCommentList', getUserCommentList),
  ('/addView', addView),
  ('/incrementView', incrementView),
  ('/addBookmark', addBookmark),
  ('/incrementBookmark', incrementBookmark),
  #('/deleteBookmark', deleteBookmark),
  #('/decrementBookmark', decrementBookmark),
  ('/getViewRanking', getViewRanking),
  ('/getBookmarkRanking', getBookmarkRanking),
  #('/updateAll', updateAll)
  ],
  debug=True,
  config={'webapp2_extras.sessions':{
    'secret_key':'1miyg9r4n3achza5s9jkdwa9t3khwu97',
    'cookie_name':'EMhomeSession',
    'session_max_age':2678400,
    'cookie_args':{
      'max_age':2678400,
      'domain':None,
      'path':'/',
      'secure':None,
      'httponly':None,
    }
  },})

#Handler Section END
