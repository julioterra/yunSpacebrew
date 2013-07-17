# Spacebrew and Websocket for the Arduino Yun

The Spacebrew Yun library features two main components - a set of python scripts that run on the linino, and a library that runs on the atmel chip. Below is an overview of how to install both of these components so that you can connect to Spacebrew from an Arduino sketch.

@date:  July 16, 2013


## Installing Linino Scripts:
There are two python scripts that you need to copy into the python library folder on the arduino. These file are: `spacebrew.py` and `getProcPid.py`. Here is how you can do it:
  
1. Navigate to the `linino/spacebrew` folder in the yunSpacebrew directories  
2. Run following commands:  
  
```
scp ./spacebrew.py root@juliyun.local:/usr/lib/python2.7
scp ./getProcPid.py root@juliyun.local:/usr/lib/python2.7
```
  
Important: replace `juliyun.local` with the name or IP of your yun  

## Installing Arduino Library:
To install the Arduino Library just copy the folder titled spacebrewYun into the libraries folder in your Arduino sketch book. Then run the example sketch to try it out.
