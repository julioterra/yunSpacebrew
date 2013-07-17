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

	class MSG:
		NAME 			= chr(29)
		DATA			= chr(30)
		END 			= chr(31)

	class CONNECTION:
		START 			= chr(28)
		END 			= chr(27)
		ERROR 			= chr(26)

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
		def __init__(self, name, brewType):
			self.name = name
			self.type = brewType
			self.value = None

		def makeConfig(self):
			conf = { 'name':self.name, 'type':self.type }
			return conf
		
	class Publisher(Slot):
		pass

	class Subscriber(Slot):
		pass

	class Events(object):
		def __init__(self, events):
			self.callbacks = {}
			for event in events:
				self.callbacks[event] = []
		def register(self, event, target):
			assert type(self.callbacks[event]) is list
			self.callbacks[event].append(target)
		def call(self, event):
			assert type(self.callbacks[event]) is list
			for target in self.callbacks[event]:
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
		self._console = {}

	def console(self, _console = {}):
		self._console = _console

	def addPublisher(self, name, brewType="string", default=None):
		if not self.connected: self.publishers[name] = self.Publisher(name, brewType)
	
	def addSubscriber(self, name, brewType="string"):
		if not self.connected: self.subscribers[name] = self.Subscriber(name, brewType)

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

	def on_open( self, ws ):
		ws.send( json.write(self.makeConfig()) )
 		self.connected = True
 		if self._console: 
 			self._console.log( SERIAL.CONNECTION.START )

	def on_message( self, ws, message ):
		full = json.read( message )
		msg = full["message"]
		if self.subscribers[msg['name']]:
	 		if self._console: self._console.publish(str(msg['name']), str(msg['value']))

	def on_error(self,ws,error):
 		if options.debug: print ( "[on_error] error encountered ", str( error ) )
 		if self._console: 
 			error_msg = SERIAL.CONNECTION.ERROR + str(error) + SERIAL.MSG.END
	 		self._console.log( error_msg )

	def on_close(self, ws):
		if self.connected:
			self.connected = False
	 		if self._console: 
		 		self._console.log( SERIAL.CONNECTION.END )

		while self.started and not self.connected:
			time.sleep(5)
			self.run()

	def publish(self,name,value):
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

		if options.debug: self._console.log("on: '" + name + "' published msg: " + str(message) + "\n")

		self.ws.send(json.write(message))

	def start(self):
		pass
		self.ws = websocket.WebSocketApp( "ws://{0}:{1}".format(self.server,self.port),
						on_message = lambda ws, msg: self.on_message(ws, msg),
						on_error = lambda ws, err: self.on_error(ws,err),
						on_close = lambda ws: self.on_close(ws), 
						on_open = lambda ws: self.on_open(ws)
						)
		self.ws.on_open = lambda ws: self.on_open(ws)
		self.ws.run_forever()

	def run(self):
		try:
			self.start()
			self.started = True
		finally:
			self.stop()
			self.started = False

	def stop(self):
		self.started = False
		if self.ws is not None:
			self.ws.close()

# def runSpacebrew():
# 	try:
# 		brew.start()
# 	finally:
# 		brew.stop()


class Console(object):
	pass

	def __init__(self, brew):
		self.console = socket(AF_INET, SOCK_STREAM)
		self.connected = False
		self.msg_buffer = ""
		self.brew = brew

	def start(self):
		try:
			self.console = socket(AF_INET, SOCK_STREAM)
			self.console.connect(('localhost', 6571))
			self.connected = True
			self.console.send("Spacebrew.py script running\n")
			thread.start_new_thread(self.brew.run, ())

		except:
			self.connected = False

	def read(self):
		if not self.connected: return

		index_end = -1

		new_data = self.console.recv(1024)

	    # if new data was received then add it buffer and check if end message was provided
		if new_data:
			self.msg_buffer += new_data
			index_end = self.msg_buffer.find(SERIAL.MSG.END)

		if new_data == '':
			console_running = False
			self.console.close()
			return None

		# if message end was found, then look for the start and div marker
		if index_end > 0:
			index_name = self.msg_buffer.find(SERIAL.MSG.NAME)
			index_msg = self.msg_buffer.find(SERIAL.MSG.DATA)

			publish_route = "" 
			msg = ""

			if index_name >= 0 and index_msg > index_name:

				publish_route = self.msg_buffer[(index_name + 1):index_msg]
				msg = self.msg_buffer[(index_msg + 1):index_end]

				try:
					self.brew.publish(publish_route, msg)
				except Exception:
					error_msg = "issue sending message via spacebrew, route: " + publish_route
					error_msg += ", message: " + msg + "\n"
					self.log(error_msg)

			self.msg_buffer = ""

	def run(self):
		self.start()
		try:
			while True:
				if self.connected: 
					self.read()
		finally:
			self.console.close()

	def publish(self, name, message):
		try:
			full_msg = SERIAL.MSG.NAME + name + SERIAL.MSG.DATA + message + SERIAL.MSG.END
			self.console.send(full_msg)
		except:
			pass

	def log(self, message):
		self.console.send(message)


if __name__ == "__main__":
# 	if options.debug: print """
# This is the Spacebrew module. 
# See spacebrew_ex.py for usage examples.
# """

	parseInput(sys.argv[1:])

	global brew, data, console, console_running

	brew = {}
	console = {}

	if options.debug: print ( "[runSpacebrew]")

	brew = Spacebrew( 	name=options.name, 
						server=options.server, 
						description=options.description,
						port=options.port)

	for sub in options.subs:
		brew.addSubscriber(sub["name"], sub["type"])
	for pub in options.pubs:
		brew.addPublisher(pub["name"], pub["type"])

	data = ""

	console = Console(brew)

	brew.console(console)

	# thread.start_new_thread(runSpacebrew, ())

	console.run()
