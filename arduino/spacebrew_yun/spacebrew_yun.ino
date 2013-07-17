#include <Bridge.h>
#include "SpacebrewYun.h"

/**
 *	Arduino Yun Example
 *
 *	This example code is in the public domain.
 *	
 * 	@date 		July 3, 2013
 *  @author		Julio Terra
 *   
 */

/**
 * APP VARIABLES
 */
int counter = 0;
long last = 0;
int interval = 2000;

SpacebrewYun sb = SpacebrewYun("aYun", "Arduino Yun spacebrew test");

void setup() { 
    delay(1000);

    Serial.begin(57600);
	while (!Serial) { 	Serial.println("connecting"); }
	Serial.println("App Started"); 

  	//Initialize Console and wait for port to open:
	Bridge.begin();
	Serial.println("Bridge Started"); 

	sb.addPublish("string test", "string");
	sb.addPublish("range test", "range");
	sb.addPublish("boolean test", "boolean");
	sb.addSubscribe("string test", "string");
	sb.addSubscribe("range test", "range");
	sb.addSubscribe("boolean test", "boolean");
	sb.onRangeMessage(onRangeMessage);

	sb.connect("sandbox.spacebrew.cc"); 
   } 


void loop() { 
	sb.monitor();
	if ( sb.connected() ) {
		if ( (millis() - last) > interval ) {
			String test_str = "string test";
			String test_ran = "range test";
			String test_bool = "boolean test";
			String test_msg = "testing, testing, ";
			test_msg += counter;
			counter ++;

			boolean test_flag = true;
			sb.send(test_str, test_msg);
			sb.send(test_ran, 500);
			sb.send(test_bool, true);

			last = millis();

		}
	}
} 

void onRangeMessage (String route, int value) {
 Serial.print("received msg ");
 Serial.print(route);
 Serial.print(" value ");
 Serial.println(value);
 
}

