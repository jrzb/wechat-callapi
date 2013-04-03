#!/usr/bin/env python

from google.appengine.ext import db

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