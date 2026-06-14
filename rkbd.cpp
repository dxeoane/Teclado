#include <Arduino.h>
#include <mbedtls/aes.h>
#include <mbedtls/md.h>

#include "USB.h"
#include "USBHIDKeyboard.h"

#include "config.h"
#include "utils.h"
#include "rkbd.h"
#include "secret.h"

USBHIDKeyboard Keyboard;

uint64_t lastCounter = 0;

void rkbdSetup() {
  Keyboard.begin();
  USB.begin();
}

void printKbdMessage(const RkbdMessage message) {
  Serial.print("Counter: ");
  printHex(message.counter, sizeof(message.counter));
  Serial.println();
  Serial.print("Random: ");
  printHex(message.random, sizeof(message.random));
  Serial.println();
  #ifdef SERIAL_DEBUG_UNSAFE
    Serial.print("Payload: ");
    printHex(message.payload, sizeof(message.payload));
    Serial.println();
  #endif
  Serial.print("Hmac: ");
  printHex(message.hmac, sizeof(message.hmac));
  Serial.println();
}

void printKbdCommand(const RkbdCommand command) {
  Serial.print("ID: ");
  printHex(&command.id, sizeof(command.id));
  Serial.println();
  switch (command.id) {
    case RKBD_COMMAND_PRINT:
       Serial.println("Command: RKBD_COMMAND_PRINT");
       break;
    case RKBD_COMMAND_PRINTLN:
       Serial.println("Command: RKBD_COMMAND_PRINTLN");
       break;
    case RKBD_COMMAND_PRESS:
       Serial.println("Command: RKBD_COMMAND_PRESS");
       break;
    case RKBD_COMMAND_RELEASE:
       Serial.println("Command: RKBD_COMMAND_RELEASE");
       break;
    case RKBD_COMMAND_RELEASE_ALL:
       Serial.println("Command: RKBD_COMMAND_RELEASE_ALL");
       break;
    case RKBD_COMMAND_STROKE:
       Serial.println("Command: RKBD_COMMAND_STROKE");
       break;   
    default:
      Serial.printf("Command: NOT IMPLEMENTED (%d)\n", command.id);   
  }
  #ifdef SERIAL_DEBUG_UNSAFE
    Serial.print("Data: ");
    printHex(command.data, sizeof(command.data));
    Serial.println();
  #endif  
}

uint64_t readUint64BE(const byte in[8]) {
  uint64_t value = 0;

  for (int i = 0; i < 8; i++) {
    value = (value << 8) | in[i];
  }

  return value;
}

void makeNonce(const RkbdMessage message, uint8_t nonce[16]) {
  memcpy(nonce, message.counter, 8);
  memcpy(nonce + 8, message.random, 8);
}

void aesCtrCrypt(
  const RkbdMessage &message,
  byte output[16]
) {
  size_t ncOff = 0;
  uint8_t nonceCounter[16];
  uint8_t streamBlock[16];  

  makeNonce(message, nonceCounter);
  memset(streamBlock, 0, 16);

  mbedtls_aes_context aesContext;
  mbedtls_aes_init(&aesContext);

  mbedtls_aes_setkey_enc(&aesContext, KEYBOARD_AES_KEY, 256);

  mbedtls_aes_crypt_ctr(
    &aesContext,
    16,
    &ncOff,
    nonceCounter,
    streamBlock,
    message.payload,
    output
  );

  mbedtls_aes_free(&aesContext);
}

void calculateHmac(const RkbdMessage &message, byte out[32]) {
  mbedtls_md_context_t ctx;

  mbedtls_md_init(&ctx);

  mbedtls_md_setup(
    &ctx,
    mbedtls_md_info_from_type(MBEDTLS_MD_SHA256),
    1
  );

  mbedtls_md_hmac_starts(&ctx, KEYBOARD_HMAC_KEY, sizeof(KEYBOARD_HMAC_KEY));
  mbedtls_md_hmac_update(&ctx, message.counter, 8);
  mbedtls_md_hmac_update(&ctx, message.random, 8);
  mbedtls_md_hmac_update(&ctx, message.payload, 16);
  mbedtls_md_hmac_finish(&ctx, out);

  mbedtls_md_free(&ctx);
}

bool constantTimeEqual(const byte *a, const byte *b, size_t len) {
  uint8_t diff = 0;

  for (size_t i = 0; i < len; i++) {
    diff |= a[i] ^ b[i];
  }

  return diff == 0;
}

void proccessMessage(const RkbdMessage message) {

  byte expectedHmac[32];

  calculateHmac(message, expectedHmac);

  if (!constantTimeEqual(expectedHmac, message.hmac, 32)) {
    #ifdef SERIAL_DEBUG_ENABLED
      Serial.println("HMAC invalido");
    #endif
    return;
  }

  uint64_t counterValue = readUint64BE(message.counter);

   if (counterValue <= lastCounter) {
    #ifdef SERIAL_DEBUG_ENABLED
      Serial.println("Replay detectado");
    #endif
    return;
  }

  lastCounter = counterValue;

  RkbdCommand command;
  aesCtrCrypt(message,(byte*)&command);

  #ifdef SERIAL_DEBUG_ENABLED
    Serial.println("RKbd command:");
    printKbdCommand(command);
  #endif

  proccessCommand(command);

}

void proccessCommand(const RkbdCommand command) {

  char buffer[16];
  memset(buffer, 0, 16);

  switch (command.id) {
    case RKBD_COMMAND_PRINT:
      memcpy(buffer, command.data, 15);
      Keyboard.print(buffer);
      return;
    case RKBD_COMMAND_PRINTLN:
      memcpy(buffer, command.data, 15);
      Keyboard.println(buffer);
      return;
    case RKBD_COMMAND_PRESS:
      Keyboard.press(command.data[0]);
      return;
    case RKBD_COMMAND_RELEASE:
      Keyboard.release(command.data[0]);
      return;
    case RKBD_COMMAND_RELEASE_ALL:
      Keyboard.releaseAll();
      return;
    case RKBD_COMMAND_STROKE:
      Keyboard.press(command.data[0]);
      delay(20);
      Keyboard.release(command.data[0]);
    default:
      return;   
  }

}