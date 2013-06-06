#!/usr/bin/python

import time
import sys
from pySpacebrew.spacebrew import Spacebrew


# get app name and server from query string
name = "Arduino Yun"
server = "sandbox.spacebrew.cc"
state = False

for cur_ele in sys.argv:
	if "name" in cur_ele: 
		name = cur_ele[5:]
	if "server" in cur_ele: 
		server = cur_ele[7:]


# configure the spacebrew client
brew = Spacebrew(name=name, server=server)
brew.addPublisher("local state", "boolean")
brew.addSubscriber("remote state", "boolean")

def handleBoolean(value):
	global code
	print("got message " + (str(value) + "  "))
	request_input()

brew.subscribe("remote state", handleBoolean)

def request_input():
	global state
	a = raw_input( "send message?" )
	state = not state
	brew.publish('local state', state)
	print("sent response " + str(state))
	request_input()

if __name__ == "__main__":
	try:
		# start-up spacebrew
		brew.start()

		# create and load info message at the top of the terminal window
		info_msg = "This is the pySpacebrew library boolean example. It sends out a boolean message every time\n" 
		info_msg += "the enter or return key is pressed and displays the latest boolean value it has received.\n"  
		info_msg += "Connected to Spacebrew as: " + name + "\n"
		info_msg += "IMPORTANT: don't shrink the Terminal window as it may cause app to crash (bug with curses lib)."  
		print(info_msg)

		request_input()

		# line = sys.stdin.readline()

		# while line:
		# 	print line,
		# 	line = sys.stdin.readline()

		# listen for keypresses and handle input
		# while 1:

			# if (c == 10 or c == 13): 
			# 	# local_state = not local_state
			# 	brew.publish('local state', local_state)
				# stdscr.addstr(pos_local, pos_state, (str(local_state) + "  ").encode(code))

			# stdscr.refresh()

	# closing out the app and returning terminal to old settings
	finally:
		brew.stop()
