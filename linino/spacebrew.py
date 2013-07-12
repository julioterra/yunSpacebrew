#!/usr/bin/python

from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, gethostname
from select import select
from websocket import websocket #, ABNF
import json
import time
import optparse
from optparse import Option
import sys
import thread

class SERIAL:

	class PUB:
		NAME 			= chr(29)
		MSG				= chr(30)
		END 			= chr(31)

	class ERROR:
		CODE			= chr(30)
		MSG				= chr(30)
		END 			= chr(31)
		PUBLISH_INVALID = (301, 'not able to publish message to spacebrew\n')



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

	ACTIONS = Option.ACTIONS + ("pubsub", "strspaces")
	STORE_ACTIONS = Option.STORE_ACTIONS + ("pubsub", "strspaces")
	TYPED_ACTIONS = Option.TYPED_ACTIONS + ("pubsub", "strspaces")
	ALWAYS_TYPED_ACTIONS = Option.ALWAYS_TYPED_ACTIONS + ("pubsub", "strspaces")

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

		elif action == "strspaces":

			# read the subscriber and publisher arguments
			for arg in parser.rargs:
				if arg[:2] == "--" and len( arg ) > 2: break
				if arg[:1] == "-" and len( arg ) > 1: break
				value += " " + arg

			setattr(values, dest, value )

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
    parser.add_option(OPT.NAME, dest='name', metavar = 'name', action='strspaces', default='Arduino Yun', help='app name [default: %default]')
    parser.add_option(OPT.DESCRIPTION, dest='description', metavar = 'description', action='strspaces', default='', help='brief description of app')
    parser.add_option('-g', dest='debug', metavar = 'debug', default=False, help='debug value')

    (options, unusedArgs) = parser.parse_args(args)

    if options.debug: print ("options ", str(options))

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
				# if options.debug: print("creating method array for " + event)
				self.callbacks[event] = []
		def register(self, event, target):
			# if options.debug: print("adding method to " + event)
			assert type(self.callbacks[event]) is list
			# if options.debug: print("added method to " + event)
			self.callbacks[event].append(target)
		def call(self, event):
			# if options.debug: print("calling method for " + event)
			assert type(self.callbacks[event]) is list
			for target in self.callbacks[event]:
				# if options.debug: print("found method for " + event)
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
 		if options.debug: print ( "[addPublisher] adding a new publisher ", name, " and type ", brewType )
		if self.connected:
			raise ConfigurationError(self,"Can not add a new publisher to a running Spacebrew instance (yet).")
		else:
			self.publishers[name]=self.Publisher(name, brewType, default)
	
	def addSubscriber(self, name, brewType="string", default=None):
 		if options.debug: print ( "[addSubscriber] adding a new subscriber ", name, " and type ", brewType )
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
 		if options.debug: print ( "[on_open] conection openned" , str(self.makeConfig()) )
		ws.send( json.write(self.makeConfig()) )
 		self.connected = True
 		if options.debug: print ( "[on_open] client configured with msg ", str(self.makeConfig()) )
		# thread.start_new_thread(startConsole, ())

	def on_message(self,ws,message):
	 	if options.debug: print ( "[on_message] message received ", str(message) )
		full = json.read(message)
		msg = full["message"]
		if self.subscribers[msg['name']]:
	 		if options.debug: print ( "[on_message] passing message to client name ", str( msg['name'] ) )
	 		printConsole("from " + str(msg['name']).encode('ascii', 'ignore') + " received " + (msg['value']).encode('ascii', 'ignore') + '\n')
	 		# toSubscriber(str(msg['name']), str(msg['value']))

	def on_error(self,ws,error):
 		if options.debug: print ( "[on_error] error encountered ", str( error ) )
		# self.on_close(ws)

	def on_close(self, ws):
 		if options.debug: print ( "[on_close] connection closing " )
		self.connected = False
 		# self.events.call("close")
		while self.started and not self.connected:
			time.sleep(5)
	 		if options.debug: print ( "[on_close] trying to re-establish connection " )
			self.run()

	def publish(self,name,value):
		printConsole("publish 1 " + str(name) + " + " + str(value) + "\n")
 		if options.debug: print ( "[publish] publishing message ", str(value))
		publisher = self.publishers[name]

		if publisher.type == "boolean":
			if value == True or value == 1 or value == "1": 
				value = "true"
			else:
				value = "false"

		message = {'message': {
			'clientName':self.name,
			'name':publisher.name,
			'type':publisher.type,
			'value':value } }

		printConsole("publish 2 " + str(message) + "\n")

 		if options.debug: print ( "[publish] publishing full message ", str(message))
		self.ws.send(json.write(message))

	def run(self):
		pass
		self.ws = websocket.WebSocketApp( "ws://{0}:{1}".format(self.server,self.port),
						on_message = lambda ws, msg: self.on_message(ws, msg),
						on_error = lambda ws, err: self.on_error(ws,err),
						on_close = lambda ws: self.on_close(ws), 
						on_open = lambda ws: self.on_open(ws)
						)
		self.ws.on_open = lambda ws: self.on_open(ws)
  		if options.debug: print ( "[run] running websocket " )
		self.ws.run_forever()

	def start(self):
		self.started = True
		self.run()

	def stop(self):
		self.started = False
		if self.ws is not None:
			self.ws.close()

