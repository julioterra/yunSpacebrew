
#ifndef YUNSPACEBREW_H
#define YUNSPACEBREW_H

#include "Arduino.h"

enum SBmsg { MSG_START = char(29), MSG_DIV = char(30), MSG_END = char(31) };

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

class SpacebrewYun {

	public:
	    SpacebrewYun(String clientName, String description);
	    void addPublish(String name, String type);
	    void addSubscribe(String name, String type);
	    void connect(String hostname, int port = 9000);
	    void connect();
	    void monitor();

	    bool send(String name, String value);
	    bool send(String name, int value);
	    bool send(String name, bool value);
	    bool send(String name, float value);
	    bool send(String name, long value);

	    typedef void (*OnBooleanMessage)(String name, boolean value);
	    typedef void (*OnRangeMessage)(String name, int value);
	    typedef void (*OnStringMessage)(String name, String value);
	    typedef void (*onCustomMessage)(String name, String value, String type);
	    typedef void (*OnSBOpen)();
	    typedef void (*OnSBClose)(int code, String message);
	    typedef void (*OnSBError)(String message);

	    void onOpen(OnSBOpen function);
	    void onClose(OnSBClose function);
	    void onRangeMessage(OnRangeMessage function);
	    void onStringMessage(OnStringMessage function);
	    void onBooleanMessage(OnBooleanMessage function);
	    void onOtherMessage(OnStringMessage function);
	    void onError(OnSBError function);

	private:
		// static bool m_bOpen;
		// static bool m_bSendConfig;
		static boolean _connected;

		String name;
		String server;
		String description;
		int port;

		/**Output should be at least 5 cells**/
		static OnBooleanMessage _onBooleanMessage;
		static OnRangeMessage _onRangeMessage;
		static OnStringMessage _onStringMessage;
		static OnStringMessage _onOtherMessage;
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
		int const pidLength = 6;
		int const sbPidsLen = 4;
		char pid [6];
		int sbPids [4];

};

#endif