from machine import UART
from lib.robot import Dobot
import time
from ControlValues import PTPMode

TX_PIN = 0
RX_PIN = 1
PORT_GP2 = 2  # Port for the color sensor
PORT_GP4 = 4  # Port for the IR sensor

# Define positions
home_position = (200.0074, 20.02575, 24.92751, 4.007095)
ir_switch_position = (271.2592, -3.383661, 18.70638, -0.7146647)
color_sensor_position = (164.214, -214.3491, 39.92078, -52.54408)
place_positions = {
    "red": (-232.1845, -145.9983, 22.97639, -147.8382),
    "green": (-228.09, -63.0786, 25.4454, -164.5411),
    "blue":(-225.2229, 24.54881, 26.05589, -186.2206),
    "trash": (-58.58149, -242.5288, 40.07163, -103.5794)
}

# Initialize Dobot instance
dobot = Dobot(tx=TX_PIN, rx=RX_PIN)
if not dobot.connected():
    print("Dobot not connected")
    exit()

def startBand():
    while True:
        dobot.conveyor_belt(speed=0.5, direction = 1)
    time.sleep(1)
    
def stopBand():
    print("Starting conveyor belt monitoring with IR sensor...")
    dobot.set_ir(enable=True, port=PORT_GP4)  # Aktivera IR-sensorn

    while True:
        sensor_value = dobot.get_ir(port=PORT_GP4)  # Läs sensordata
        if sensor_value == 1:
            # Objekt detekterat: stoppa bandet
            dobot.conveyor_belt(speed=0.0)
        else:
            # Ingen detektion: kör bandet
            dobot.conveyor_belt(speed=0.5, direction=1)
            print("Conveyor belt is running...")

        time.sleep(0.1)  # Liten fördröjning för att minska processorbelastning
    
def activateColor():
# Activate color sensor and detect the color of the object
        dobot.set_color(enable = True)
        while True:
            color = dobot.get_color(port=PORT_GP2, version=0x1)
            if color == [1, 0, 0]:  # Red detected
                print("Red color detected. Moving to Place 1.")
                dobot._set_ptp_cmd(x=place_position[0], y=place_position[1], z=place_position[2], r=place_position[3], mode=PTPMode.JUMP_XYZ, wait=True)
#                 dobot.suck(enable=False)
            elif color == [0, 1, 0]:  # Green detected
                print("Green color detected. Moving to Place 2.")
                dobot._set_ptp_cmd(x=place_position[0], y=place_position[1], z=place_position[2], r=place_position[3], mode=PTPMode.JUMP_XYZ, wait=True)
#                 dobot.suck(enable=False)
            elif color == [0, 0, 1]:  # Blue detected
                print("Blue color detected. Moving to Place 3.")
                dobot._set_ptp_cmd(x=place_position[0], y=place_position[1], z=place_position[2], r=place_position[3], mode=PTPMode.JUMP_XYZ, wait=True)
#                 dobot.suck(enable=False)
            else:
                print("No valid color detected. Moving to trash position.")
                dobot._set_ptp_cmd(x=place_position[0], y=place_position[1], z=place_position[2], r=place_position[3], mode=PTPMode.JUMP_XYZ, wait=True)
#                 dobot.suck(enable=False)
                time.sleep(1)  # Wait to ensure the object is placed    
            
            dobot.set_color(enable=False)
            dobot.suck(enable=False)
            


def main():
#     startBand()
#     print("Starting conveyor belt monitoring with IR sensor...")
#     dobot.set_ir(enable=True, port=PORT_GP4)  # Aktivera IR-sensorn
#     try:
    print("Starting conveyor belt monitoring with IR sensor...")
    dobot.set_ir(enable=True, port=PORT_GP4)  # Aktivera IR-sensorn

    while True:
        sensor_value = dobot.get_ir(port=PORT_GP4)  # Läs sensordata
        if sensor_value == 1:
            # Objekt detekterat: stoppa bandet
            dobot.conveyor_belt(speed=0.0)
            while True:
                dobot.go(x=-39.70616, y=264.1018, z=17.54504, r=0)
            print("IR sensor detected an object. Conveyor belt stopped.")
        else:
            # Ingen detektion: kör bandet
            dobot.conveyor_belt(speed=0.5, direction=1)
            print("Conveyor belt is running...")

        time.sleep(0.1)  # Liten fördröjning för att minska processorbelastning
#     while True:
#         sensor_value = dobot.get_ir(port=PORT_GP4)  # Läs sensordata
#         if sensor_value == 1:
#             # Objekt detekterat: stoppa bandet
#             dobot.conveyor_belt(speed=0.0)
#             while True:
#                activateColor()
#                time.sleep(2)
#         else:
#             # Ingen detektion: kör bandet
#             dobot.conveyor_belt(speed=0.5, direction=1)
#             print("Conveyor belt is running...")
#  

if __name__ == "__main__":
    main()