def runSpacebrew():
	if options.debug: print ( "[runSpacebrew]")
	global brew

	brew = Spacebrew( 	name=options.name, 
						server=options.server, 
						description=options.description,
						port=options.port)

	for sub in options.subs:
		brew.addSubscriber(sub["name"], sub["type"])
	for pub in options.pubs:
		brew.addPublisher(pub["name"], pub["type"])

	try:
		brew.start()
	finally:
		brew.stop()

class Console(object):
	pass

	def __init__(self, brew):
		self.brew = brew
		pass

		# 02 - start message
		# 03 - end message

def startConsole():
	global console, console_running

	try:
		console = socket(AF_INET, SOCK_STREAM)
		console.connect(('localhost', 6571))
		console_running = True
		if options.debug: print "[startConsole] able to connect" 
		console.send("\n\nconnected to spacebrew.py\n\n")
	except:
		console_running = False
		if options.debug: print "[startConsole] not able to connect" 


def readConsole():
	global console, data

	index_end = -1

	new_data = console.recv(1024)

    # if new data was received then add it buffer and check if end message was provided
	if new_data:
		data += new_data
		index_end = data.find(SERIAL.PUB.END)

	if new_data == '':
		if options.debug: print "[runConsole] closing connection to console"
		console_running = False
		console.close()
		return None

	# if message end was found, then look for the start and div marker
	if index_end > 0:
		# printConsole("full message: " + data + "\n")

		index_name = data.find(SERIAL.PUB.NAME)
		index_msg = data.find(SERIAL.PUB.MSG)

		printConsole("indices - end: " + str(index_end) + ", name: " + str(index_name) + ", msg: " + str(index_name) + "\n")

		if options.debug: print data

		publish_route = "" 
		msg = ""

		if index_name >= 0 and index_msg > 0:

			try:
				# send the message to spacebrew
				publish_route = data[(index_name + 1):index_msg]
			except Exception:
				error_msg = "issue extracting publisher name - start index: " + (index_name + 1)
				error_msg += ", end index: " + index_msg
				printConsole(error_msg)

			try:
				# send the message to spacebrew
				msg = data[(index_msg + 1):index_end]
			except Exception:
				error_msg = "issue extracting msg - start index: " + (index_msg + 1)
				error_msg += ", end index: " + index_end
				printConsole(error_msg)

			try:
				if publish_route != "" and msg != "":
					brew.publish(publish_route, msg)
			except Exception:
				error_msg = "issue sending message via spacebrew, route: " + publish_route
				error_msg += ", message: " + msg
				printConsole(error_msg)
				# error_msg = SERIAL.ERROR.CODE + str(SERIAL.ERROR.PUBLISH_INVALID[0]) + ", "
				# error_msg += SERIAL.ERROR.MSG + SERIAL.ERROR.PUBLISH_INVALID[1] 
				# error_msg += " - " + str(Exception) + "\n" + SERIAL.ERROR.END
				# printConsole(error_msg)

		data = ""
        
def runConsole():
	startConsole()
	try:
		while True:
			if console_running:
				readConsole()
	finally:
		console.close()

def toSubscriber(name, message):
	try:
		full_msg = SERIAL.PUB.NAME + name + SERIAL.PUB.MSG + message + SERIAL.PUB.END
		console.send(full_msg)
	except:
		pass

def printConsole(message):
	console.send(message)

if __name__ == "__main__":
# 	if options.debug: print """
# This is the Spacebrew module. 
# See spacebrew_ex.py for usage examples.
# """
	global brew, data, console, console_running

	data = ""

	parseInput(sys.argv[1:])

	thread.start_new_thread(runSpacebrew, ())

	runConsole()
