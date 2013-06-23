### Spacebrew and Websocket on the Yun
  
## Installing Websockets:
To install the websockets library just copy the websocket folder to the /usr/lib/python2.7 directory on the arduino yun.  
  
1. Navigate to the folder that contains the websocket directory in Terminal  
2. Run following command:  
  
```
scp -r ./websocket root@juliyun.local:/usr/lib/python2.7
```
  
Replace `juliyun.local` with the name or IP of your yun  
  
## Installing Spacebrew:
In order for spacebrew to be able to run on a yun, you first need to make the json.py script from the bridge library available to other libraries. This is accomplished by adding a __init__.py file to that directory. Once that is done, just copy the spacebrew.py file to the /usr/lib/python2.7 directory on the yun.  
  
1. Navigate to the folder that contains the spacebrew.py file in Terminal  
2. Run following commands the copy the bridge __init__ file and spacebrew library:  
```
scp -r ./bridge/__init__.py root@juliyun.local:/usr/lib/python2.7/bridge
scp -r ./spacebrew.py root@juliyun.local:/usr/lib/python2.7
```
  
Replace `juliyun.local` with the name or IP of your yun  

## Running Spacebrew Test Scripts:
To run the test scripts via ssh, just copy the test script files to the /tmp/ directory on the yun, and then run the scripts using python.
  
1. Navigate to the folder that contains the test files in Terminal  
2. Execute following commands to copy both scripts to the Yun:  
```
scp -r ./boolean_client.py root@juliyun.local:/tmp
scp -r ./range_client.py root@juliyun.local:/tmp
```
  
3. SSH into your YUN by running the command below, and entering your password when prompted:  
```
ssh root@juliyun.local
```

4. Run the boolean and range test scripts   
  
```
python boolean_client.py
```  
or  
  
```
python range_client.py
```  

## Next Steps: 
* Create a version of the spacebrew library that can be executed and configured via the command line.  
* Enable communication with the Arduino sketches using the bridge key/value store.  
