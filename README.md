Developed an embedded robotic control solution using Raspberry Pi Pico and Dobot Magician as part of a collaborative automated sorting project.

The system is designed to receive sorting orders wirelessly from a client application, process the order information on a Raspberry Pi Pico server, and control the Dobot Magician robotic arm through UART communication.

The sorting process involves detecting objects, identifying their colors, and performing pick-and-place operations according to the received order.

This repository focuses on the embedded server, robot communication, and hardware control components rather than the web application.

## Project Demonstration

### Hardware Setup

![Dobot Magician and Sorting System](images/hardware-setup.jpg)

*Dobot Magician robotic arm, conveyor belt, and sorting hardware.*

## System Workflow

**Client Order → Wi-Fi / TCP-IP → Raspberry Pi Pico Server → UART → Dobot Magician → Object Sorting**

1. The client application sends a sorting order over Wi-Fi.
2. The Raspberry Pi Pico server receives and processes the order.
3. Control commands are communicated to the Dobot Magician through UART.
4. The robotic system performs color-based pick-and-place operations.

## Technical Implementation

- **MicroPython:** Embedded programming on Raspberry Pi Pico.
- **TCP/IP Sockets:** Wireless communication and order reception.
- **UART:** Serial communication between the microcontroller and robotic arm.
- **JSON:** Processing incoming order information.
- **Robot Control:** Motion commands and suction-based object handling.
- **Hardware Integration:** Coordination with conveyor and sensor functions.

## Source Code

The repository contains modules for:

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

According to the project report, 58 out of 60 object placement attempts were successful, corresponding to approximately **96.7%**.

## My Contribution

My work focused on the embedded server and robotic control, including:

- Configuring communication between Raspberry Pi Pico and Dobot Magician.
- Developing UART-based robot control functions.
- Implementing TCP/IP communication for receiving orders.
- Integrating robotic movements with the sorting workflow.
- Supporting hardware integration, testing, and troubleshooting.

The overall system was developed collaboratively, with additional components implemented by other project members.

## Development Tools

- Raspberry Pi Pico
- Dobot Magician
- MicroPython
- Thonny IDE
- DobotStudio
- UART and TCP/IP communication

## Documentation

The project report provides further details on system architecture, implementation, testing, and results.

*Note: The repository documents an academic prototype. Additional hardware configuration and software dependencies may be required to reproduce the complete system.*
