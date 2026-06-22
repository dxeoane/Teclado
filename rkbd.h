#ifndef _RKBD_H_
#define _RKBD_H_

struct RkbdMessage {
  byte counter[8];
  byte random[8];
  byte payload[16];
  byte hmac[32];
};

// Commands
#define RKBD_COMMAND_PRINT       0x01
#define RKBD_COMMAND_PRINTLN     0x02
#define RKBD_COMMAND_PRESS       0x03
#define RKBD_COMMAND_RELEASE     0x04
#define RKBD_COMMAND_RELEASE_ALL 0x05
#define RKBD_COMMAND_STROKE      0x06
#define RKBD_COMMAND_STROKE      0x06
#define RKBD_COMMAND_HOTKEY      0x07

struct RkbdCommand {
  byte id;
  byte data[15];
};

void rkbdSetup();

void printKbdMessage(const RkbdMessage message);
void printKbdCommand(const RkbdCommand command);

void proccessMessage(const RkbdMessage message);
void proccessCommand(const RkbdCommand command);

#endif