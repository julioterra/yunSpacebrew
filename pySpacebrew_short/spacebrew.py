#!/usr/bin/python

from websocket import websocket
from bridge import json
import time

class Spacebrew(object):

	# Define any runtime errors we'll need
	class ConfigurationError(Exception):
		def __init__(self, brew, explanation):
			self.brew = brew
			self.explanation = explanation
		def __str__(self):
			return repr(self.explanation)

	class Slot(object):
		def __init__(self, name, brewType, default = None):
			self.name = name
			self.type = brewType
			self.value = None
			self.default = default
		def makeConfig(self):
			d = { 'name':self.name, 'type':self.type, 'default':self.default }
			return d
		
	class Publisher(Slot):
		pass

	class Subscriber(Slot):
		def __init__(self, name, brewType, default = None):
			super(Spacebrew.Subscriber,self).__init__(name,brewType,default)
			self.callbacks=[]
		def subscribe(self, target):
			self.callbacks.append(target)
		def unsubscribe(self, target):
			self.callbacks.remove(target)
		def disseminate(self, value):
			for target in self.callbacks:
				target(value)

	class Events(object):
		def __init__(self, events):
			self.callbacks = {}
			for event in events:
				# print("creating method array for " + event)
				self.callbacks[event] = []
		def register(self, event, target):
			# print("adding method to " + event)
			assert type(self.callbacks[event]) is list
			# print("added method to " + event)
			self.callbacks[event].append(target)
		def call(self, event):
			# print("calling method for " + event)
			assert type(self.callbacks[event]) is list
			for target in self.callbacks[event]:
				# print("found method for " + event)
				target()


	def __init__(self, name, description="", server="sandbox.spacebrew.cc", port=9000):
		self.server = server
		self.port = port
		self.name = name
		self.description = description
		self.connected = False
		self.started = False
		self.publishers = {}
		self.subscribers = {}
		self.ws = None
		self.events = self.Events(["open", "close", "error", "message"])

	def addPublisher(self, name, brewType="string", default=None):
		if self.connected:
			raise ConfigurationError(self,"Can not add a new publisher to a running Spacebrew instance (yet).")
		else:
			self.publishers[name]=self.Publisher(name, brewType, default)
	
	def addSubscriber(self, name, brewType="string", default=None):
		if self.connected:
			raise ConfigurationError(self,"Can not add a new subscriber to a running Spacebrew instance (yet).")
		else:
			self.subscribers[name]=self.Subscriber(name, brewType, default)

	def addListener(self, name, target):
		self.events.register(name, target)

	def makeConfig(self):
		subs = map(lambda x:x.makeConfig(),self.subscribers.values())
		pubs = map(lambda x:x.makeConfig(),self.publishers.values())
		d = {'config':{
			'name':self.name,
			'description':self.description,
			'publish':{'messages':pubs},
			'subscribe':{'messages':subs},
			}}
		return d

	def on_open(self, ws):
		ws.send(json.write(self.makeConfig()))
 		self.connected = True
 		self.events.call("open")

	def on_message(self,ws,message):
		full = json.read(message)[0]
		msg = full["message"]
		sub = self.subscribers[msg['name']]
		sub.disseminate(msg['value'])
 		self.events.call("message")

	def on_error(self,ws,error):
		# logging.error("[on_error] ERROR: {0}".format(error))
		# logging.error("[on_error] self started " + str(self.started))
 		self.events.call("error")
		self.on_close(ws)

	def on_close(self, ws):
		self.connected = False
 		self.events.call("close")
		while self.started and not self.connected:
			time.sleep(5)
			self.run()

	def publish(self,name,value):
		publisher = self.publishers[name]

		if publisher.type == "boolean":
			if value == True: 
				value = "true"
			else:
				value = "false"

		message = {'message': {
			'clientName':self.name,
			'name':publisher.name,
			'type':publisher.type,
			'value':value } }
		self.ws.send(json.write(message))

	def subscribe(self,name,target):
		subscriber = self.subscribers[name]
		subscriber.subscribe(target)

	def run(self):
		self.ws = websocket.WebSocketApp( "ws://{0}:{1}".format(self.server,self.port),
						on_message = lambda ws, msg: self.on_message(ws, msg),
						on_error = lambda ws, err: self.on_error(ws,err),
						on_close = lambda ws: self.on_close(ws), 
						on_open = lambda ws: self.on_open(ws)
						)
		self.ws.on_open = lambda ws: self.on_open(ws)
		self.ws.run_forever()

	def start(self):
		self.started = True
		self.run()

	def stop(self):
		self.started = False
		if self.ws is not None:
			self.ws.close()
		# self.thread.join()

if __name__ == "__main__":
	print """
This is the Spacebrew module. 
See spacebrew_ex.py for usage examples.
"""
	
