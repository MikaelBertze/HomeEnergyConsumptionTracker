#define RED_LED D4
#define BLUE_LED D2
#define GREEN_LED D3

#include <Arduino.h>

class LedControl {
    public:
        static void SetGreen(bool state) {
            digitalWrite(GREEN_LED, state ? HIGH : LOW);
        }
        static void SetRed(bool state) {
            digitalWrite(RED_LED, state ? HIGH : LOW);
        }
        static void SetBlue(bool state) {
            digitalWrite(BLUE_LED, state ? HIGH : LOW);
        }
        static void ToggleGreen() {
            digitalWrite(GREEN_LED, !digitalRead(GREEN_LED));
        }
        static void ToggleRed() {
            digitalWrite(RED_LED, !digitalRead(RED_LED));
        }
        static void ToggleBlue() {
            digitalWrite(BLUE_LED, !digitalRead(BLUE_LED));
        }
        
        static void InitLeds() {
            pinMode(RED_LED, OUTPUT);
            pinMode(BLUE_LED, OUTPUT);
            pinMode(GREEN_LED, OUTPUT);
            SetGreen(false);
            SetRed(false);
            SetBlue(false);
        }

        static void RebootSignal() {
            
            SetGreen(false);
            SetRed(false);
            SetBlue(false);

            for(byte i = 0; i < 20; i++) {
                ToggleBlue();
                ToggleRed();
                ToggleGreen();
                delay(200);
            }

            SetGreen(false);
            SetRed(false);
            SetBlue(false);
        }
};
