#!/usr/bin/python

import time
import sys
from spacebrew import Spacebrew
import thread
import os

# get app name and server from query string
name = "Arduino Yun Range"
server = "sandbox.spacebrew.cc"
state = 0

for cur_ele in sys.argv:
	if "name" in cur_ele: 
		name = cur_ele[5:]
	if "server" in cur_ele: 
		server = cur_ele[7:]


# configure the spacebrew client
brew = Spacebrew(name=name, server=server)
brew.addPublisher("local state", "range")
brew.addSubscriber("remote state", "range")

def handleRange(value):
	print("got message " + (str(value) + "  "))

brew.subscribe("remote state", handleRange)

def requestInput():
	global state
	a = raw_input("press key to send msg \n" )
	state = (state + 10) % 1024
	brew.publish('local state', state)
	print("sent msg " + str(state))
	requestInput()

def startThread():
	print("starting new thread")
	thread.start_new_thread(requestInput, ())

brew.addListener("open", startThread)

if __name__ == "__main__":
	try:
		# start-up spacebrew

		# create and load info message at the top of the terminal window
		info_msg = "\nThis is the pySpacebrew library range send example. It sends out a random range\n" 
		info_msg += "message every time the enter or return key is pressed.\n"  
		info_msg += "Connected to Spacebrew as: " + name + "\n"
		print(info_msg)

		# request_input()

		brew.start()


	# closing out the app and returning terminal to old settings
	finally:
		brew.stop()
