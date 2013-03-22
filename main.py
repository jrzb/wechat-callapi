#!/usr/bin/env python
import hashlib
import time 
import logging

from xml.dom import minidom

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template

# talk class
class Talk(db.Model):
	ToUserName = db.StringProperty()
	FromUserName = db.StringProperty()
	CreateTime = db.StringProperty()
	MsgType = db.StringProperty()
	Content = db.TextProperty()
	PicUrl = db.TextProperty()
	MsgId = db.IntegerProperty()
	def parseXml(self,xml):
		dom = minidom.parseString(xml);
		self.ToUserName = dom.getElementsByTagName('ToUserName')[0].childNodes[0].nodeValue;
		self.FromUserName = dom.getElementsByTagName('FromUserName')[0].childNodes[0].nodeValue;
		self.CreateTime = dom.getElementsByTagName('CreateTime')[0].childNodes[0].nodeValue;
		self.MsgType = dom.getElementsByTagName('MsgType')[0].childNodes[0].nodeValue;
		if self.MsgType == 'text':
			self.Content = dom.getElementsByTagName('Content')[0].childNodes[0].nodeValue;
		elif self.MsgType == 'image':
			self.PicUrl = dom.getElementsByTagName('PicUrl')[0].childNodes[0].nodeValue;
		elif self.MsgType == 'location':
			logging.info('location msg')
		elif self.MsgType == 'event':
			logging.info('event msg')
		elif self.MsgType == 'link':
			logging.info('link msg')
		
		self.MsgId = long(dom.getElementsByTagName('MsgId')[0].childNodes[0].nodeValue);	
# reply class
class Reply(db.Model):
	ToUserName = db.StringProperty()
	FromUserName = db.StringProperty()
	CreateTime = db.StringProperty()
	MsgType = db.StringProperty()
	Content = db.TextProperty()
	_xmlTpl = ("<xml>"
	"<ToUserName><![CDATA[%s]]></ToUserName>"
	"<FromUserName><![CDATA[%s]]></FromUserName>"
	"<CreateTime>%s</CreateTime>"
	"<MsgType><![CDATA[%s]]></MsgType>"
	"<Content><![CDATA[%s]]></Content>"
	"<FuncFlag>0</FuncFlag>"
	"</xml>"); 
	def toXml(self):
		return (self._xmlTpl % (self.ToUserName,self.FromUserName,self.CreateTime,self.MsgType,self.Content)) 
    			
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
		tempStr =nonce + timestamp + token
		tempStr = hashlib.sha1(tempStr).hexdigest()
		return signature == tempStr
		
	def post(self):
		if self.checkSignature():
			postStr  = self.request.body # xml str			
			if (not postStr.isspace()) and (not postStr == ''): #no empty
				logging.debug(postStr)
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