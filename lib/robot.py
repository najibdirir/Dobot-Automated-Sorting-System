from machine import UART, Pin
import struct
import time

from lib.mesage import Message
import math
from ControlValues import PTPMode
from ControlValues import CommunicationProtocolIDs
from ControlValues import ControlValues
# from ControlValues import Circle
# Anpassad DobotException
class DobotException(Exception):
    pass
PORT_GP1 = 0x00
PORT_GP2 = 0x01
PORT_GP4 = 0x02
PORT_GP5 = 0x03
STEP_PER_CIRCLE = 360.0 / 1.8 * 10.0 * 16.0
MM_PER_CIRCLE = 3.1415926535898 * 36.0
class Dobot:

    def __init__(self, tx, rx, baudrate=115200, verbose=False):
        """Initialiserar UART för seriell kommunikation med Dobot."""
        self.verbose = verbose
        # Initiera UART med specifika TX och RX pins
        self.uart  = UART(0, baudrate=115200, tx=0, rx=1)
        self.uart.init(bits=8, parity=None, stop=1)
        self.lock = False  # Flaggbaserad låsmekanism
        if self.verbose:
            print("UART initialized.")


        self._set_queued_cmd_start_exec()
        self._set_queued_cmd_clear()
        self._set_ptp_joint_params(200, 200, 200, 200, 200, 200, 200, 200)
        self._set_ptp_coordinate_params(velocity=200, acceleration=200)
        self._set_ptp_jump_params(10, 200)
        self._set_ptp_common_params(velocity=100, acceleration=100)
        self._get_pose()
        
    def connected(self):
        return True
    
    def start(self):
        print("[DOBOT] start() kallas...")
        self._running = True
        return True
    def start(self):
        print("[DOBOT] stop() kallas...")
        self._running = False
        return True
        

    def acquire_lock(self):
        while self.lock:
            time.sleep(0.01)  # Vänta på att låset frigörs
        self.lock = True

    def release_lock(self):
        self.lock = False
        
    def _read_message(self):
            time.sleep(0.1)  # Ge UART lite tid att ta emot data
            b = self.uart.read()  # Läs inkommande data
            if b:  # Kontrollera att data faktiskt mottogs
                msg = Message(b)
                if self.verbose:
                    print("myDobot: <<", msg)
                return msg
            return None  # Returnera None om ingen data mottogs
        
    def _send_command(self, msg, wait=False):
        self.acquire_lock()
        self._send_message(msg)
        response = self._read_message()
        self.release_lock()
        if not wait:
            return response
        expected_idx = struct.unpack_from('L', response.params, 0)[0]
        if self.verbose:
            print('myDobot: waiting for command', expected_idx)
        while True:
            current_idx = self._get_queued_cmd_current_index()
            if current_idx != expected_idx:
                time.sleep(0.1)
                continue
            if self.verbose:
                print('myDobot: command %d executed' % current_idx)
            break
        return response

    def _send_message(self, msg):
        time.sleep(0.1)  # Ge UART lite tid
        if self.verbose:
            print("myDobot: >>", msg)
        try:
            self.uart.write(msg.bytes())  # Skicka data via UART
        except Exception as e:
            if self.verbose:
                print(f"myDobot: Failed to send message: {e}")

    """ Gets the current command index"""
    def _get_queued_cmd_current_index(self):
        msg = Message()
        msg.id = CommunicationProtocolIDs.GET_QUEUED_CMD_CURRENT_INDEX
        response = self._send_command(msg)
        idx = struct.unpack_from('L', response.params, 0)[0]
        print(f":  din nu kö: {idx}")
        return idx
    
    """Gets the real-time pose of the Dobot"""
    def _get_pose(self):
        msg = Message()
        msg.id = CommunicationProtocolIDs.GET_POSE
        response = self._send_command(msg)
        self.x = struct.unpack_from('f', response.params, 0)[0]
        self.y = struct.unpack_from('f', response.params, 4)[0]
        self.z = struct.unpack_from('f', response.params, 8)[0]
        self.r = struct.unpack_from('f', response.params, 12)[0]
        self.j1 = struct.unpack_from('f', response.params, 16)[0]
        self.j2 = struct.unpack_from('f', response.params, 20)[0]
        self.j3 = struct.unpack_from('f', response.params, 24)[0]
        self.j4 = struct.unpack_from('f', response.params, 28)[0]

        if self.verbose:
            print("myDobot: x:%03.1f \
                            y:%03.1f \
                            z:%03.1f \
                            r:%03.1f \
                            j1:%03.1f \
                            j2:%03.1f \
                            j3:%03.1f \
                            j4:%03.1f" %
                  (self.x, self.y, self.z, self.r, self.j1, self.j2, self.j3, self.j4))
        return response

    """Making Dobot Home"""
    def _set_home_cmd(self, x=200,y=10,z=50):
        msg = Message()
        msg.id =CommunicationProtocolIDs.SET_HOME_CMD
        msg.ctrl = ControlValues.THREE
        msg.params = bytearray(bytes([0x01]))
        msg.params.extend(bytearray(struct.pack('f', x)))
        msg.params.extend(bytearray(struct.pack('f', y)))
        msg.params.extend(bytearray(struct.pack('f', z)))
        msg.params.append(0x00)
        return self._send_command(msg)

    """Executes the CP Command"""
    def _set_cp_cmd(self, x, y, z):
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_CP_CMD
        msg.ctrl = ControlValues.THREE
        msg.params = bytearray(bytes([0x01]))
        msg.params.extend(bytearray(struct.pack('f', x)))
        msg.params.extend(bytearray(struct.pack('f', y)))
        msg.params.extend(bytearray(struct.pack('f', z)))
        msg.params.append(0x00)
        return self._send_command(msg)

    """Sets the status of the gripper"""
    def _set_end_effector_gripper(self, enable=False):
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_GET_END_EFFECTOR_GRIPPER
        msg.ctrl = ControlValues.THREE
        msg.params = bytearray([])
        msg.params.extend(bytearray([0x01]))
        if enable is True:
            msg.params.extend(bytearray([0x01]))
        else:
            msg.params.extend(bytearray([0x00]))
        return self._send_command(msg)

    """Sets the status of the suction cup"""
    def _set_end_effector_suction_cup(self, enable=False):
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_GET_END_EFFECTOR_SUCTION_CUP
        msg.ctrl = ControlValues.THREE
        msg.params = bytearray([])
        msg.params.extend(bytearray([0x01]))
        if enable is True:
            msg.params.extend(bytearray([0x01]))
        else:
            msg.params.extend(bytearray([0x00]))
        return self._send_command(msg)

    """Sets the velocity ratio and the acceleration ratio in PTP mode"""
    def _set_ptp_joint_params(self, v_x, v_y, v_z, v_r, a_x, a_y, a_z, a_r):
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_GET_PTP_JOINT_PARAMS
        msg.ctrl = ControlValues.THREE
        msg.params = bytearray([])
        msg.params.extend(bytearray(struct.pack('f', v_x)))
        msg.params.extend(bytearray(struct.pack('f', v_y)))
        msg.params.extend(bytearray(struct.pack('f', v_z)))
        msg.params.extend(bytearray(struct.pack('f', v_r)))
        msg.params.extend(bytearray(struct.pack('f', a_x)))
        msg.params.extend(bytearray(struct.pack('f', a_y)))
        msg.params.extend(bytearray(struct.pack('f', a_z)))
        msg.params.extend(bytearray(struct.pack('f', a_r)))
        return self._send_command(msg)

    """Sets the velocity and acceleration of the Cartesian coordinate axes in PTP mode"""
    def _set_ptp_coordinate_params(self, velocity, acceleration):
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_GET_PTP_COORDINATE_PARAMS
        msg.ctrl = ControlValues.THREE
        msg.params = bytearray([])
        msg.params.extend(bytearray(struct.pack('f', velocity)))
        msg.params.extend(bytearray(struct.pack('f', velocity)))
        msg.params.extend(bytearray(struct.pack('f', acceleration)))
        msg.params.extend(bytearray(struct.pack('f', acceleration)))
        return self._send_command(msg)

    """Sets the lifting height and the maximum lifting height in JUMP mode"""
    def _set_ptp_jump_params(self, jump, limit):
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_GET_PTP_JUMP_PARAMS
        msg.ctrl = ControlValues.THREE
        msg.params = bytearray([])
        msg.params.extend(bytearray(struct.pack('f', jump)))
        msg.params.extend(bytearray(struct.pack('f', limit)))
        return self._send_command(msg)

    """Sets the velocity ratio, acceleration ratio in PTP mode"""
    def _set_ptp_common_params(self, velocity, acceleration):
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_GET_PTP_COMMON_PARAMS
        msg.ctrl = ControlValues.THREE
        msg.params = bytearray([])
        msg.params.extend(bytearray(struct.pack('f', velocity)))
        msg.params.extend(bytearray(struct.pack('f', acceleration)))
        return self._send_command(msg)

    """Executes PTP command"""
    def _set_ptp_cmd(self, x, y, z, r, mode, wait):
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_PTP_CMD
        msg.ctrl = ControlValues.THREE
        msg.params = bytearray([])
        msg.params.extend(bytearray([mode]))
        msg.params.extend(bytearray(struct.pack('f', x)))
        msg.params.extend(bytearray(struct.pack('f', y)))
        msg.params.extend(bytearray(struct.pack('f', z)))
        msg.params.extend(bytearray(struct.pack('f', r)))
        return self._send_command(msg, wait)

    """Clears command queue"""
    def _set_queued_cmd_clear(self):
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_QUEUED_CMD_CLEAR
        msg.ctrl = ControlValues.ONE
        return self._send_command(msg)

    """Start command"""
    def _set_queued_cmd_start_exec(self):
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_QUEUED_CMD_START_EXEC
        msg.ctrl = ControlValues.ONE
        return self._send_command(msg)

    """Wait command"""
    def _set_wait_cmd(self, ms):
        msg = Message()
        msg.id = 110
        msg.ctrl = 0x03
        msg.params = bytearray(struct.pack('I', ms))
        return self._send_command(msg)

    """Stop command"""
    def _set_queued_cmd_stop_exec(self):
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_QUEUED_CMD_STOP_EXEC
        msg.ctrl = ControlValues.ONE
        return self._send_command(msg)

    def _get_eio_level(self, address):
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_GET_EIO
        msg.ctrl = ControlValues.ZERO
        msg.params = bytearray([])
        msg.params.extend(bytearray([address]))
        return self._send_command(msg)

    def _set_eio_level(self, address, level):
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_GET_EIO
        msg.ctrl = ControlValues.ONE
        msg.params = bytearray([])
        msg.params.extend(bytearray([address]))
        msg.params.extend(bytearray([level]))
        return self._send_command(msg)

    def get_eio(self, addr):
        return self._get_eio_level(addr)

    def set_eio(self, addr, val):
        return self._set_eio_level(addr, val)

    def close(self):
        self._on = False
        self.lock.acquire()
        self.uart.close()
        if self.verbose:
            print('myDobot: %s closed' % self.uart.name)
        self.lock.release()

    def go(self, x, y, z, r=0.):
