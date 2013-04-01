#!/usr/bin/env python
import jinja2
import os
import hashlib
import time 
import logging

from xml.dom import minidom

from google.appengine.ext import webapp
from google.appengine.ext import db
#from google.appengine.ext.webapp import template



jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

# talk class
class Talk(db.Model):
	ToUserName = db.StringProperty()
	FromUserName = db.StringProperty()
	CreateTime = db.StringProperty()
	MsgType = db.StringProperty()
	Content = db.TextProperty()
	MsgId = db.IntegerProperty()
	
	PicUrl = db.TextProperty()
	
	Event = db.StringProperty()
	EventKey = db.StringProperty()
	
	Location_X = db.FloatProperty()
	Location_Y = db.FloatProperty()
	Scale = db.IntegerProperty()
	Label = db.StringProperty()
	
	Title = db.StringProperty()
	Description = db.StringProperty()
	Url = db.StringProperty()
	
	
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
			self.Location_X = dom.getElementsByTagName('Location_X')[0].childNodes[0].nodeValue;
			self.Location_Y = dom.getElementsByTagName('Location_Y')[0].childNodes[0].nodeValue;
			self.Scale = dom.getElementsByTagName('Scale')[0].childNodes[0].nodeValue;
			self.Label = dom.getElementsByTagName('Label')[0].childNodes[0].nodeValue;
		elif self.MsgType == 'event':
			self.EventKey = long(dom.getElementsByTagName('EventKey')[0].childNodes[0].nodeValue);
			self.Event = dom.getElementsByTagName('Event')[0].childNodes[0].nodeValue;
		elif self.MsgType == 'link':
			self.Title = long(dom.getElementsByTagName('Title')[0].childNodes[0].nodeValue);
			self.Description = dom.getElementsByTagName('Description')[0].childNodes[0].nodeValue;
			self.Url = dom.getElementsByTagName('Url')[0].childNodes[0].nodeValue;
			
		if self.MsgType != 'event':
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
			template = jinja_environment.get_template('tpl/index.html')
			self.response.write(
				template.render(template_values))
    
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