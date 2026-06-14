#include <Arduino.h>

#include "utils.h"
#include "rkbd.h"
#include "secret.h"


void printKbdMessage(const RkbdMessage message) {
  Serial.print("Counter: ");
  printHex(message.counter, sizeof(message.counter));
  Serial.println();
  Serial.print("Random: ");
  printHex(message.random, sizeof(message.random));
  Serial.println();
  Serial.print("Payload: ");
  printHex(message.payload, sizeof(message.payload));
  Serial.println();
  Serial.print("Hmac: ");
  printHex(message.hmac, sizeof(message.hmac));
  Serial.println();
}

void proccessMessage(const RkbdMessage message) {
  
}