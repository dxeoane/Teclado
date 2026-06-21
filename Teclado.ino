#include "config.h"

// Aqui van los parámetros que no se deben subir al repo de github (ssid, password, etc ...)
#include "secret.h"

#include <WiFi.h>
#include <PubSubClient.h>

#include "utils.h"
#include "led.h"
#include "rkbd.h"

#define MQTT_MAX_BUFFER_SIZE 256
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

unsigned long lastWifiCheckMillis = 0;

void setup() {  
  delay(1000);
  Serial.begin(115200); 
  randomSeed(micros());

  ledSetup();
  delay(1000);

  rkbdSetup();

  ledOn(RED);
  WiFi.mode(WIFI_STA);
  WiFi.begin(STASSID, STAPSK); 
  Serial.println("\n\n=== Remote keyboard ===\n");
  Serial.printf("MAC: %s\n", WiFi.macAddress().c_str()); 
  Serial.printf("Red: %s\n", STASSID); 
  Serial.print("Conectando ...") ;  
  int retries = 0;
  while (WiFi.status() != WL_CONNECTED && retries < 20) {
    Serial.print(".");
    retries++;
    delay(500);
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {  
    ledOn(ORANGE);
    Serial.printf("IP: %s\n", WiFi.localIP().toString().c_str());  
    Serial.printf("Gateway: %s\n", WiFi.gatewayIP().toString().c_str());  
    Serial.printf("DNS: %s\n", WiFi.dnsIP().toString().c_str());  
    int rssi = WiFi.RSSI();  
    Serial.printf("RSSI: %s\n", formatSignalStrength(rssi).c_str());   

    Serial.println("Conectando con el servidor MQTT ...");
    mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
    mqttClient.setCallback(mqttReceive);
    String mqttClientId = "Keyboard-";
    mqttClientId += String(random(0xffff), HEX);
    if (mqttClient.connect(mqttClientId.c_str(), MQTT_USER, MQTT_PASSWORD)) {
        ledOff();
        Serial.printf("MQTT Server: %s\n", MQTT_SERVER);
        if (mqttClient.subscribe(MQTT_TOPIC)) {
          Serial.printf("MQTT Topic: %s\n", MQTT_TOPIC);
        }
    } 
  }
}

void loop() {  

  checkWiFi();
  if (WiFi.status() != WL_CONNECTED) {   
    delay(1000);
    return;
  }

  mqttClient.loop();

  ledLoop();
}

WiFiClient checkClient;

void checkWiFi() {

  unsigned long now = millis(); 
  if (now - lastWifiCheckMillis < 5000) return;
  lastWifiCheckMillis = now;
  
  if (WiFi.status() == WL_CONNECTED) {
    if (checkClient.connect(WIFI_CHECK_ADDRESS, WIFI_CHECK_PORT)) {
      ledOn(ORANGE);
      checkClient.stop();    
      if (!mqttClient.connected()) {        
        mqttReconnect();
      } else {
        ledOff();
      }
      return;
    }   
    checkClient.stop();
  }
  
  ledOn(RED);
  Serial.println("No hay conexion WiFi!");   
  WiFi.disconnect();  

  Serial.print("Conectando ...");
  WiFi.begin(STASSID, STAPSK);  
  int retries = 0;
  while (WiFi.status() != WL_CONNECTED && retries < 20) {
    ledLoop();    
    Serial.print(".");
    delay(500);
    retries++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    ledOn(ORANGE);
    Serial.println("\nConexion WiFi restablecida.");
    Serial.printf("IP: %s\n", WiFi.localIP().toString().c_str());
  } else {
    Serial.println("\nNo se pudo restablecer la conexion!");
  } 
 
  lastWifiCheckMillis = now;
}

void mqttReceive(char* topic, byte* payload, unsigned int length) {

  // Si acabamos de recibir un mensaje damos por supuesto que la WiFi funciona bien
  lastWifiCheckMillis = millis();  

#ifdef SERIAL_DEBUG_ENABLED
  Serial.printf("Message arrived [%s]: ", topic);
  printHex(payload, length);
  Serial.println();
#endif   

  if (sizeof(RkbdMessage) != length) {
    #ifdef SERIAL_DEBUG_ENABLED
      Serial.println("Invalid message length");
    #endif
    return;
  }

  RkbdMessage message;
  memcpy(&message, payload, sizeof(message));

#ifdef SERIAL_DEBUG_ENABLED
  Serial.println("Keyboard message:");
  printKbdMessage(message);
#endif  

 // Procesamos el mensaje
 proccessMessage(message); 

}

void mqttReconnect() {
  if (!mqttClient.connected()) {
    ledOn(ORANGE);
    Serial.println("Volviendo a conectar con el servidor MQTT ...");
    String mqttClientId = "Keyboard-";
    mqttClientId += String(random(0xffff), HEX);
    if (mqttClient.connect(mqttClientId.c_str(), MQTT_USER, MQTT_PASSWORD)) {
        Serial.printf("MQTT Server: %s\n", MQTT_SERVER);
        if (mqttClient.subscribe(MQTT_TOPIC)) {
          Serial.printf("MQTT Topic: %s\n", MQTT_TOPIC);
          ledOff();
        }
    } else {
      Serial.println("Error al conectar con el servidor MQTT");
    }
  }
}
