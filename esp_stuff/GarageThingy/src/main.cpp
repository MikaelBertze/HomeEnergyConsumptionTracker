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

#define DEBOUNCE_MS 50
volatile long lastDebounceTime = 0;
volatile long lastTick = -1;

const char* mqtt_server = "192.168.1.150";
const char* mqtt_garage_id = "garageThingy1";
const char* mqtt_temp_id = "garageThingy_temp";
const char* mqtt_door_id = "garageThingy_door";
const char* mqtt_power_id = "garageThingy_power";


ESP8266WiFiMulti WiFiMulti;

TempReporter tempReporter(D1, String(ESP.getChipId())+ "_1", { mqtt_server, "/megatron/temperature", mqtt_temp_id});
DoorReporter doorReporter(D6, String(ESP.getChipId())+ "_2", { mqtt_server, "/megatron/door", mqtt_door_id});
PowerReporter powerReporter(D5, String(ESP.getChipId()) + "_3", { mqtt_server, "/megatron/power", mqtt_power_id});

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

  uint32_t test = 15000;
  if (WiFiMulti.run() == WL_CONNECTED)
    return;
  
  Serial.print("No connection...");
  LedControl::SetRed(true);
  byte num_retries = 60;
  byte retries = 0;
  while (WiFiMulti.run(15000) != WL_CONNECTED) { // Wait for the Wi-Fi to connect: scan for Wi-Fi networks, and connect to the strongest of the networks above
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
  delay(10);
  Serial.println("\n\n\n\n");

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
  
   if (!MDNS.begin("garagethingy")) {             // Start the mDNS responder for esp8266.local
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
}

void loop() {
  verifyWifi();
  handleTempReporter();  
  handleDoorReporter();
  handlePowerReporter();
  powerReporter.Report();

  MDNS.update();
  ArduinoOTA.handle();
}
