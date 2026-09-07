#ifndef _WAKE_ON_LAN_H_
#define _WAKE_ON_LAN_H_

// data debe contener al menos 10 bytes: IPv4 de broadcast (4) y MAC (6).
void sendWakeOnLan(const byte* data);

#endif
