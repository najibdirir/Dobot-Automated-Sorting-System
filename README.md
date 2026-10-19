# Automated Color Sorting System – Dobot Magician & Raspberry Pi Pico

**Embedded Systems | Robotics | Industrial Automation | MicroPython**

**Institution:** Halmstad University  
**Course:** Development Project (Utvecklingsprojekt)  
**Year:** 2025  
**Platform:** Dobot Magician & Raspberry Pi Pico

## Project Overview

This project explores the development of an automated robotic sorting system capable of identifying, picking, and placing objects according to their colors and incoming orders.

The system integrates a Dobot Magician robotic arm, Raspberry Pi Pico, conveyor belt, color sensors, IR sensors, and network communication.

The development was carried out as a collaborative engineering project consisting of four subsystems: web/database, client interface, embedded server and robotic control, and PLC automation.

This repository focuses primarily on the embedded control, communication, and robot integration components.

## Project Demonstration

The physical prototype combines a robotic arm with a conveyor belt and sensors to perform color-based sorting.

<!-- Add a real prototype image here after uploading it to images/ -->

## System Architecture

The system consists of four cooperating subsystems:

| Subsystem | Responsibility |
|---|---|
| Web & Database | Order management and data storage |
| Client Application | Graphical interface and communication with the server |
| Embedded Server & Robot Control | Raspberry Pi Pico, TCP/IP communication, UART protocol, robotic movements and sorting logic |
| PLC & Automation | Conveyor control and coordination of physical components |

### Communication Architecture

The client application and embedded server communicate wirelessly over Wi-Fi using TCP/IP.

The Raspberry Pi Pico receives order information, processes commands, and communicates with the Dobot Magician through a UART serial interface.

The robotic control software handles movement commands and supports automated pick-and-place operations.

This architecture separates client-side order interaction from the embedded robot controller.

## Key Features

### Robotic Arm Control

- Communication with Dobot Magician using UART.
- Point-to-point (PTP) movement control.
- Robotic pick-and-place operations.
- Control of the suction-based gripping mechanism.
- Command handling based on incoming sorting orders.

### Wireless Communication

- Wi-Fi communication between the client and Raspberry Pi Pico.
- TCP/IP socket-based server implementation.
- Reception and processing of client orders.
- Status and response messages for control operations.

### Automated Sorting

- Color-based sorting of red, green, and blue objects.
- Integration with IR-based object detection.
- Coordination with conveyor operation.
- Placement of matching objects in predefined positions.
- Handling of objects that do not match the requested order.

### Embedded Programming

- MicroPython development using Thonny IDE.
- UART communication and serial command packets.
- GPIO-based peripheral interaction.
- Network communication using sockets.
- Integration and testing of multiple hardware components.

## Hardware Components

| Hardware | Function |
|---|---|
| Raspberry Pi Pico | Embedded controller and communication server |
| Dobot Magician | Robotic arm for pick-and-place operations |
| Conveyor Belt | Object transportation |
| Color Sensor | Identification of object colors |
| IR Sensors | Detection of object positions |
| Suction Cup | Object gripping and lifting |
| PLC | Control and coordination within the larger automation system |

## My Technical Contributions

The work focused on the embedded control and robotic integration aspects of the system, particularly:

- Integration of Raspberry Pi Pico and Dobot Magician.
- UART communication setup and command handling.
- Development of robotic movement sequences.
- Implementation of TCP/IP-based communication.
- Coordination of sorting commands and robot actions.
- Hardware and communication testing.
- Integration activities involving the client and embedded control subsystems.

The complete system was developed collaboratively, with other project members contributing to the web/database, client interface, and PLC components.

## Development and Testing

The system was developed incrementally, starting with individual component tests before integration.

Testing activities documented in the project report included:

- UART communication and checksum verification.
- Wi-Fi connectivity and TCP/IP messaging.
- Robotic movement and suction control.
- Color detection and IR sensor tests.
- Conveyor operation.
- Integrated sorting and pick-and-place testing.

The report records 58 successful object placements out of 60 attempts, corresponding to approximately 96.7% in that test set.

## Engineering Challenges

### Communication Reliability

Establishing communication between the Raspberry Pi Pico and Dobot Magician required configuration and testing of UART parameters and command formats.

### Hardware Integration

Coordinating the robot, sensors, and conveyor required iterative testing and troubleshooting.

### Robot Positioning

Predefined movement coordinates introduced limitations in placement precision. Dynamic position feedback could improve future performance.

### Network Coordination

The system required reliable exchange of commands between the client application and the embedded controller.

## Development Environment

- **Programming:** MicroPython
- **IDE:** Thonny
- **Microcontroller:** Raspberry Pi Pico
- **Robot:** Dobot Magician
- **Communication:** UART, Wi-Fi, TCP/IP
- **Testing:** DobotStudio, serial output, oscilloscope and hardware integration tests

## Repository Scope

This repository documents the available embedded software and associated development work.

The complete original system included additional web, database, GUI, and PLC components developed collaboratively. Not all of those components are included in this repository.

## Future Improvements

- Add robot position feedback.
- Improve handling of communication errors.
- Introduce dynamic position adjustment.
- Extend automated testing.
- Improve modularity and documentation.
- Strengthen coordination between system components.

## Acknowledgements

Developed as part of a collaborative engineering project at Halmstad University.

The project involved contributions from team members across the web, client, embedded server, robotic control, and PLC subsystems.
