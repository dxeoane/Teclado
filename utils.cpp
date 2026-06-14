#include <Arduino.h>
#include "config.h"

// Formatea la calidad de señal del WiFi
String formatSignalStrength(int rssi) {
  int quality = 0;

  if (rssi <= -100) {
    quality = 0;                // Sin señal
  } else if (rssi >= -50) {
    quality = 100;              // Señal máxima
  } else {
    quality = 2 * (rssi + 100); // Escala lineal entre -100 y -50 dBm
  }

  int bars = quality / 20;
  String signalText = "[";

  for (int i = 0; i < 5; i++) {
    if (i < bars) {
      signalText += "="; 
    } else {
      signalText += " ";
    }
  }

  signalText += "] ";

  if (quality >= 80) {
    signalText += "Excelente";
  } else if (quality >= 60) {
    signalText += "Buena";
  } else if (quality >= 40) {
    signalText += "Regular";
  } else if (quality >= 20) {
    signalText += "Baja";
  } else {
    signalText += "";
  }

  return signalText;
}

void printHex(const byte* data, unsigned int length) {
  for (size_t i = 0; i < length; i++) {
    if ((i > 0) && (i % 8 == 0)) {
      Serial.print(" ");
    }
    Serial.printf("%02X", data[i]);
  }
}