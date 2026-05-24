#include <Arduino.h>

/**
 * UT33C+ Pico Rig Command Firmware
 * Hardware: Raspberry Pi Pico / YD-RP2040
 *
 * The Pico is flashed once and then controlled from a PC over USB serial.
 * Time-sensitive actions stay on the Pico; experiment sequencing and logging
 * live in host-side Python scripts.
 */

const char* FW_VERSION = "ut33c-rig-fw/1";

// Pin definitions
const int PIN_INT_TX = 0;        // UART0 TX -> internal pad RX
const int PIN_INT_RX = 1;        // UART0 RX <- internal pad TX
const int PIN_EXT_TX = 4;        // UART1 TX -> external pad RX
const int PIN_EXT_RX = 5;        // UART1 RX <- external pad TX
const int PIN_PAD1 = 14;         // soft reset, active low
const int PIN_PAD2 = 15;         // hard reset, active low
const int PIN_PWR_FET_POS = 16;  // positive rail, active high
const int PIN_PWR_FET_NEG = 17;  // ground rail, active low

const long BAUD_USB = 115200;
const long DEFAULT_METER_BAUD = 2400;
const size_t LINE_BUF_SIZE = 160;
const size_t MAX_TOKENS = 48;
const size_t MAX_BYTES = 32;

char lineBuf[LINE_BUF_SIZE];
size_t lineLen = 0;
long intBaud = DEFAULT_METER_BAUD;
long extBaud = DEFAULT_METER_BAUD;

struct ByteList {
    uint8_t bytes[MAX_BYTES];
    size_t count;
};

HardwareSerial& serialForPort(const char* port) {
    if (strcasecmp(port, "EXT") == 0) {
        return Serial2;
    }
    return Serial1;
}

const char* normalizedPortName(const char* port) {
    return strcasecmp(port, "EXT") == 0 ? "EXT" : "INT";
}

void printHexByte(uint8_t b) {
    if (b < 0x10) {
        Serial.print('0');
    }
    Serial.print(b, HEX);
}

bool parseLong(const char* text, long& out) {
    if (text == nullptr || *text == '\0') {
        return false;
    }

    char* end = nullptr;
    long value = strtol(text, &end, 10);
    if (end == text || *end != '\0') {
        return false;
    }

    out = value;
    return true;
}

bool parseHexByte(const char* text, uint8_t& out) {
    if (text == nullptr || *text == '\0') {
        return false;
    }

    char* end = nullptr;
    long value = strtol(text, &end, 16);
    if (end == text || *end != '\0' || value < 0 || value > 0xFF) {
        return false;
    }

    out = static_cast<uint8_t>(value);
    return true;
}

bool collectHexBytes(char** tokens, size_t start, size_t argc, ByteList& out) {
    out.count = 0;
    for (size_t i = start; i < argc; i++) {
        if (out.count >= MAX_BYTES) {
            Serial.println("ERR too many bytes");
            return false;
        }

        uint8_t value = 0;
        if (!parseHexByte(tokens[i], value)) {
            Serial.print("ERR invalid hex byte ");
            Serial.println(tokens[i]);
            return false;
        }
        out.bytes[out.count++] = value;
    }
    return true;
}

size_t splitTokens(char* line, char** tokens, size_t maxTokens) {
    size_t count = 0;
    char* token = strtok(line, " \t\r\n");
    while (token != nullptr && count < maxTokens) {
        tokens[count++] = token;
        token = strtok(nullptr, " \t\r\n");
    }
    return count;
}

void setPower(bool on) {
    if (on) {
        digitalWrite(PIN_PWR_FET_POS, HIGH);
        digitalWrite(PIN_PWR_FET_NEG, LOW);
    } else {
        digitalWrite(PIN_PWR_FET_POS, LOW);
        digitalWrite(PIN_PWR_FET_NEG, HIGH);
    }
}

void powerCycle(uint32_t postDelayMs) {
    setPower(false);
    delay(1500);
    setPower(true);
    delay(postDelayMs);
}

void pulseResetPin(int pin, uint32_t durationMs) {
    digitalWrite(pin, LOW);
    delay(durationMs);
    digitalWrite(pin, HIGH);
}

void beginMeterUart(const char* port, long baud) {
    if (strcasecmp(port, "EXT") == 0) {
        Serial2.end();
        Serial2.setTX(PIN_EXT_TX);
        Serial2.setRX(PIN_EXT_RX);
        Serial2.begin(baud);
        extBaud = baud;
    } else {
        Serial1.end();
        Serial1.setTX(PIN_INT_TX);
        Serial1.setRX(PIN_INT_RX);
        Serial1.begin(baud);
        intBaud = baud;
    }
}

