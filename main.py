#!/usr/bin/env python
import hashlib 
import logging

from webob import Request

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template

# talk class
class Talk(db.Model):
	xml = db.StringProperty()
	date = db.DateTimeProperty(auto_now_add=True)

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
                            "ORDER BY date DESC LIMIT 100")
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
		tempStr =nonce + timestamp + token
		tempStr = hashlib.sha1(tempStr).hexdigest()
		
		logging.debug('signature: '+tempStr)
		return signature == tempStr
		
	def post(self):
		if self.checkSignature():
			args_dic = self.request.arguments()
			
			args_str = ''
			for k in args_dic:
				args_str += k+'='+self.request.get(k)
			
			logging.debug(args_str)
						
			postStr  = self.request.get('HTTP_RAW_POST_DATA')
						
			if (not postStr.isspace()) and (not postStr == ''): #no empty
				talk = Talk()
				talk.xml = postStr
				talk.put()
#run wsgi app
app = webapp.WSGIApplication([('/', MainPage)],debug=True)