#         warnings.warn('go() is deprecated, use move_to() instead')
        self.move_to(x, y, z, r)

    def move_to(self, x, y, z, r, wait=False):
        self._set_ptp_cmd(x, y, z, r, mode=PTPMode.MOVL_XYZ, wait=wait)

    def suck(self, enable):
        self._set_end_effector_suction_cup(enable)

    def grip(self, enable):
        self._set_end_effector_gripper(enable)

    def speed(self, velocity=100., acceleration=100.):
        self._set_ptp_common_params(velocity, acceleration)
        self._set_ptp_coordinate_params(velocity, acceleration)
        

    def wait(self, ms):
        self._set_wait_cmd(ms)

    def pose(self):
        response = self._get_pose()
        x = struct.unpack_from('f', response.params, 0)[0]
        y = struct.unpack_from('f', response.params, 4)[0]
        z = struct.unpack_from('f', response.params, 8)[0]
        r = struct.unpack_from('f', response.params, 12)[0]
        j1 = struct.unpack_from('f', response.params, 16)[0]
        j2 = struct.unpack_from('f', response.params, 20)[0]
        j3 = struct.unpack_from('f', response.params, 24)[0]
        j4 = struct.unpack_from('f', response.params, 28)[0]
        return x, y, z, r, j1, j2, j3, j4
    

    def conveyor_belt(self, speed, direction=1, interface=0):
        if 0.0 <= speed <= 1.0 and (direction == 1 or direction == -1):
            motor_speed = int(50 * speed * STEP_PER_CIRCLE / MM_PER_CIRCLE * direction)
            self._set_stepper_motor(motor_speed, interface)
        else:
            raise DobotException("Wrong Parameter")

    def _set_stepper_motor(self, speed, interface=0, motor_control=True):
        msg = Message()
        msg.id = 0x87
        msg.ctrl = 0x03
        msg.params = bytearray([])
        if interface == 1:
            msg.params.extend(bytearray([0x01]))
        else:
            msg.params.extend(bytearray([0x00]))
        msg.params.extend(bytearray([0x01 if motor_control else 0x00]))
        msg.params.extend(bytearray(struct.pack('i', speed)))
        return self._send_command(msg)

    def conveyor_belt_distance(self, speed_mm_per_sec, distance_mm, direction=1, interface=0):
        if speed_mm_per_sec > 100:
            raise DobotException("Speed must be <= 100 mm/s")

        MM_PER_REV = 34 * math.pi  # Justera detta om det behÃ¶vs
        STEP_ANGLE_DEG = 1.8
        STEPS_PER_REV = 360.0 / STEP_ANGLE_DEG * 10.0 * 16.0 / 2.0
        distance_steps = distance_mm / MM_PER_REV * STEPS_PER_REV
        speed_steps_per_sec = speed_mm_per_sec / MM_PER_REV * STEPS_PER_REV * direction
        return self._send_command(self._set_stepper_motor_distance(int(speed_steps_per_sec), int(distance_steps), interface))

    def _set_stepper_motor_distance(self, speed, distance, interface=0, motor_control=True):
        msg = Message()
        msg.id = 0x88
        msg.ctrl = 0x03
        msg.params = bytearray([])
        if interface == 1:
            msg.params.extend(bytearray([0x01]))
        else:
            msg.params.extend(bytearray([0x00]))
        msg.params.extend(bytearray([0x01 if motor_control else 0x00]))
        msg.params.extend(bytearray(struct.pack('i', speed)))
        msg.params.extend(bytearray(struct.pack('I', distance)))
        return self._send_command(msg)

    def set_color(self, enable=True, port=PORT_GP2, version=0x1):
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_GET_ColorSensor # 137
        msg.ctrl = ControlValues.THREE # 0x03
        msg.params = bytearray([int(enable), port, version])
