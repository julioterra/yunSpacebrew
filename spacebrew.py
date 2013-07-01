#!/usr/bin/python

from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, gethostname
from select import select
from websocket import websocket
import json
import time
import optparse
from optparse import Option
import sys
import thread


class OPT:
	SERVER 			= '--server'
	PORT 			= '--port'
	NAME 			= '-n'
	DESCRIPTION 	= '-d'
	SUBSCRIBER   	= '-s'
	PUBLISHER 		= '-p'

class ERROR:
    OK                  = (0,   '')
    SERVER_MISSING     	= (201, '(' + OPT.SERVER + ') server host not specified')
    SERVER_INVALID     	= (202, '(' + OPT.SERVER + ') "%s" is not a valid host name')
    PORT_MISSING     	= (203, '(' + OPT.PORT + ') port number not specified')
    PORT_INVALID    	= (204, '(' + OPT.PORT + ') "%s" is not a valid port number.')
    NAME_MISSING     	= (205, '(' + OPT.NAME + ') name is required and was not specified.')
    DESCRIPTION_MISSING = (206, '(' + OPT.DESCRIPTION + ') description not provided.')
    SUBSCRIBER_MISSING 	= (207, '(' + OPT.SUBSCRIBER + ') subscriber only accepts two args: type and name. %i args provided.')
    PUBLISHER_MISING 	= (208, '(' + OPT.PUBLISHER + ') publisher only accepts two args: type and name.  %i args provided.')

class SpacebrewOptParser(optparse.OptionParser):
    ERRORS = {
        OPT.SERVER     		:ERROR.SERVER_MISSING,
        OPT.PORT      		:ERROR.PORT_MISSING,
        OPT.NAME  			:ERROR.NAME_MISSING,
        OPT.DESCRIPTION     :ERROR.DESCRIPTION_MISSING,
        OPT.SUBSCRIBER      :ERROR.SUBSCRIBER_MISSING,
        OPT.PUBLISHER 		:ERROR.PUBLISHER_MISING,
    }

    def error(self, msg):
        if msg.endswith("option requires an argument"):
            opt = msg.split(None, 1)[0]
            if opt in SpacebrewOptParser.ERRORS:
                err = SpacebrewOptParser.ERRORS[opt]
                optparse.OptionParser.exit(self, err[0], 'Error: ' + err[1]+'\n')
            else:
                optparse.OptionParser.error(self, msg)
        else:
            optparse.OptionParser.error(self, msg)


class sbOptions(Option):

	ACTIONS = Option.ACTIONS + ("pubsub",)
	STORE_ACTIONS = Option.STORE_ACTIONS + ("pubsub",)
	TYPED_ACTIONS = Option.TYPED_ACTIONS + ("pubsub",)
	ALWAYS_TYPED_ACTIONS = Option.ALWAYS_TYPED_ACTIONS + ("pubsub",)

	def take_action(self, action, dest, opt, value, values, parser):
		if action == "pubsub":

			# read the subscriber and publisher arguments
			value += " "
			for arg in parser.rargs:
				if arg[:2] == "--" and len(arg) > 2: break
				if arg[:1] == "-" and len(arg) > 1: break
				value += arg + " "
			subpubArray = [ x.strip() for x in value.split(",") if x.strip() ] 

			# verify that argument meets requirements
			if len(subpubArray) == 2:
				values.ensure_value(dest, []).append({"name": subpubArray[0], "type": subpubArray[1]})
			else:
				if opt == '-s': exitWithError(ERROR.SUBSCRIBER_MISSING, len(subpubArray))
				if opt == '-p': exitWithError(ERROR.PUBLISHER_MISING, len(subpubArray))
		else:
			Option.take_action(self, action, dest, opt, value, values, parser)

def parseInput(args):
    global options
    global unusedArgs

    parser = SpacebrewOptParser(optparse.SUPPRESS_USAGE, version='1.0', option_class=sbOptions)
    parser.add_option(OPT.SUBSCRIBER, dest='subs', metavar = 'pubs: name, type', action='pubsub', help='register subscriber', default=[])
    parser.add_option(OPT.PUBLISHER, dest='pubs', metavar = 'subs: name, type', action='pubsub', help='register publisher', default=[])
    parser.add_option(OPT.SERVER, dest='server', metavar = 'server', default='sandbox.spacebrew.cc', help='spacebrew server hostname [default: %default]')
    parser.add_option(OPT.PORT, dest='port', metavar = 'port', default=9000, type="int", help='spacebrew server port number [default: %default]')
    parser.add_option(OPT.NAME, dest='name', metavar = 'name', default='Arduino Yun', help='app name [default: %default]')
    parser.add_option(OPT.DESCRIPTION, dest='description', metavar = 'description', default='', help='brief description of app')

    (options, unusedArgs) = parser.parse_args(args)

    print ("options ", str(options))

