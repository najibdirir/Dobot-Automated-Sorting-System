
# Dobot Automated Sorting System

**Embedded Systems | Robotics | MicroPython | UART | Wi-Fi / TCP-IP**

**Halmstad University | Development Project | 2025**

## Project Overview

Developed an embedded robotic control solution using Raspberry Pi Pico and Dobot Magician as part of a collaborative automated sorting project.

The system receives sorting orders wirelessly from a client application through Wi-Fi and TCP/IP. A Raspberry Pi Pico server processes the order information and communicates with the Dobot Magician robotic arm via UART.

The sorting process involves object detection, color identification, and robotic pick-and-place operations based on the received order.

This repository focuses on embedded server functionality, robot communication, and hardware control rather than the web application.

## Project Demonstration

### Physical Prototype

<!-- IMAGE 1: Actual project prototype -->

![Automated Sorting System Prototype](images/projekt.jpg)

*Physical prototype featuring the Dobot Magician robotic arm, conveyor system, sensors, and control hardware.*

## System Workflow

**Client Order → Wi-Fi / TCP-IP → Raspberry Pi Pico Server → UART → Dobot Magician → Object Sorting**

1. The client application sends a sorting order over Wi-Fi.
2. The Raspberry Pi Pico server receives and processes the order.
3. The conveyor and sensor system detects objects and identifies their colors.
4. Control commands are sent to the Dobot Magician through UART.
5. The robotic arm performs pick-and-place operations according to the order.

### Sorting Process Flowchart

<!-- IMAGE 2: Sorting flowchart -->

![Automated Sorting Workflow](images/flowchart.png)

*Flowchart illustrating order reception, object detection, color identification, and robotic sorting.*

## Technical Implementation

- **MicroPython:** Embedded programming on Raspberry Pi Pico.
- **TCP/IP Sockets:** Wireless communication and order reception.
- **UART:** Serial communication between the microcontroller and robotic arm.
- **JSON:** Processing incoming order information.
- **Robot Control:** Movement commands and suction-based object handling.
- **Hardware Integration:** Coordination with conveyor and sensor functions.

### Hardware Configuration

<!-- IMAGE 3: Hardware illustration -->

![Dobot Sorting Hardware](images/dobot.png)

*Illustration of the robotic sorting configuration with Dobot Magician arms, a conveyor belt, and colored objects.*

## Source Code

The repository contains the following modules:

| Module | Description |
|---|---|
| `server.py` | TCP socket communication and incoming order processing |
| `wifi-pico.py` | Wireless connection and server command handling |
| `robot.py` | Dobot UART communication and robotic control |
| `band.py` | Conveyor-related control functions |
| `main.py` | Initialization and control integration |
| `mesage.py` | Communication message handling |

Some scripts represent separate development or testing stages and may require additional dependencies or configuration.

## Testing and Results

The project involved UART communication tests, wireless connection testing, robot movement verification, and integrated sorting tests.

According to the project report, **58 out of 60 object placement attempts were successful (96.7%)**.

## My Contribution

My work focused on embedded server development, robotic control, and integration, including:

- Configuring UART communication between Raspberry Pi Pico and Dobot Magician.
- Developing robot movement and control functions.
- Implementing TCP/IP communication for receiving sorting orders.
- Integrating robot operations with the sorting process.
- Supporting hardware integration, testing, and troubleshooting.

The overall system was developed collaboratively, with other project members contributing additional components.

## Development Tools

- Raspberry Pi Pico
- Dobot Magician
- MicroPython
- Thonny IDE
- DobotStudio
- UART and TCP/IP communication

## Documentation

The project report contains further details about the system architecture, implementation, testing, and results.

*Note: This repository documents an academic prototype. Additional hardware configuration and software dependencies may be required to reproduce the complete system.*
