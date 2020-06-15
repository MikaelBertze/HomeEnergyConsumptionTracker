#include<Arduino.h>
#include <mqttreporter.h>

class DoorReporter : public MqttReporter {
    public:
        //TempReporter(byte pin, mqttConfig mqtt_config, WiFiClient* espClient) 
        DoorReporter(byte pin, String id,  mqttConfig mqtt_config) 
          : MqttReporter(mqtt_config), pin_(pin) 
        { 
          pinMode(pin_, INPUT);           
        }

        void Report() {
          bool state = digitalRead(pin_);
          report("{ \"id\" : \"" + id_ + "\", \"door\" : \"" + (state ? "true" : "false") + "}");
        }

    private:
        byte pin_;
        String id_;
};