void drainMeterUarts() {
    while (Serial1.available()) {
        Serial1.read();
    }
    while (Serial2.available()) {
        Serial2.read();
    }
}

void monitorPort(HardwareSerial& uart, const char* name, uint32_t durationMs) {
    uint32_t start = millis();
    uint8_t buf[16];
    size_t len = 0;
    uint32_t lastByteAt = 0;

    while (millis() - start < durationMs) {
        while (uart.available()) {
            if (len == 0) {
                lastByteAt = millis();
            }
            buf[len++] = static_cast<uint8_t>(uart.read());
            lastByteAt = millis();

            if (len == sizeof(buf)) {
                Serial.print("DATA ");
                Serial.print(name);
                Serial.print(' ');
                Serial.print(millis() - start);
                for (size_t i = 0; i < len; i++) {
                    Serial.print(' ');
                    printHexByte(buf[i]);
                }
                Serial.println();
                len = 0;
            }
        }

        if (len > 0 && millis() - lastByteAt >= 10) {
            Serial.print("DATA ");
            Serial.print(name);
            Serial.print(' ');
            Serial.print(millis() - start);
            for (size_t i = 0; i < len; i++) {
                Serial.print(' ');
                printHexByte(buf[i]);
            }
            Serial.println();
            len = 0;
        }

        yield();
    }

    if (len > 0) {
        Serial.print("DATA ");
        Serial.print(name);
        Serial.print(' ');
        Serial.print(millis() - start);
        for (size_t i = 0; i < len; i++) {
            Serial.print(' ');
            printHexByte(buf[i]);
        }
        Serial.println();
    }
}

void monitorBoth(uint32_t durationMs) {
    uint32_t start = millis();
    while (millis() - start < durationMs) {
        if (Serial1.available()) {
            monitorPort(Serial1, "INT", 1);
        }
        if (Serial2.available()) {
            monitorPort(Serial2, "EXT", 1);
        }
        yield();
    }
}

void writeBytes(HardwareSerial& uart, const ByteList& bytes, uint32_t gapMs) {
    for (size_t i = 0; i < bytes.count; i++) {
        uart.write(bytes.bytes[i]);
        uart.flush();
        if (gapMs > 0) {
            delay(gapMs);
        }
    }
}

void cmdHelp() {
    Serial.println("OK commands: PING HELP STATUS POWER RESET UART TX NULLS MONITOR MARKER CYCLE_MARKER");
    Serial.println("OK POWER ON|OFF|CYCLE [post_ms]");
    Serial.println("OK RESET PAD1|PAD2|BOTH [duration_ms]");
    Serial.println("OK UART INT|EXT <baud>");
    Serial.println("OK TX INT|EXT <hex bytes...>");
    Serial.println("OK NULLS INT|EXT <count> [gap_ms]");
    Serial.println("OK MONITOR INT|EXT|BOTH <duration_ms>");
    Serial.println("OK MARKER INT|EXT <timeout_ms> <post_ms> <markers...> RESP <response...>");
    Serial.println("OK CYCLE_MARKER INT|EXT <timeout_ms> <post_ms> <markers...> RESP <response...>");
}

void cmdStatus() {
    Serial.print("OK ");
    Serial.print(FW_VERSION);
    Serial.print(" power=");
    Serial.print(digitalRead(PIN_PWR_FET_POS) == HIGH && digitalRead(PIN_PWR_FET_NEG) == LOW ? "ON" : "OFF");
    Serial.print(" pad1=");
    Serial.print(digitalRead(PIN_PAD1));
    Serial.print(" pad2=");
    Serial.print(digitalRead(PIN_PAD2));
    Serial.print(" int_baud=");
    Serial.print(intBaud);
    Serial.print(" ext_baud=");
    Serial.println(extBaud);
}

void cmdPower(char** tokens, size_t argc) {
    if (argc < 2) {
        Serial.println("ERR POWER requires ON, OFF, or CYCLE");
        return;
    }

    if (strcasecmp(tokens[1], "ON") == 0) {
        setPower(true);
        Serial.println("OK POWER ON");
    } else if (strcasecmp(tokens[1], "OFF") == 0) {
        setPower(false);
        Serial.println("OK POWER OFF");
    } else if (strcasecmp(tokens[1], "CYCLE") == 0) {
        long postDelay = 500;
        if (argc >= 3 && (!parseLong(tokens[2], postDelay) || postDelay < 0)) {
            Serial.println("ERR invalid post delay");
            return;
        }
        powerCycle(static_cast<uint32_t>(postDelay));
        Serial.println("OK POWER CYCLE");
    } else {
        Serial.println("ERR unknown POWER action");
    }
}

