#include "wifi-credentials.h"
#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
#include <ESP8266mDNS.h>  
#include <ArduinoOTA.h>
#include <ledcontrol.h>
#include <tempreporter.h>
#include <doorreporter.h>
#include <powerreporter.h>

#ifndef IOT_ID
  #error “IOT_ID not specified. Define this in platform.ini for your target”
#endif 

#ifndef TOPIC_SPACE
  #error “TOPIC_SPACE not specified. Define this in platform.ini for your target”
#endif 



#define DEBOUNCE_MS 50
volatile long lastDebounceTime = 0;
volatile long lastTick = -1;

const char* mqtt_server = BROKER;
//const char* mqtt_garage_id = "garageThingy1";
const char* mqtt_temp_id = IOT_ID "_temp";
const char* mqtt_door_id = IOT_ID "_door";
const char* mqtt_power_id = IOT_ID "_power";


ESP8266WiFiMulti WiFiMulti;

TempReporter tempReporter(D1, IOT_ID, { mqtt_server, TOPIC_SPACE "temperature", mqtt_temp_id});
DoorReporter doorReporter(D6, IOT_ID, { mqtt_server, TOPIC_SPACE "door", mqtt_door_id});
PowerReporter powerReporter(D5, IOT_ID, { mqtt_server,TOPIC_SPACE "power", mqtt_power_id});

long tempReportLastSend = 0;
long doorReportLastSend = 0;
long powerReportLastSend = 0;


void reboot() {
  LedControl::RebootSignal();
  ESP.restart();
}

void ICACHE_RAM_ATTR handleInterrupt ();

void handleInterrupt() {
  // Check to see if the change is within a debounce delay threshold.
  boolean debounce = (millis() - lastDebounceTime) <= DEBOUNCE_MS;

  long timeNow = millis();
  // This update to the last debounce check is necessary regardless of debounce state.
  lastDebounceTime = timeNow;

  // Ignore reads within a debounce delay threshold.
  if(debounce) return;

  powerReporter.SetTickPeriod(timeNow - lastTick);
  
  lastTick = timeNow;
}

void verifyWifi() {

  if (WiFiMulti.run() == WL_CONNECTED)
    return;
  
  Serial.print("No connection...");
  LedControl::SetRed(true);
  byte num_retries = 60;
  byte retries = 0;
  while (WiFiMulti.run() != WL_CONNECTED) { // Wait for the Wi-Fi to connect: scan for Wi-Fi networks, and connect to the strongest of the networks above
    Serial.print("connecting...");
    delay(1000);
    LedControl::ToggleBlue();
    if(retries++ > num_retries){
      Serial.print("Restarting.");
      reboot();
    }
  }
  Serial.print("Connected to ");
  Serial.println(WiFi.SSID());              // Tell us what network we're connected to
  Serial.print("IP address:\t");
  Serial.println(WiFi.localIP());
  Serial.print("MAC: ");
  Serial.println(WiFi.macAddress());
  Serial.print("ChipID: ");
  Serial.println(ESP.getChipId());
  LedControl::SetRed(false);
}

void setup() {
  LedControl::InitLeds();
  
  Serial.begin(9600);
  Serial.setDebugOutput(true);
  delay(10);
  Serial.println("\n\n\n\n");
  Serial.println("setting up...");
  for (unsigned char i = 0; i < sizeof(wifiCredentials) / sizeof(wifiCredentials[0]); i+=2) {
     WiFiMulti.addAP(wifiCredentials[i], wifiCredentials[i+1]);
  }

  verifyWifi();
  
  LedControl::SetBlue(true);
  LedControl::SetRed(true);
  LedControl::SetGreen(true);
    
  for(byte i = 0; i < 10; i++){
    delay(50);
    LedControl::ToggleBlue();
    LedControl::ToggleRed();
    LedControl::ToggleGreen();
  }
  LedControl::SetBlue(false);
  LedControl::SetRed(false);
  LedControl::SetGreen(false);
    
  if(!tempReporter.connect() || !doorReporter.connect() || !powerReporter.connect())
  {
    Serial.println("Could not connect to broker. restarting...");
    reboot();
  }
  
  attachInterrupt(digitalPinToInterrupt(powerReporter.GetTickPin()), handleInterrupt, FALLING);
  
   if (!MDNS.begin(IOT_ID)) {             // Start the mDNS responder for esp8266.local
    Serial.println("Error setting up MDNS responder!");
  }
  Serial.println("mDNS responder started");
  ArduinoOTA.begin();
  LedControl::SetGreen(true);
}

void handleTempReporter() {
  tempReporter.reconnectingLoop();
  //garageReporter.report("Door!");
  long t = (millis() - tempReportLastSend) / 1000;
  if (t >= 10) {
    Serial.println("Sending temp report");
    tempReporter.Report();

    tempReportLastSend = millis();
  }
}

void handleDoorReporter() {
  doorReporter.reconnectingLoop();
  long t = (millis() - doorReportLastSend) / 1000;
  if (t >= 10) {
    Serial.println("Sending door report");
    bool state = doorReporter.Report();
    LedControl::SetRed(!state);
    doorReportLastSend = millis();
  }

}
void handlePowerReporter() {
  powerReporter.reconnectingLoop();
  powerReporter.Report();
}

void loop() {
  verifyWifi();
  handleTempReporter();  
  handleDoorReporter();
  handlePowerReporter();
  MDNS.update();
  ArduinoOTA.handle();
}
