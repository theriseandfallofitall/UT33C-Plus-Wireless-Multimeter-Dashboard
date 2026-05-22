# Pi Pico Test Rig: Hardware Wiring Guide

This document details how to connect a Raspberry Pi Pico to the UNI-T UT33C+ for fully automated reverse engineering and protocol discovery.

## ⚠️ CRITICAL SAFETY WARNING
The internal UART Ground of the multimeter is directly connected to the **COM (Black Probel)** lead. 
- **DO NOT** connect the multimeter to high voltage while it is wired to the Pi Pico.
- If the Pico is connected to your PC via USB, your PC's ground is now tied to the multimeter's COM lead. 
- **ALWAYS** power the multimeter from a battery or an isolated 3V supply during testing.

---

## 🛠 Required Components
1. **Raspberry Pi Pico** (or Pico W)
2. **N-Channel MOSFET** (e.g., 2N7000, BSS138, or IRLZ44N)
3. **UT33C+ Multimeter** (Opened, with wires soldered to pads)
4. **Jumper Wires**

---

## 📍 Pin Mapping Table

| Pico Pin | Name | Connection Target | Function |
| :--- | :--- | :--- | :--- |
| **GP0** | UART0 TX | **Internal RX Pad** | Inject commands to internal port |
| **GP1** | UART0 RX | **Internal TX Pad** | Monitor raw high-speed data |
| **GP4** | UART1 TX | **External RX Pad** | Inject commands to opto-port |
| **GP5** | UART1 RX | **External TX Pad** | Monitor legacy PC-Link data |
| **GP14** | GPIO OUT | **Pad 1 (Soft Reset)** | Trigger logic reset / Long beep |
| **GP15** | GPIO OUT | **Pad 2 (Hard Reset)** | Trigger CPU halt / Full reboot |
| **GP16** | GPIO OUT | **MOSFET Gate** | Automated Power Control |
| **GND** | Ground | **Meter COM / UART GND**| Common Ground reference |

---

## ⚡ Power Control Schematic (MOSFET)

To automate power cycling, we use an N-Channel MOSFET as a "Low-Side Switch". This allows the Pico to completely disconnect the meter from its battery.

1. **Meter Battery Negative (-)** -> MOSFET **Drain**.
2. **Pico GND** -> MOSFET **Source** -> **Meter VCC Negative Input**.
3. **Pico GP16** -> MOSFET **Gate**.
4. **Meter Battery Positive (+)** -> **Meter VCC Positive Input**.

*When GP16 is HIGH, the meter is ON. When GP16 is LOW, the meter is OFF.*

---

## 🔌 UART Connections

### 1. Internal Pads (High-Speed)
These are the pads we found auto-transmitting at 2400 baud.
- **Pico GP1 (RX)** <--- **Meter TX Pad**
- **Pico GP0 (TX)** ---> **Meter RX Pad**

### 2. External Pads (Legacy)
These are the pads near the opto-port window.
- **Pico GP5 (RX)** <--- **Meter TX Pad**
- **Pico GP4 (TX)** ---> **Meter RX Pad**

### 3. Reset Control
- **Pico GP14** ---> **Pad 1**
- **Pico GP15** ---> **Pad 2**
