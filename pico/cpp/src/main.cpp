#include <Arduino.h>

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  // USB Serial Initialization
  Serial.begin(115200);
}

void loop() {
  // LED Heartbeat
  digitalWrite(LED_BUILTIN, HIGH);
  delay(100);
  digitalWrite(LED_BUILTIN, LOW);
  delay(900);

  // Serial Output
  Serial.print("[");
  Serial.print(millis());
  Serial.println("] Pico 2 Serial Test: System Online.");
}
