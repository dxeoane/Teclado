#ifndef _UTILS_H_
#define _UTILS_H_

// Formatea la calidad de señal del WiFi
String formatSignalStrength(int rssi);

// Imprime una cadena de bytes
void printHex(byte* data, unsigned int length);


#endif