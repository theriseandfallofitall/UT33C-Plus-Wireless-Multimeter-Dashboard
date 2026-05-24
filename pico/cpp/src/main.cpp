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

    Serial.println("\n\n########################################");
    Serial.println("# UT33C+ PICO 2 AUTOMATED RIG ONLINE   #");
    Serial.println("# STATUS: WAITING FOR MONITOR START... #");
    Serial.println("########################################");

    // Wait for start command ('S') from python monitor
    while (true) {
        if (Serial.available()) {
            char c = Serial.read();
            if (c == 'S') {
                Serial.println("[SYS] START COMMAND RECEIVED. BEGINNING FUZZ CYCLE.");
                break;
            }
        }
        // Heartbeat while waiting
        digitalWrite(LED_BUILTIN, HIGH);
        delay(500);
        digitalWrite(LED_BUILTIN, LOW);
        delay(500);
    }
}

void loop() {
    // Phase 1: Standard Baud Rate Sweep
    long bauds[] = {2400, 4800, 9600, 115200};
    for (int i = 0; i < 4; i++) {
        Serial.print("\n[PHASE 1] Testing Boot @ ");
        Serial.print(bauds[i]);
        Serial.println(" baud...");
        Serial1.begin(bauds[i]);
        Serial2.begin(bauds[i]);
        powerCycle(50);
        monitor(2000);
    }

    // Phase 2: R12 - Long NULL Blast (Watchdog Hunting)
    Serial.println("\n[PHASE 2] Starting R12: LONG NULL BLAST (10 seconds)...");
    Serial1.begin(2400);
    Serial2.begin(2400);

    pulseReset(PIN_PAD1, 100);
    
    // Hold RX line LOW (Continuous 0x00) for 10 seconds
    uint32_t start_blast = millis();
    while (millis() - start_blast < 10000) {
        Serial1.write((uint8_t)0x00);
        Serial2.write((uint8_t)0x00);
        delayMicroseconds(500); // Sustainable blast rate
        if ((millis() - start_blast) % 1000 == 0) {
            Serial.print("."); // Progress dots
        }
    }
    Serial.println("\n[SYS] Blast complete. Monitoring for recovery...");
    
    monitor(5000); // Long monitor for watchdog reboot

    Serial.println("\n\n########################################");
    Serial.println("# EXPERIMENT R12 COMPLETE              #");
    Serial.println("########################################");
    Serial.println("[SYS] Entering terminal state. Please switch mode and reset Pico.");

    while (true) {
        digitalWrite(LED_BUILTIN, HIGH);
        delay(50);
        digitalWrite(LED_BUILTIN, LOW);
        delay(50);
    }
}
