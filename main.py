#!/usr/bin/env python
import os
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
	
	def getXmlOneNodeValue(self,xmlNode,name):
		nodes = xmlNode.getElementsByTagName(name) if xmlNode else []
		return nodes[0].childNodes[0].nodeValue if nodes[0] and nodes[0].childNodes else ''
		#logging.info(val)
		#return val
	
	def parseXml(self,xml):
		dom = minidom.parseString(xml)
		self.ToUserName = self.getXmlOneNodeValue(dom,'ToUserName')
		self.FromUserName = self.getXmlOneNodeValue(dom,'FromUserName')
		self.CreateTime = self.getXmlOneNodeValue(dom,'CreateTime')
		self.MsgType = self.getXmlOneNodeValue(dom,'MsgType')
		if self.MsgType == 'text':
			self.Content = self.getXmlOneNodeValue(dom,'Content')
		elif self.MsgType == 'image':
			self.PicUrl = self.getXmlOneNodeValue(dom,'PicUrl')
		elif self.MsgType == 'location':
			self.Location_X = float(self.getXmlOneNodeValue(dom,'Location_X'))
			self.Location_Y = float(self.getXmlOneNodeValue(dom,'Location_Y'))
			self.Scale = long(self.getXmlOneNodeValue(dom,'Scale'))
			self.Label = self.getXmlOneNodeValue(dom,'Label')
		elif self.MsgType == 'event':
			self.EventKey = long(self.getXmlOneNodeValue(dom,'EventKey'))
			self.Event = self.getXmlOneNodeValue(dom,'Event')
		elif self.MsgType == 'link':
			self.Title = self.getXmlOneNodeValue(dom,'Title')
			self.Description = self.getXmlOneNodeValue(dom,'Description')
			self.Url = self.getXmlOneNodeValue(dom,'Url')
			
		if self.MsgType != 'event':
			self.MsgId = long(self.getXmlOneNodeValue(dom,'MsgId'))
	
	def testParseXml(self):
		xml = ( "<xml><ToUserName><![CDATA[gh_f688fa7c5f0d]]></ToUserName>"
				"<FromUserName><![CDATA[ozXqJjuFc91lDnGpK8Ys7imuftik]]></FromUserName>"
				"<CreateTime>1364808655</CreateTime>"
				"<MsgType><![CDATA[text]]></MsgType>"
				"<Content><![CDATA[]]></Content>"
				"<MsgId>5861808538522746968</MsgId>"
				"</xml>")
		self.parseXml(xml)
		logging.info(xml)
		logging.info(self.Content)

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
		
		#talk = Talk()
		#talk.testParseXml()
		
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
		#logging.info(signature);
		#logging.info(tempStr);
		return signature == tempStr
		
	def post(self):
		if self.checkSignature():
			postStr  = self.request.body # xml str	
			#logging.info(postStr)
			if (not postStr.isspace()) and (not postStr == ''): #no empty
				#logging.debug(postStr)
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