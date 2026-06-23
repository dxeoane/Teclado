#include <WiFiUdp.h>

#include "secret.h"
#include "wol.h"

WiFiUDP udp;

#define WAKE_ON_LAN_PORT 9

void sendWakeOnLan(const byte* mac) {

  byte packet[102];

  // 6 bytes a 0xFF
  for (int i = 0; i < 6; i++) {
    packet[i] = 0xFF;
  }

  // MAC repetida 16 veces
  for (int i = 1; i <= 16; i++) {
    memcpy(&packet[i * 6], mac, 6);
  }                 

  udp.beginPacket(WIFI_BROADCAST_ADDRESS, WAKE_ON_LAN_PORT);
  udp.write(packet, sizeof(packet));
  udp.endPacket();

}  