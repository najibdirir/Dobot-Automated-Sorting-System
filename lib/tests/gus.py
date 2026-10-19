from machine import UART
from lib.robot import Dobot
import time
from ControlValues import PTPMode

TX_PIN = 0
RX_PIN = 1
PORT_GP1 = 0x00
PORT_GP2 = 0x01
PORT_GP4 = 0x02
PORT_GP5 = 0x03

# Skapa Dobot-instans
robot = Dobot(tx=TX_PIN, rx=RX_PIN)

# Kontrollera om bot är ansluten
print('Robot status:', 'connected' if robot.connected() else 'not connected')

def Startband():
    try:
        while True:
            print("Starting conveyor belt...")
            robot.conveyor_belt(speed=1.0, direction=1)  # Test med standardvärden
            robot.conveyor_belt_distance(speed_mm_per_sec=50, distance_mm=100, direction=1)
            time.sleep(1)
    except Exception as e:
        print(f"Error during conveyor belt test: {e}")

def Stopband():
    try:
        print("Starting conveyor belt monitoring with IR sensor...")
        robot.set_ir(enable=True, port=PORT_GP4)  # Aktivera IR-sensorn
        while True:
            sensor_value = robot.get_ir(port=PORT_GP4)  # Läs sensordata från IR-sensorn
            if sensor_value == 1:
                # Objekt detekterat: stoppa transportbandet
                print("IR sensor detected an object. Stopping conveyor belt...")
                robot.conveyor_belt(speed=0.0)  # Stoppar bandet
                time.sleep(1)  # Vänta lite innan nästa läsning
            else:
                # Ingen detektion: starta transportbandet
                print("No object detected. Conveyor belt running...")
                robot.conveyor_belt(speed=0.5, direction=1)  # Kör bandet
            time.sleep(0.1)  # Liten fördröjning för att minska processorbelastning
    except Exception as e:
        print(f"Error during conveyor belt monitoring: {e}")
    finally:
        # Stäng av IR-sensorn när funktionen avslutas
        robot.set_ir(enable=False, port=PORT_GP4)
        print("IR sensor disabled. Conveyor belt monitoring stopped.")


def test_Color_sensor():
    # Fördefinierade positioner
    color_sensor_position = (195.4795, 184.0777, 37.3494, 41.56878)
    place_position = (264.7272, -42.93243, 44.67304, -10.9224)  # Enskild plats
    ir_switch_position = (-30.09021, 266.9014, 16.12678, 94.72172)

    try:
        # Loopa kontinuerligt
        while True:
            # Flytta till IR-switchposition och plocka objekt
            print("Moving to IR switch position...")
            robot._set_ptp_cmd(x=ir_switch_position[0], y=ir_switch_position[1], z=ir_switch_position[2], r=ir_switch_position[3], mode=PTPMode.JUMP_XYZ, wait=True)
            robot.suck(enable=True)
            print("Object picked.")

            # Flytta till färgsensorn
            print("Moving to color sensor position...")
            robot._set_ptp_cmd(x=color_sensor_position[0], y=color_sensor_position[1], z=color_sensor_position[2], r=color_sensor_position[3], mode=PTPMode.JUMP_XYZ, wait=True)
            time.sleep(1)

            # Aktivera färgsensorn och få färgdata
            print("Activating color sensor...")
            robot.set_color(enable=True)
            time.sleep(0.5)  # Ge sensorn tid att stabilisera

            EMPTY_SENSOR_VALUES = [0, 0, 0]
            color = robot.get_color(port=PORT_GP2, version=0x1)

            if color == EMPTY_SENSOR_VALUES:
                print("No object detected. Moving to trash position.")
            else:
                print(f"Detected color: R={color[0]}, G={color[1]}, B={color[2]}")

            # Flytta till placeringsposition och släpp objekt
            print("Moving to place position...")
            robot._set_ptp_cmd(x=place_position[0], y=place_position[1], z=place_position[2], r=place_position[3], mode=PTPMode.JUMP_XYZ, wait=True)
            robot.suck(enable=False)
            print("Object placed.")

            # Stäng av färgsensorn
            robot.set_color(enable=False)

            # Kort paus mellan iterationer
            time.sleep(1)

    except KeyboardInterrupt:
        print("Process interrupted by user. Stopping robot...")
        robot.suck(enable=False)
        robot.set_color(enable=False)
    except Exception as e:
        print(f"Error during color sensor test: {e}")

def conveyor_and_positioning():
    # Fördefinierade positioner
    color_sensor_position = (187.5455, 198.9772 ,36.794 ,44.98348)
