#ifndef _MQTT_REPORTER_H
#define _MQTT_REPORTER_H

#include <Arduino.h>
#include <PubSubClient.h>
#include <ESP8266WiFi.h>

#define MSG_BUFFER_SIZE 50

  struct mqttConfig {
      const char* broker;
      const char* topic;
      const char* id;
    };


class MqttReporter {
  public:
    bool connect() {
      // Attempt to connect
      client_.setServer(config_.broker, 1883);
      if (client_.connect(config_.id)) {
         Serial.println("connected");
         return true;
      } 
      else {
         Serial.print("failed, rc=");
         Serial.print(client_.state());
         return false;
      }
    }

    void reconnectingLoop() {
      if (!client_.loop()) {
        if (!connect());
          ESP.reset();
      }
    }
  
  protected:
    MqttReporter(mqttConfig config)
      : config_(config), espClient_() 
    { 
      client_ = PubSubClient(espClient_);
    }
    
    void report(String message) {
      char msg[MSG_BUFFER_SIZE];
      snprintf (msg, MSG_BUFFER_SIZE, message.c_str());
      client_.publish(config_.topic, msg);
    }

    

  private:
    mqttConfig config_;
    WiFiClient espClient_;
    PubSubClient client_;
    
};

#endif