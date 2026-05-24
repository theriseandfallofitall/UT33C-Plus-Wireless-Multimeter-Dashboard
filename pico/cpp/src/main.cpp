#include <Arduino.h>

/**
 * UT33C+ Pico Raw UART Passthrough Firmware
 * Hardware: Raspberry Pi Pico / YD-RP2040
 *
 * This firmware acts as a passive USB-to-UART adapter for the multimeter's
 * internal 2400 baud TX/RX pads. Power and reset pins are not configured, so
 * they remain high-impedance and do not interfere with an externally powered
 * meter.
 */

const int PIN_INT_TX = 0;        // UART0 TX -> internal pad RX
const int PIN_INT_RX = 1;        // UART0 RX <- internal pad TX

const long METER_BAUD = 2400;

void setup() {
    Serial.begin(115200);

    Serial1.setTX(PIN_INT_TX);
    Serial1.setRX(PIN_INT_RX);
    Serial1.begin(METER_BAUD);

    pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
    while (Serial.available()) {
        Serial1.write(Serial.read());
    }

    while (Serial1.available()) {
        Serial.write(Serial1.read());
    }

    static uint32_t lastBlink = 0;
    if (millis() - lastBlink >= 500) {
        digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
        lastBlink = millis();
    }
}
