#include <Bridge.h>
#include <Console.h>
#include <Process.h>

/**
 *	Arduino Yun Example
 *
 *	This example code is in the public domain.
 *	
 * 	@date 		July 3, 2013
 *  @author		Julio Terra
 *   
 */
 

Process brew;
String name;
String server;
int port;
String description;
String subscribers;
String publishers;

Process pids;
int const pidLength = 6;
char pid [6] = {'\0','\0','\0','\0','\0','\0'};
int const sbPidsLen = 4;
int sbPids [4] = {-1, -1, -1, -1};


void setup() { 
    delay(1000);

    Serial.begin(57600);
	while (!Serial) { 	Serial.println("connecting"); }
	Serial.println("App Started"); 

  	//Initialize Console and wait for port to open:
	Bridge.begin();
	Serial.println("Bridge Started"); 

	constructorSB();
	connectSB(); 
   
//	Console.buffer(64);
//	Serial.println("Console Started"); 
} 

void constructorSB() {
	name = "Arduino Yun Revised";
	server = "sandbox.spacebrew.cc";
	port = 9000;
	description = "no description";
	subscribers = "";
	publishers = "";
}

//void addPublish(String name, String type) {
//	publishers += name + "," + type + ";";
//}
//
//void addSubscribe(String name, String type) {
//	subscribers += name + "," + type + ";";
//}

// 

void getSbPid() {

	// request the pid of all python processes
	pids.begin("python");
	pids.addParameter("/usr/lib/python2.7/getSbPid.py"); // Process should launch the "curl" command
	pids.run();

	Serial.println("getSbPid - process running");

	int sbPidsIndex = 0;
    int pidCharIndex = 0;
    char c = '\0';

	while ( pids.available() > 0 ) {

	    c = pids.read();

		if ( c >= '0' && c <= '9' ) {
			pid[pidCharIndex] = c;
			pidCharIndex = (pidCharIndex + 1) % pidLength;
		} 

		else if ( (c == ' ' || c == '\n') && pidCharIndex > 0) {
			sbPids[sbPidsIndex] = atoi(pid);
			if ( sbPidsIndex < (sbPidsLen - 1) ) sbPidsIndex = (sbPidsIndex + 1);    		

			for( int i = 0; i < pidLength; i++ ){ 
				pid[i] = '\0';
				pidCharIndex = 0;
			}
		}
	}

	// print out the pid of all python processes
	Serial.println("\nSB pids recap: ");
	for (int i = 0; i < sbPidsIndex; i++) {
		Serial.print(i);
		Serial.print(" : ");
		Serial.println(sbPids[i]);                
	}
}

void killBrewPids() {
	getSbPid();
	delay(400);

	for (int i = 0; i < sbPidsLen; i ++) {
		if (sbPids[i] > 0) {
			char * newPID = itoa(sbPids[i], pid, 10);
			Serial.print("deleting pid: ");
			Serial.println(newPID);

			Process p;
			p.begin("kill");
			p.addParameter("-9");
			p.addParameter(newPID);		// Process should launch the "curl" command
			p.run();            		// Run the process and wait for its termination	

			delay(400);						
		}
	}
}

void connectSB() {

	killBrewPids();

 	brew.begin("python"); // Process should launch the "curl" command
	brew.addParameter("/usr/lib/python2.7/spacebrew.py"); // Process should launch the "curl" command
	brew.addParameter("--server");
	brew.addParameter(server);
	brew.addParameter("--port");
	brew.addParameter(String(port));
	brew.addParameter("-n");
	brew.addParameter(name);
	brew.addParameter("-d");
	brew.addParameter(description);
	brew.addParameter("-p"); // Add the URL parameter to "curl"
	brew.addParameter("tested, range"); // Add the URL parameter to "curl"
	brew.addParameter("-s"); // Add the URL parameter to "curl"
	brew.addParameter("test, range"); // Add the URL parameter to "curl"

    Serial.println("connectSB - command ready");

	Console.begin();
	delay(500);

	brew.run();                   // Run the process and wait for its termination	

    Serial.println("connectSB - check console");
	while (!Console) { ; }        
}


void loop() { 
} 
