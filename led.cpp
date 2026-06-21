#include <Arduino.h>


#include "led.h"

#define RGB_LED_PIN GPIO_NUM_48

void ledSetup() {
  if (!rmtInit(RGB_LED_PIN, RMT_TX_MODE, RMT_MEM_NUM_BLOCKS_1, 10000000)) {
    Serial.println("Led setup failed!");
  }

  ledOff();
}

void ledLoop() {

}

void writeColor(const LedColor color) {
  // Cada color son 24 bits
  rmt_data_t led_data[24];
  
  int i = 0;
  for (int c = 0; c < 3; c++) {     
    for (int bit = 0; bit < 8; bit++) {
      int col = 0;
      switch (c) {
        case 0:
          col = color.green;
          break;
        case 1:
          col = color.red;
          break;
        default:
          col = color.blue;      
      }
      if (col & (1 << (7 - bit))) {
        led_data[i].level0 = 1;
        led_data[i].duration0 = 8;
        led_data[i].level1 = 0;
        led_data[i].duration1 = 4;
      } else {
        led_data[i].level0 = 1;
        led_data[i].duration0 = 4;
        led_data[i].level1 = 0;
        led_data[i].duration1 = 8;
      }
      i++;
    }
  }

  // Send the data and wait until it is done
  rmtWrite(RGB_LED_PIN, led_data, 24, RMT_WAIT_FOR_EVER); 
}

void ledOn(LedColor color) {
  writeColor(color);
}

void ledOff() {
  writeColor(LED_OFF);
}