def exitWithError(err, params=None):
    errMsg = 'Error: ' + err[1] + '\n'
    msg = errMsg%params if params else errMsg
    sys.stderr.write(msg)
    sys.exit(err[0])



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
			conf = { 'name':self.name, 'type':self.type, 'default':self.default }
			return conf
		
	class Publisher(Slot):
		pass

	class Subscriber(Slot):
		pass

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
		# self.events = self.Events(["open", "close", "error", "message"])

	def addPublisher(self, name, brewType="string", default=None):
 		print ( "[addPublisher] adding a new publisher ", name, " and type ", brewType )
		if self.connected:
			raise ConfigurationError(self,"Can not add a new publisher to a running Spacebrew instance (yet).")
		else:
			self.publishers[name]=self.Publisher(name, brewType, default)
	
	def addSubscriber(self, name, brewType="string", default=None):
 		print ( "[addSubscriber] adding a new subscriber ", name, " and type ", brewType )
		if self.connected:
			raise ConfigurationError(self,"Can not add a new subscriber to a running Spacebrew instance (yet).")
		else:
			self.subscribers[name]=self.Subscriber(name, brewType, default)

	# def addListener(self, name, target):
	# 	self.events.register(name, target)

	def makeConfig(self):
		subs = map(lambda x:x.makeConfig(),self.subscribers.values())
		pubs = map(lambda x:x.makeConfig(),self.publishers.values())
		config = {'config':{
			'name':self.name,
			'description':self.description,
			'publish':{'messages':pubs},
			'subscribe':{'messages':subs},
			}}
		return config

	def on_open(self, ws):
 		print ( "[on_open] conection openned" , str(self.makeConfig()) )
		ws.send( json.write(self.makeConfig()) )
 		self.connected = True
 		print ( "[on_open] client configured with msg ", str(self.makeConfig()) )
		thread.start_new_thread(startConsole, ())

	def on_message(self,ws,message):
	 	print ( "[on_message] message received ", str(message) )
		full = json.read(message)
		msg = full["message"]
		if self.subscribers[msg['name']]:
	 		print ( "[on_message] passing message to client name ", str( msg['name'] ) )
			################################
			# add code here to add appropriate message to mailbox
			pass

	def on_error(self,ws,error):
 		print ( "[on_error] error encountered ", str( error ) )
		# self.on_close(ws)

	def on_close(self, ws):
 		print ( "[on_close] connection closing " )
		self.connected = False
 		# self.events.call("close")
		while self.started and not self.connected:
			time.sleep(5)
	 		print ( "[on_close] trying to re-establish connection " )
			self.run()

	def publish(self,name,value):
 		print ( "[publish] publishing message ", str(value))
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

 		print ( "[publish] publishing full message ", str(message))
		self.ws.send(json.write(message))

	def run(self):
		self.ws = websocket.WebSocketApp( "ws://{0}:{1}".format(self.server,self.port),
						on_message = lambda ws, msg: self.on_message(ws, msg),
						on_error = lambda ws, err: self.on_error(ws,err),
						on_close = lambda ws: self.on_close(ws), 
						on_open = lambda ws: self.on_open(ws)
						)
		self.ws.on_open = lambda ws: self.on_open(ws)
  		print ( "[run] running websocket " )
		self.ws.run_forever()

	def start(self):
		self.started = True
		self.run()

	def stop(self):
		self.started = False
		if self.ws is not None:
			self.ws.close()

def startSpacebrew():
	print ( "[startSpacebrew]")
	brew = Spacebrew(name=options.name, server=options.server)

	for sub in options.subs:
		brew.addSubscriber(sub["name"], sub["type"])

	for pub in options.pubs:
		brew.addPublisher(pub["name"], pub["type"])

	try:
		brew.start()

	finally:
		brew.stop()

def startConsole():
	print ( "[startConsole]")
	console = socket(AF_INET, SOCK_STREAM)

	try:
		print ( "[startConsole] 2")
		console.connect(('localhost', 6571))
		print ( "[startConsole] 3")
		console.setblocking(0)
		print "connected to socket" 
	except:
		print "not able to connect" 
	finally:
		print "not able to connect" 
		console.close()

	try:
		data = console.recv(1024)
		print "received data ", data 
	except:
		print "no data available" 


if __name__ == "__main__":
	print """
This is the Spacebrew module. 
See spacebrew_ex.py for usage examples.
"""

parseInput(sys.argv[1:])

startSpacebrew()
# thread.start_new_thread(startSpacebrew, ())

