#ifndef _MQTT_REPORTER_H
#define _MQTT_REPORTER_H

#include <PubSubClient.h>
#include <WiFi.h>

#define MSG_BUFFER_SIZE 100

  struct mqttConfig {
      const char* broker;
      const char* topic;
      const char* id;
    };


class MqttReporter {
  public:
    bool connect() {
      // Attempt to connect
      espClient_ = new WiFiClient();
      
      // pubsub_client = new PubSubClient();
      // _pubsub_client->setClient(*_eth_client);
      
      
      client_ = new PubSubClient();
      client_->setClient(*espClient_);
      client_->setServer(config_.broker, 1883);
      if (client_->connect(config_.id, "hallondisp", "disphallon")) {
         Serial.println("connected to broker");
         client_->publish("/megatron/IoT_status", "CONNECTED! WWWWOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO");
         return true;
      } 
      else {
         Serial.print("failed, rc=");
         Serial.print(client_->state());
         return false;
      }
    }

    void reconnectingLoop() {
      if (!client_->loop()) {
        if (!connect());
          ESP.restart();
      }
    }
  
    MqttReporter(mqttConfig config)
      : config_(config)//, espClient_() 
    { 
      
    }
    
    void report(String message) {
      char msg[MSG_BUFFER_SIZE];
      snprintf (msg, MSG_BUFFER_SIZE, message.c_str());
      client_->publish(config_.topic, msg);
    }

    

  private:
    mqttConfig config_;
    WiFiClient *espClient_;
    PubSubClient *client_;
    
};

#endif