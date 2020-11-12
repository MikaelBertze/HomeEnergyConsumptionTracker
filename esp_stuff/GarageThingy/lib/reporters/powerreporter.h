#include<Arduino.h>
#include <mqttreporter.h>

class PowerReporter : public MqttReporter {
    public:
        //TempReporter(byte pin, mqttConfig mqtt_config, WiFiClient* espClient) 
        PowerReporter(byte pin, String id,  mqttConfig mqtt_config) 
          : MqttReporter(mqtt_config), pin_(pin), id_(id) 
        {
          
        }

        void SetTickPeriod(long tickPeriod){
          currentTickPeriod = tickPeriod;
        }

        void Report() {
          if (currentTickPeriod != lastSentTickPeriod) {
            report("{ \"id\" : \"" + id_ + "\", \"power_tick_period\" : " + currentTickPeriod + " }");
            lastSentTickPeriod = currentTickPeriod;
          }
        }

        byte GetTickPin() {
          return pin_;
        }

    private:
        byte pin_;
        String id_;
        int currentTickPeriod;
        int lastSentTickPeriod;
        
};