#         print(f"Set Color Params: {msg.params}")  # Debugging
        return self._send_command(msg)
#         return self._extract_cmd_index(self._send_command(msg))

    def get_color(self, port=PORT_GP2, version=0x1):
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_GET_ColorSensor #137
        msg.ctrl = ControlValues.ZERO # 0x00
        msg.params = bytearray([port, version])
        response = self._send_command(msg)
#         print(f"Raw Response: {response.params}")
#         if respons.params and len(respons.params) >= 3:
        r = struct.unpack_from('B', response.params, 0)[0]
        g = struct.unpack_from('B', response.params, 1)[0]
        b = struct.unpack_from('B', response.params, 2)[0]
        return [r, g, b]
    


    def set_ir(self, enable=True, port=PORT_GP4):
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_GET_IRSwitch  # 138
        msg.ctrl = ControlValues.THREE  # 0x03
        msg.params = bytearray([int(enable), port])
#         print(f"[DEBUG] Sending IR enable command: {msg.params}")  # Debug
        return self._send_command(msg)


    def get_ir(self, port=PORT_GP4):
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_GET_IRSwitch  # 138
        msg.ctrl = ControlValues.ZERO  # 0x00
        msg.params = bytearray([port])  # Lägg till version
        response = self._send_command(msg)
        
#         print(f"[DEBUG] Full Response: {response}")
        if len(response.params) > 0:
            state = struct.unpack_from('B', response.params, 0)[0]
            return state
        else:
#             print("[ERROR] Invalid response")
            return None

    
#     def set_ir(self, enable=True, port=PORT_GP4):
#         msg = Message()
#         msg.id = CommunicationProtocolIDs.SET_GET_IRSwitch #138
#         msg.ctrl = ControlValues.TWO # 0x02
#         msg.params = bytearray([int(enable), port])
#         return self._send_command(msg)
# 
#     def get_ir(self, port=PORT_GP4):
#         msg = Message()
#         msg.id = CommunicationProtocolIDs.SET_GET_IRSwitch #138
#         msg.ctrl = ControlValues.ZERO # 0x00
#         msg.params = bytearray([port])
#         response = self._send_command(msg)
#         state = struct.unpack_from('B', response.params, 0)[0]
#         return state