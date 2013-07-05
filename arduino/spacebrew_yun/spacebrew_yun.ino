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
 

Process pids;
Process brew;

String name;
String server;
int port;
String description;
String subscribers;
String publishers;

boolean kill = true;

int pidLength = 6;
char pid [6] = {'\0','\0','\0','\0','\0','\0'};
int bridgePID = 0;
int const otherPidsLen = 8;
int otherPIDs [8] = {-1, -1, -1, -1, -1, -1, -1, -1};
int sbPID = 0;
int cur_pid_index = 0;


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

	// readSbPids();

    int cur_char_loc = 0;
    char c = '\0';

	while ( pids.available() > 0 ) {

	    c = pids.read();
	    // Serial.print("readSbPids - read char "); Serial.println(c);

		if ( c >= '0' && c <= '9' ) {
			pid[cur_char_loc] = c;
			cur_char_loc = (cur_char_loc + 1) % pidLength;
			// Serial.println(pid);
		} 

		else if ( (c == ' ' || c == '\n') && cur_char_loc > 0) {
			otherPIDs[cur_pid_index] = atoi(pid);
		    // Serial.print("readSbPids - pid "); Serial.println(pid);
		    // Serial.print("readSbPids - loading number "); Serial.println(otherPIDs[cur_pid_index]);
			if ( cur_pid_index < (otherPidsLen - 1) ) cur_pid_index = (cur_pid_index + 1);    		

			for( int i = 0; i < pidLength; i++ ){ 
				pid[i] = '\0';
				cur_char_loc = 0;
			}
			// return true;
		}
		else if (c == 'N') {
			// return false;
		}
	}

	// print out the pid of all python processes
	Serial.println("\nSB pids recap: ");
	for (int i = 0; i < cur_pid_index; i++) {
		Serial.print(i);
		Serial.print(" : ");
		Serial.println(otherPIDs[i]);                
	}
}

void connectSB() {

	getSbPid();
	delay(500);

	for (int i = 0; i < cur_pid_index; i ++) {
		char * newPID = itoa(otherPIDs[i], pid, 10);
		Serial.print("deleting pid: ");
		Serial.println(newPID);

		Process p;
		p.begin("kill");
		p.addParameter(newPID);		// Process should launch the "curl" command
		p.run();            		// Run the process and wait for its termination	

		delay(400);			
	}

 	brew.begin("python"); // Process should launch the "curl" command
	brew.addParameter("/usr/lib/python2.7/spacebrew.py"); // Process should launch the "curl" command
	brew.addParameter("--server");
	brew.addParameter(server);
	brew.addParameter("--port");
	brew.addParameter("9000");
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
	delay(1000);

	brew.run();                   // Run the process and wait for its termination	
	Console.begin();

    Serial.println("connectSB - check console");
	while (!Console) { ; }        
}


void loop() { 
} 

//void getBridgePID() {
//    	Process p;
//    	p.begin("pidof");
//    	p.addParameter("python"); // Process should launch the "curl" command
//        p.run();
//        int cur_loc = 0;
//        while(p.available()>0) {
//          char c = p.read();
//          if (cur_loc < pidLength) {
//            pid[cur_loc] = c;
//            cur_loc++;
//          }
//        }
//        bridgePID = atoi(pid);
//        Serial.println(bridgePID);
//
//
//        Serial.print("convert back to string: ");
//        char test [pidLength];
//        itoa(bridgePID, test, 10);
//        Serial.print(test);
//
//}

// void getAllNonBridgePIDs() {
//     	Process p;
//     	pids.begin("pidof");
//     	pids.addParameter("python"); // Process should launch the "curl" command
//         pids.run();
//         int cur_char_loc = 0;
//         int cur_pid_index = 0;
//         while(p.available()>0) {
//           char c = p.read();
//           pid[cur_char_loc] = c;
//           cur_char_loc += 1 % pidLength;
//           if (cur_char_loc == 0) {
//             int newPID = atoi(pid);
//             if (newPID != bridgePID) {
//               otherPIDs[cur_pid_index] = newPID;
//               cur_pid_index++;
//               if (cur_pid_index >= pidLength) break;
//             }            
//           }
//         }


//         Serial.print(cur_pid_index);
//         Serial.println(" Non-Bridge Python Processes");
//         for (int i = 0; i < cur_pid_index; i++) {
//           Serial.print(i);
//           Serial.print(" : ");
//           Serial.print(otherPIDs[i]);                
//         }

// }
// 
// void getAllPIDs(boolean getSB) {

// 	// request the pid of all python processes
// 	pids.begin("pidof");
// 	pids.addParameter("python"); // Process should launch the "curl" command
//     pids.run();

//     Serial.println("getAllPIDs - process running");

//     int cur_pid_index = 0;
//     while( pids.available() > 0 ) {
//     	otherPIDs[cur_pid_index] = getNextNumber();
// 		if ( getSB && (cur_pid_index == 0) ) {
// 			sbPID = otherPIDs[cur_pid_index];
// 			Serial.print("SB bid "); Serial.println(otherPIDs[cur_pid_index]); 
// 		} else {
// 			Serial.print("other pid "); Serial.println(otherPIDs[cur_pid_index]); 
// 		}
// 		if ( cur_pid_index < (otherPidsLen - 1) ) cur_pid_index = (cur_pid_index + 1);
//     }

// 	// print out the pid of all python processes
//     Serial.println("\nNon-Bridge Python Processes: ");
//     for (int i = 0; i < cur_pid_index; i++) {
//           Serial.print(i);
//           Serial.print(" : ");
//           Serial.println(otherPIDs[i]);                
//     }
// }

// int getNextNumber() {
//     int cur_char_loc = 0;
//     char c = '\0';
// 	while ( (pids.available() > 0) && !(c == ' ' || c == '\n') ) {
// 	    char c = pids.read();
// 		if ( c >= '0' && c <= '9' ) {
// 			pid[cur_char_loc] = c;
// 			cur_char_loc = (cur_char_loc + 1) % pidLength;
// 		} 
// 		else if (c == ' ' || c == '\n') {
// 			break;
// 		}
// 		else if (c == 'N') {
// 			return -1;
// 		}
// 	}
// 	int return_value = atoi(pid);
// 	for( int i = 0; i < pidLength; i++ ) pid[i] = '\0';
// 	return return_value;
// }

// boolean readSbPids() {
//     int cur_char_loc = 0;
//     char c = '\0';

// 	while ( pids.available() > 0 ) {

// 	    c = pids.read();
// 	    // Serial.print("readSbPids - read char "); Serial.println(c);

// 		if ( c >= '0' && c <= '9' ) {
// 			pid[cur_char_loc] = c;
// 			cur_char_loc = (cur_char_loc + 1) % pidLength;
// 			// Serial.println(pid);
// 		} 

// 		else if ( (c == ' ' || c == '\n') && cur_char_loc > 0) {
// 			otherPIDs[cur_pid_index] = atoi(pid);
// 		    // Serial.print("readSbPids - pid "); Serial.println(pid);
// 		    // Serial.print("readSbPids - loading number "); Serial.println(otherPIDs[cur_pid_index]);
// 			if ( cur_pid_index < (otherPidsLen - 1) ) cur_pid_index = (cur_pid_index + 1);    		

// 			for( int i = 0; i < pidLength; i++ ){ 
// 				pid[i] = '\0';
// 				cur_char_loc = 0;
// 			}
// 			// return true;
// 		}
// 		else if (c == 'N') {
// 			// return false;
// 		}
// 	}
// }
