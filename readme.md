# Spacebrew for the Arduino Yun

The Spacebrew Yun library features two main components - a set of python scripts that run on the linino, and a library that runs on the atmel chip. Below is an overview of how to install both of these components so that you can connect to Spacebrew from an Arduino sketch.

@date:  July 16, 2013


## Installing Linino Python and Shell Scripts:
There are two python scripts that you need to copy into the python library folder on the arduino. These file are `spacebrew.py` and `getprocpid.py`, and they both reside in the spacebrew folder on the linino directory of this project. Here is how to copy them over: 
  
1. Navigate to the `linino` folder in the yunSpacebrew directories  
2. Run following commands:  
  
```
scp -r ./spacebrew root@juliyun.local:/usr/lib/python2.7
```

There are two shell scripts that you need to copy into the user bin folder on the arduino. These files are `run-spacebrew` and `run-getsbproc`. They both reside in the shell folder on the linino directory of this project. Here is how to copy them over and then configure them to be executable files:

1. Navigate to the `linino/shell` folder in the yunSpacebrew directories  
2. Copy files over to linino with `scp` commands:  
  
```
scp ./run-spacebrew root@juliyun.local:/usr/bin
scp ./run-getsbproc root@juliyun.local:/usr/bin
```

3. SSH into the linino using the following command, input the password when prompted:

```
ssh root@juliyun.local
```

4. Make the files executable by running `chmod` commands:
  
```
chmod 0755 /usr/bin/run-spacebrew
chmod 0755 /usr/bin/run-getsbproc
```
  
**Important**: replace `juliyun.local` with the name or IP of your yun  

## Installing Arduino Library:
To install the Arduino Library just copy the folder titled spacebrewYun into the libraries folder in your Arduino sketch book. Then run the example sketch to try it out.

## Trying it Out with the Sample Sketch:
Here is how you can test out the library with the sample sketch:  
* Upload the sample sketch to your internet connected Arduino Yun  
* Open the serial monitor to see the status of the app (this is required) 
* Navigate to the spacebrew admin website on your browser: http://spacebrew.github.io/spacebrew/admin  
* Confirm that an app called `aYun` has appeared on the list of live apps   
* Open the javascript examples to connect to your app:  
  * Range example: http://julioterra.github.io/spacebrew-slider-with-admin/index.html?name=yunRange  
  * Boolean example: http://julioterra.github.io/spacebrew-button-with-admin/index.html?name=yunButton  
  * String example: http://julioterra.github.io/spacebrew-string-send-with-admin/index.html?name=yunString  
* Connect the publishers from `aYun` to the subscriber of the javascript clients, and vice versa.   
* Interact with the javascript apps while checking the serial monitor to confirm that data is being received.   
* Confirm that the data is being sent from the yun by looking at the javascript apps.  
  
## Understanding the Example Sketch:
Here is how the example sketch works. At the top of the sketch we create an instance of the SpacebrewYun class using the constructor. The constructor accepts two values: a `name` and a `description`.  
   
```
SpacebrewYun sb = SpacebrewYun("aYun", "Arduino Yun spacebrew test");
```
  
In the setup function we configure our Spacebrew client as follows.    
  
First, we call the `verbose()` method with the argument `true` to tell the `sb` object to print status messages to serial. If we didn't call this method, or if we called it and passed it a `false` argument instead, then the `sb` object would not print status messages.  
  
```
sb.verbose(true);
``` 
  
Next, we register the subscribers and publishers for our app using the `addSubscribe` and `addPublish` methods. These are the incoming and outgoing data channels that will enable us to send and receive data from Spacebrew. Each publisher and subscriber needs to have a unique name, and a data type.

```
sb.addPublish("string test", "string");
sb.addPublish("range test", "range");
sb.addPublish("boolean test", "boolean");
sb.addPublish("custom test", "crazy");  
sb.addSubscribe("string test", "string");
sb.addSubscribe("range test", "range");
sb.addSubscribe("boolean test", "boolean");
sb.addSubscribe("custom test", "crazy");
```
  
Then, we register the callback method that will handle different types of data. Spacebrew supports three different standard data types - `range`, `string`, and `boolean`. If you created a subscriber with any other data type, those messages will be routed to the callback function registered with `onCustomMessage` method.  
  
```
sb.onRangeMessage(handleRange);
sb.onStringMessage(handleString);
sb.onBooleanMessage(handleBoolean);
sb.onCustomMessage(handleCustom);
```
  
The handler functions that are registered in the setup are defined at the end of the example sketch. When creating your own sketch make sure that your functions support the appropriate types and numbers of arguments.    
Once the `sb` object has been configured we are ready to connect to the Spacebrew server. To do so we call the `sb.connect()` method and pass it the server ip address or hostname, and optionally, the port number. 

```
sb.connect("sandbox.spacebrew.cc"); 
```

Once connected to Spacebrew, we send messages to all publishers using the `sb.send()` method. This method accepts two arguments, the first argument is the `name` and the second argument is the `value`.   
  
```
sb.send("string test", test_str_msg);
sb.send("range test", 500);
sb.send("boolean test", true);
sb.send("custom test", "youre loco");
```
  
It automatically publishes information on the outgoing routes every 2 seconds. Data received via the subscriber routes is printed to the serial monitor. is set-up to connect your yun directly to the cloud instance of Spacebrew. Here is how to test out the library with the example.   
  
# Websocket for the Arduino Yun
  
The Websockets for Arduino script is also included in this repo. That said, this script is already included in the Arduino Yun distribution.