void cmdReset(char** tokens, size_t argc) {
    if (argc < 2) {
        Serial.println("ERR RESET requires PAD1, PAD2, or BOTH");
        return;
    }

    long duration = 150;
    if (argc >= 3 && (!parseLong(tokens[2], duration) || duration < 1)) {
        Serial.println("ERR invalid reset duration");
        return;
    }

    if (strcasecmp(tokens[1], "PAD1") == 0) {
        pulseResetPin(PIN_PAD1, static_cast<uint32_t>(duration));
    } else if (strcasecmp(tokens[1], "PAD2") == 0) {
        pulseResetPin(PIN_PAD2, static_cast<uint32_t>(duration));
    } else if (strcasecmp(tokens[1], "BOTH") == 0) {
        digitalWrite(PIN_PAD1, LOW);
        digitalWrite(PIN_PAD2, LOW);
        delay(static_cast<uint32_t>(duration));
        digitalWrite(PIN_PAD1, HIGH);
        digitalWrite(PIN_PAD2, HIGH);
    } else {
        Serial.println("ERR unknown RESET target");
        return;
    }

    Serial.println("OK RESET");
}

void cmdUart(char** tokens, size_t argc) {
    if (argc < 3) {
        Serial.println("ERR UART requires port and baud");
        return;
    }

    long baud = 0;
    if (!parseLong(tokens[2], baud) || baud < 300) {
        Serial.println("ERR invalid baud");
        return;
    }

    beginMeterUart(tokens[1], baud);
    Serial.print("OK UART ");
    Serial.print(normalizedPortName(tokens[1]));
    Serial.print(' ');
    Serial.println(baud);
}

void cmdTx(char** tokens, size_t argc) {
    if (argc < 3) {
        Serial.println("ERR TX requires port and bytes");
        return;
    }

    ByteList bytes;
    if (!collectHexBytes(tokens, 2, argc, bytes)) {
        return;
    }

    HardwareSerial& uart = serialForPort(tokens[1]);
    writeBytes(uart, bytes, 0);
    Serial.print("OK TX ");
    Serial.print(normalizedPortName(tokens[1]));
    Serial.print(' ');
    Serial.println(bytes.count);
}

void cmdNulls(char** tokens, size_t argc) {
    if (argc < 3) {
        Serial.println("ERR NULLS requires port and count");
        return;
    }

    long count = 0;
    long gapMs = 10;
    if (!parseLong(tokens[2], count) || count < 1 || count > 255) {
        Serial.println("ERR invalid NULLS count");
        return;
    }
    if (argc >= 4 && (!parseLong(tokens[3], gapMs) || gapMs < 0)) {
        Serial.println("ERR invalid NULLS gap");
        return;
    }

    HardwareSerial& uart = serialForPort(tokens[1]);
    for (long i = 0; i < count; i++) {
        uart.write(static_cast<uint8_t>(0x00));
        uart.flush();
        if (gapMs > 0) {
            delay(static_cast<uint32_t>(gapMs));
        }
    }

    Serial.print("OK NULLS ");
    Serial.println(count);
}

void cmdMonitor(char** tokens, size_t argc) {
    if (argc < 3) {
        Serial.println("ERR MONITOR requires port and duration");
        return;
    }

    long duration = 0;
    if (!parseLong(tokens[2], duration) || duration < 1) {
        Serial.println("ERR invalid monitor duration");
        return;
    }

    Serial.println("OK MONITOR START");
    if (strcasecmp(tokens[1], "BOTH") == 0) {
        monitorBoth(static_cast<uint32_t>(duration));
    } else {
        monitorPort(serialForPort(tokens[1]), normalizedPortName(tokens[1]), static_cast<uint32_t>(duration));
    }
    Serial.println("OK MONITOR END");
}

void runMarkerResponse(HardwareSerial& uart, const char* portName, uint32_t timeoutMs, uint32_t postMs, const ByteList& markers, const ByteList& response) {
    uint32_t start = millis();
    bool sent = false;
    uint8_t matched = 0;

    while (millis() - start < timeoutMs) {
        if (uart.available()) {
            uint8_t value = static_cast<uint8_t>(uart.read());
            for (size_t i = 0; i < markers.count; i++) {
                if (value == markers.bytes[i]) {
                    matched = value;
                    writeBytes(uart, response, 0);
                    sent = true;
                    break;
                }
            }

            Serial.print("DATA ");
            Serial.print(portName);
            Serial.print(' ');
            Serial.print(millis() - start);
            Serial.print(' ');
            printHexByte(value);
            Serial.println();

            if (sent) {
                break;
            }
        }
        yield();
    }

    if (sent) {
        Serial.print("OK MARKER MATCH ");
        printHexByte(matched);
        Serial.println();
    } else {
        Serial.println("OK MARKER TIMEOUT");
    }

    monitorPort(uart, portName, postMs);
    Serial.println("OK MARKER END");
}

