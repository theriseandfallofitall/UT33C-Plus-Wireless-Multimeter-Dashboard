#include <Arduino.h>

/**
 * UT33C+ Automated Fuzzer & Monitor
 * Hardware: Raspberry Pi Pico 2 (RP2350)
 * Core: Earle Philhower RP2040/RP2350
 */

// Pin Definitions
const int PIN_INT_TX  = 0;   // UART0 TX -> Internal Pad RX
const int PIN_INT_RX  = 1;   // UART0 RX <- Internal Pad TX
const int PIN_EXT_TX  = 4;   // UART1 TX -> External Pad RX
const int PIN_EXT_RX  = 5;   // UART1 RX <- External Pad TX
const int PIN_PAD1    = 14;  // Soft Reset (Active High pulse to GND?) - Verify logic
const int PIN_PAD2    = 15;  // Hard Reset
const int PIN_PWR_FET_POS = 16;  // 3.3V Rail (Active HIGH: 1=ON, 0=OFF)
const int PIN_PWR_FET_NEG = 17;  // GND Rail (Active LOW: 0=ON, 1=OFF)

// Configuration
const long BAUD_USB = 115200;

void powerCycle(int postDelayMs = 500) {
    Serial.println("[SYS] Powering OFF (Inverted Dual Rail)...");
    // To cut power: POS -> LOW (Off), NEG -> HIGH (Off)
    digitalWrite(PIN_PWR_FET_POS, LOW);
    digitalWrite(PIN_PWR_FET_NEG, HIGH);
    delay(1500); // 1.5s to ensure full capacitor discharge
    
    Serial.println("[SYS] Powering ON...");
    // To restore power: POS -> HIGH (On), NEG -> LOW (On)
    digitalWrite(PIN_PWR_FET_POS, HIGH);
    digitalWrite(PIN_PWR_FET_NEG, LOW);
    delay(postDelayMs);
}

void pulseReset(int pin, int durationMs = 150) {
    Serial.print("[SYS] Pulsing Reset (Active Low) on Pin ");
    Serial.println(pin);
    digitalWrite(pin, LOW);
    delay(durationMs);
    digitalWrite(pin, HIGH);
}

void monitor(uint32_t durationMs) {
    uint32_t start = millis();
    while (millis() - start < durationMs) {
        // Monitor Internal Port
        if (Serial1.available()) {
            Serial.print("INT: ");
            while (Serial1.available()) {
                byte b = Serial1.read();
                if (b < 0x10) Serial.print("0");
                Serial.print(b, HEX);
                Serial.print(" ");
            }
            Serial.println();
        }
        
        // Monitor External Port
        if (Serial2.available()) {
            Serial.print("EXT: ");
            while (Serial2.available()) {
                byte b = Serial2.read();
                if (b < 0x10) Serial.print("0");
                Serial.print(b, HEX);
                Serial.print(" ");
            }
            Serial.println();
        }
        yield();
    }
}

void setup() {
    Serial.begin(BAUD_USB);
    
    pinMode(LED_BUILTIN, OUTPUT);
    pinMode(PIN_PAD1, OUTPUT);
    pinMode(PIN_PAD2, OUTPUT);
    pinMode(PIN_PWR_FET_POS, OUTPUT);
    pinMode(PIN_PWR_FET_NEG, OUTPUT);
    
    digitalWrite(PIN_PAD1, HIGH);
    digitalWrite(PIN_PAD2, HIGH); // Start with RESET pins HIGH (Run State)
    digitalWrite(PIN_PWR_FET_POS, HIGH); 
    digitalWrite(PIN_PWR_FET_NEG, LOW); // Start with GND ON (Active LOW)

    // Configure Hardware UARTs
    Serial1.setTX(PIN_INT_TX);
    Serial1.setRX(PIN_INT_RX);
    Serial1.begin(2400);

    Serial2.setTX(PIN_EXT_TX);
    Serial2.setRX(PIN_EXT_RX);
    Serial2.begin(2400);

    delay(2000);
    Serial.println("\n\n########################################");
    Serial.println("# UT33C+ PICO 2 AUTOMATED RIG ONLINE   #");
    Serial.println("########################################");
}

void loop() {
    // Phase 1: Baud Rate Sweep on Boot
    long bauds[] = {2400, 4800, 9600, 19200, 38400, 115200};
    for (int i = 0; i < 6; i++) {
        Serial.print("\n[PHASE 1] Testing Boot @ ");
        Serial.print(bauds[i]);
        Serial.println(" baud...");
        
        Serial1.begin(bauds[i]);
        Serial2.begin(bauds[i]);
        
        powerCycle(50); // Fast boot monitor
        monitor(2000);
    }

    // Phase 2: Reset Injection (Pad 2)
    Serial.println("\n[PHASE 2] Starting Reset Injection Fuzzing...");
    Serial1.begin(2400);
    Serial2.begin(2400);
    
    // Commands often used in UNI-T or generic multimeters
    const int CMD_COUNT = 5;
    byte cmds[CMD_COUNT][2] = {
        {0xAB, 0x01}, // Sync/Wake
        {0xAB, 0x00}, // Reset
        {0x55, 0xAA}, // Pattern
        {0x01, 0x02}, // Generic
        {0x7F, 0x7F}  // All high
    };

    for (int i = 0; i < CMD_COUNT; i++) {
        Serial.print("Target: ");
        Serial.print(cmds[i][0], HEX);
        Serial.print(" ");
        Serial.println(cmds[i][1], HEX);

        pulseReset(PIN_PAD2, 100);
        
        // Rapid injection during the reset recovery window
        for (int j = 0; j < 100; j++) {
            Serial1.write(cmds[i], 2);
            Serial2.write(cmds[i], 2);
            delayMicroseconds(100);
        }
        
        monitor(1500);
    }

    Serial.println("\n[SYS] Loop complete. Waiting for next cycle...");
    // Heartbeat while waiting
    for(int i=0; i<10; i++) {
        digitalWrite(LED_BUILTIN, HIGH);
        delay(100);
        digitalWrite(LED_BUILTIN, LOW);
        delay(900);
    }
}
