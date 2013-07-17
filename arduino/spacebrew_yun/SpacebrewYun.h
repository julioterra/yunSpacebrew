
#ifndef YUNSPACEBREW_H
#define YUNSPACEBREW_H

#include "Arduino.h"
#include <Bridge.h>
#include <Console.h>
#include <Process.h>

enum SBmsg { MSG_CONNECTED = char(28), MSG_START = char(29), MSG_DIV = char(30), MSG_END = char(31) };

struct Publisher {
	char *name;
	char *type;
	char *defaultValue;
	Publisher * next;
};

struct Subscriber{
	char *name;
	char *type;
	Subscriber * next;
};

int const pidLength = 6;
int const sbPidsLen = 4;


class SpacebrewYun {

	public:
	    SpacebrewYun(const String&, const String&);
	    void addPublish(const String&, const String&);
	    void addSubscribe(const String&, const String&);

	    void connect(String, int);

		void connect() {
			connect(server, port);
		}

		void connect(String _server) {
			connect(String(_server), port);
		}

	    void monitor();
	    void onMessage();
	    boolean connected();

	    boolean send(const String&, const String&);

		boolean send(const String & name, bool value){
			return send(name, (value ? "true" : "false"));
		}

		boolean send(const String & name, int value) {
			return send(name, String(value));
		}

		boolean send(const String & name, long value) {
			return send(name, String(value));
		}

		boolean send(const String & name, float value) {
			return send(name, String(value));
		}

	    typedef void (*OnBooleanMessage)(String name, boolean value);
	    typedef void (*OnRangeMessage)(String name, int value);
	    typedef void (*OnStringMessage)(String name, String value);
	    typedef void (*OnCustomMessage)(String name, String value, const String type);
	    typedef void (*OnSBOpen)();
	    typedef void (*OnSBClose)(int code, const String message);
	    typedef void (*OnSBError)(const String message);

	    void onOpen(OnSBOpen function);
	    void onClose(OnSBClose function);
	    void onRangeMessage(OnRangeMessage function);
	    void onStringMessage(OnStringMessage function);
	    void onBooleanMessage(OnBooleanMessage function);
	    void onCustomMessage(OnCustomMessage function);
	    void onError(OnSBError function);
	    void killPids();
	    void getPids();


	private:

		Process brew;
		String name;
		String server;
		String description;
		static boolean _connected;
		int port;

		/**Output should be at least 5 cells**/
		static OnBooleanMessage _onBooleanMessage;
		static OnRangeMessage _onRangeMessage;
		static OnStringMessage _onStringMessage;
		static OnCustomMessage _onCustomMessage;
		static OnSBOpen _onOpen;
		static OnSBClose _onClose;
		static OnSBError _onError;

		Subscriber * subscribers;
		Publisher * publishers;
		String sub_name;
		String sub_msg;
		String sub_type;

		boolean read_name;
		boolean read_msg;
		int sub_name_max;
		int sub_msg_max;

		Process pids;
		char pid [6];
		int sbPids [4];


static char * createString(int len){
	char * out = ( char * )malloc( len + 1 );
	return out;
}		

};

#endif