void cmdMarkerCommon(char** tokens, size_t argc, bool cyclePower) {
    if (argc < 7) {
        Serial.println("ERR marker command requires port, timeout, post_ms, markers, RESP, response");
        return;
    }

    long timeoutMs = 0;
    long postMs = 0;
    if (!parseLong(tokens[2], timeoutMs) || timeoutMs < 1 || !parseLong(tokens[3], postMs) || postMs < 0) {
        Serial.println("ERR invalid MARKER timing");
        return;
    }

    ByteList markers;
    markers.count = 0;
    size_t respIndex = 0;
    for (size_t i = 4; i < argc; i++) {
        if (strcasecmp(tokens[i], "RESP") == 0) {
            respIndex = i;
            break;
        }
        if (markers.count >= MAX_BYTES) {
            Serial.println("ERR too many marker bytes");
            return;
        }
        if (!parseHexByte(tokens[i], markers.bytes[markers.count++])) {
            Serial.print("ERR invalid marker byte ");
            Serial.println(tokens[i]);
            return;
        }
    }

    if (respIndex == 0 || markers.count == 0 || respIndex + 1 >= argc) {
        Serial.println("ERR MARKER missing marker list or response");
        return;
    }

    ByteList response;
    if (!collectHexBytes(tokens, respIndex + 1, argc, response)) {
        return;
    }

    HardwareSerial& uart = serialForPort(tokens[1]);
    const char* portName = normalizedPortName(tokens[1]);
    drainMeterUarts();

    if (cyclePower) {
        Serial.println("OK CYCLE_MARKER POWER_OFF");
        setPower(false);
        delay(1500);
        drainMeterUarts();
        setPower(true);
    }

    Serial.println("OK MARKER ARMED");
    runMarkerResponse(
        uart,
        portName,
        static_cast<uint32_t>(timeoutMs),
        static_cast<uint32_t>(postMs),
        markers,
        response
    );
}

void cmdMarker(char** tokens, size_t argc) {
    cmdMarkerCommon(tokens, argc, false);
}

void cmdCycleMarker(char** tokens, size_t argc) {
    cmdMarkerCommon(tokens, argc, true);
}

void processCommand(char* line) {
    char* tokens[MAX_TOKENS];
    size_t argc = splitTokens(line, tokens, MAX_TOKENS);
    if (argc == 0) {
        return;
    }

    if (tokens[0][0] == '#') {
        return;
    } else if (strcasecmp(tokens[0], "PING") == 0) {
        Serial.print("OK PONG ");
        Serial.println(FW_VERSION);
    } else if (strcasecmp(tokens[0], "HELP") == 0) {
        cmdHelp();
    } else if (strcasecmp(tokens[0], "STATUS") == 0) {
        cmdStatus();
    } else if (strcasecmp(tokens[0], "POWER") == 0) {
        cmdPower(tokens, argc);
    } else if (strcasecmp(tokens[0], "RESET") == 0) {
        cmdReset(tokens, argc);
    } else if (strcasecmp(tokens[0], "UART") == 0) {
        cmdUart(tokens, argc);
    } else if (strcasecmp(tokens[0], "TX") == 0) {
        cmdTx(tokens, argc);
    } else if (strcasecmp(tokens[0], "NULLS") == 0) {
        cmdNulls(tokens, argc);
    } else if (strcasecmp(tokens[0], "MONITOR") == 0) {
        cmdMonitor(tokens, argc);
    } else if (strcasecmp(tokens[0], "MARKER") == 0) {
        cmdMarker(tokens, argc);
    } else if (strcasecmp(tokens[0], "CYCLE_MARKER") == 0) {
        cmdCycleMarker(tokens, argc);
    } else {
        Serial.print("ERR unknown command ");
        Serial.println(tokens[0]);
    }
}

void readUsbSerial() {
    while (Serial.available()) {
        char c = static_cast<char>(Serial.read());
        if (c == '\n' || c == '\r') {
            if (lineLen > 0) {
                lineBuf[lineLen] = '\0';
                processCommand(lineBuf);
                lineLen = 0;
            }
        } else if (lineLen < LINE_BUF_SIZE - 1) {
            lineBuf[lineLen++] = c;
        } else {
            lineLen = 0;
            Serial.println("ERR command too long");
        }
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
    digitalWrite(PIN_PAD2, HIGH);
    setPower(true);

    beginMeterUart("INT", DEFAULT_METER_BAUD);
    beginMeterUart("EXT", DEFAULT_METER_BAUD);

    delay(500);
    Serial.print("READY ");
    Serial.println(FW_VERSION);
}

void loop() {
    readUsbSerial();

    static uint32_t lastBlink = 0;
    if (millis() - lastBlink >= 1000) {
        digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
        lastBlink = millis();
    }
}