#     place_position = (264.7272, -42.93243, 44.67304, -10.9224)  # Enskild plats
    ir_switch_position = (-46.53043, 240.8973 ,15.95725 ,99.22173 )
    place_positions = {
    "red": ( -90.33964, -252.3899 ,23.48224 ,-111.4048),
    "green": ( -8.424411, -246.3143 ,29.41533 ,-93.66946),
    "blue": (72.90192, -241.329 ,36.89011 ,-74.90181),
    "trash": (234.8106, -53.96931 ,45.74065 ,-14.65475)
}

    try:
        print("Starting conveyor belt monitoring and positioning system...")
        robot.set_ir(enable=True, port=PORT_GP4)  # Aktivera IR-sensorn
        while True:
            # Övervaka IR-sensorn
            sensor_value = robot.get_ir(port=PORT_GP4)  # Läs sensordata från IR-sensorn
            if sensor_value == 1:
                # Objekt detekterat: stoppa transportbandet
                print("IR sensor detected an object. Stopping conveyor belt...")
                robot.conveyor_belt(speed=0.0)  # Stoppar bandet
                time.sleep(1)  # Vänta lite innan nästa operation

                # Flytta till IR-switchposition och plocka objekt
                print("Moving to IR switch position...")
                robot._set_ptp_cmd(x=ir_switch_position[0], y=ir_switch_position[1], z=ir_switch_position[2], r=ir_switch_position[3], mode=PTPMode.JUMP_XYZ, wait=True)
                robot.suck(enable=True)
                print("Object picked.")

                # Flytta till färgsensorn
                print("Moving to color sensor position...")
                robot._set_ptp_cmd(x=color_sensor_position[0], y=color_sensor_position[1], z=color_sensor_position[2], r=color_sensor_position[3], mode=PTPMode.JUMP_XYZ, wait=True)
                time.sleep(1)

                # Aktivera färgsensorn och få färgdata
                print("Activating color sensor...")
                robot.set_color(enable=True)
                time.sleep(0.5)  # Ge sensorn tid att stabilisera

                EMPTY_SENSOR_VALUES = [0, 0, 0]
                color = robot.get_color(port=PORT_GP2, version=0x1)

                # Avgör placering baserat på färg
                if color == EMPTY_SENSOR_VALUES:
                    print("No object detected. Moving to trash position.")
                    target_position = place_positions["trash"]
                elif color[0] > color[1] and color[0] > color[2]:  # Rött objekt
                    print("Red object detected. Moving to red position.")
                    target_position = place_positions["red"]
                elif color[1] > color[0] and color[1] > color[2]:  # Grönt objekt
                    print("Green object detected. Moving to green position.")
                    target_position = place_positions["green"]
                elif color[2] > color[0] and color[2] > color[1]:  # Blått objekt
                    print("Blue object detected. Moving to blue position.")
                    target_position = place_positions["blue"]
                else:
                    print("Unknown color detected. Moving to trash position.")
                    target_position = place_positions["trash"]

                # Flytta till den bestämda positionen och släpp objektet
                print(f"Moving to target position: {target_position}")
                robot._set_ptp_cmd(x=target_position[0], y=target_position[1], z=target_position[2], r=target_position[3], mode=PTPMode.JUMP_XYZ, wait=True)
                robot.suck(enable=False)
                print("Object placed.")


                # Stäng av färgsensorn
                robot.set_color(enable=False)

                # Starta om transportbandet
                print("Restarting conveyor belt...")
                robot.conveyor_belt(speed=0.5, direction=1)
                time.sleep(1)
            else:
                # Ingen detektion: håll transportbandet igång
                print("No object detected. Conveyor belt running...")
                robot.conveyor_belt(speed=0.5, direction=1)  # Kör bandet
                time.sleep(0.1)  # Liten fördröjning för att minska processorbelastning
    except KeyboardInterrupt:
        print("Process interrupted by user. Stopping robot...")
        robot.suck(enable=False)
        robot.set_color(enable=False)
        robot.conveyor_belt(speed=0.0)
        robot.set_ir(enable=False, port=PORT_GP4)
    except Exception as e:
        print(f"Error during conveyor and positioning process: {e}")
    finally:
        # Stäng av IR-sensorn när funktionen avslutas
        robot.set_ir(enable=False, port=PORT_GP4)
        print("IR sensor disabled. Conveyor belt and positioning system stopped.")

# Kör funktionen här
if robot.connected():
#     robot._set_home_cmd()
#     time.sleep(30)
    (x, y, z, r, j1, j2, j3, j4 )= robot.pose()
    print(f'{x}, {y} ,{z} ,{r} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')
#    conveyor_and_positioning()
else:
    print("Robot not connected. Check connections.")
