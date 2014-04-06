## Dev Notes

Create a handshake protocol between the Spacebrew sketch on the atmel chip and linino. Log all errors to a text file so that they can be used for debugging.

* On the Arduino side a confirmation message needs to be sent to the linino every time it is done reading an parsing a message. 
* On the linino side they need to wait until the Arduino is ready before sending a message. 
  * While on "hold" the linino needs to save messages in a queue. 
  * This queue needs to hold the latest message for each subscriber, and make sure to hold only one message per subscriber. 
  * These messages need to be prioritized based on whichever order of receipt.



