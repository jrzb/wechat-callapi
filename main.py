#!/usr/bin/env python
import os
import hashlib
import time 
import logging

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template

from wetalk.models import Reply
from wetalk.models import Talk

# main page
class MainPage(webapp.RequestHandler):
	def get(self):
		echostr = self.request.get('echostr')
		self.response.headers['Content-Type'] = 'text/html'
		if self.checkSignature():
			self.response.write(echostr)
		else:
			talks = db.GqlQuery("SELECT * "
                            "FROM Talk "
                            "ORDER BY MsgId DESC LIMIT 1000")
			template_values = {
				'talks':talks
			}

			self.response.write(
				template.render('tpl/index.html',template_values))
    
	def checkSignature(self):
		token = 'wechat' # your token
		signature = self.request.get('signature')
		timestamp = self.request.get('timestamp')
		nonce = self.request.get('nonce')
		tmpArr = [token, timestamp, nonce];
		tmpArr.sort()
		tempStr = "".join(tmpArr)
		tempStr = hashlib.sha1(tempStr).hexdigest()
		return signature == tempStr
		
	def post(self):
		if self.checkSignature():
			postStr  = self.request.body # xml str	
			
			if (not postStr.isspace()) and (not postStr == ''): #no empty
				talk = Talk()
				talk.parseXml(postStr)
				talk.put()
				# reply 
				reply = Reply()
				reply.ToUserName = talk.FromUserName
				reply.FromUserName = talk.ToUserName
				reply.CreateTime = str(time.time())
				reply.MsgType = "text"
				reply.Content = "/::D Thinks !"
				self.response.write(reply.toXml())
				
#run wsgi app
app = webapp.WSGIApplication([('/', MainPage)],debug=True)