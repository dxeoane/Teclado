#ifndef _RKBD_H_
#define _RKBD_H_

struct RkbdMessage {
  byte counter[8];
  byte random[8];
  byte payload[16];
  byte hmac[32];
};


void printKbdMessage(const RkbdMessage message);

void proccessMessage(const RkbdMessage message);

#endif