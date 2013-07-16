
#ifndef YUNSPACEBREW_H
#define YUNSPACEBREW_H

#include "Arduino.h"
#include "Process.h"

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

int const pidLength = 6;
int const sbPidsLen = 4;


class SpacebrewYun {

	public:
	    SpacebrewYun(const String clientName, const String description);
	    void addPublish(const String name, const String type);
	    void addSubscribe(const String name, const String type);
	    void connect(const String hostname, int port = 9000);
//	    void connect(const String hostname);
	    void connect();
	    void monitor();
	    boolean connected();
		static char * createString(int len);

	    bool send(const String name, const String value);
	    bool send(const String name, int value);
	    bool send(const String name, bool value);
	    bool send(const String name, float value);
	    bool send(const String name, long value);

	    typedef void (*OnBooleanMessage)(const String name, boolean value);
	    typedef void (*OnRangeMessage)(const String name, int value);
	    typedef void (*OnStringMessage)(const String name, const String value);
	    typedef void (*onCustomMessage)(const String name, const String value, const String type);
	    typedef void (*OnSBOpen)();
	    typedef void (*OnSBClose)(int code, const String message);
	    typedef void (*OnSBError)(const String message);

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
		char pid [6];
		int sbPids [4];

};

#endif
