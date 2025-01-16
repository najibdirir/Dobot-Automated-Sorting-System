# connection_manager.py

import network
import socket
import time
import ujson as json
from order_data import is_valid_order  # Om du vill använda tabellen
from machine import UART, Pin
from lib.robot import Dobot
import time
from ControlValues import PTPMode

TX_PIN = 0
RX_PIN = 1
PORT_GP1 = 0x00
PORT_GP2 = 0x01
PORT_GP4 = 0x02
PORT_GP5 = 0x03
# Dobot-pin
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

class ConnectionManager:
    def __init__(self, ssid, password, port, dobot=None):
        self.ssid = ssid
        self.password = password
        self.port = port
        self.ip_address = None
        self.dobot = dobot  # Vi injectar Dobot utifrån
        self.current_order = None  # För att lagra den aktuella ordern

        # Initiera LED-pinnar (justera pinnumren vid behov)
        self.led1 = Pin(15, Pin.OUT)
        self.led2 = Pin(14, Pin.OUT)
        system_started = False  # Global eller instansvariabel i klassen


    def connect_wifi(self, timeout=10):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        if not wlan.isconnected():
            print("Ansluter till WiFi...")
            wlan.connect(self.ssid, self.password)
            while not wlan.isconnected() and timeout > 0:
                time.sleep(1)
                timeout -= 1
        
        if wlan.isconnected():
            self.ip_address = wlan.ifconfig()[0]
            print("WiFi ansluten:", wlan.ifconfig())
        else:
            raise Exception("Misslyckades med att ansluta till WiFi.")

    def start_server(self):
        if not self.ip_address:
            raise Exception("Saknar IP-adress, kör connect_wifi() först.")

        # Skapa och lyssna på en TCP-socket
        s = socket.socket()
        s.bind((self.ip_address, self.port))
        s.listen(1)
        print(f"Server körs på {self.ip_address}:{self.port}")
        
        while True:
            conn, addr = s.accept()
            print(f"Anslutning från {addr}")

            try:
                data = conn.recv(1024).decode('utf-8')
                print(f"Mottaget data: {data}")

                # Variabler för att separera kommando- & orderdata
                command_request = None
                order_request   = None

                # Försök tolka data som JSON
                try:
                    request = json.loads(data)
                except ValueError:
                    # MicroPython har ofta inte json.JSONDecodeError
                    response = {
                        "status": "NACK",
                        "message": "Ogiltigt JSON-format."
                    }
                    conn.send(json.dumps(response).encode("utf-8"))
                    conn.close()
                    continue

                # Hämta eventuella nycklar
                cmd         = request.get("command")       # ex: "start_dobot" eller "stop_dobot"
                order_id    = request.get("order_id")      # ex: "001"
                combination = request.get("combination")   # ex: "BGR"

                # 1) Om vi har ett "command"-fält => kommando
                if cmd:
                    command_request = request  # Här kan du spara undan kommando-data
                    response = self.handle_command(cmd, request)

                # 2) Om inget "command" men "order_id" & "combination" => order
                elif order_id and combination:
                    order_request = request  # Här kan du spara undan order-data
                    response = self.handle_order(order_id, combination, request)

                # 3) Annars => NACK
                else:
                    response = {
                        "status": "NACK",
                        "message": "Varken kommando eller giltig order-info hittades."
                    }

                # Skicka svar tillbaka
                conn.send(json.dumps(response).encode('utf-8'))

            except Exception as e:
                print(f"Fel vid bearbetning: {e}")
            finally:
                conn.close()

    def handle_order(self, order_id, combination, request):
        """
        Tar emot och lagrar ordern utan att bearbeta den direkt.
        """
        if is_valid_order(order_id, combination):
            self.current_order = {"order_id": order_id, "combination": combination}
            print(f"[INFO] Order {order_id} med kombination {combination} mottagen och sparad.")
            return {
                "status": "ACK",
                "message": f"Order {order_id} mottagen.",
                "timestamp": request.get("timestamp")
            }
        else:
            print(f"[ERROR] Ogiltig order {order_id}.")
            return {
                "status": "NACK",
                "message": f"Order {order_id} är ogiltig.",
                "timestamp": request.get("timestamp")
            }

    def handle_command(self, cmd, request):
        global system_started
        if cmd == "start_dobot":
            if self.current_order:
                system_started = True
                order_id = self.current_order["order_id"]
                combination = self.current_order["combination"]
                print(f"[INFO] Startar bearbetning av order {order_id} med kombination {combination}")
                process_orders(order_id, combination, self.dobot)
                return {
                    "status": "ACK",
                    "message": f"Bearbetning av order {order_id} påbörjad.",
                    "timestamp": request.get("timestamp")
                }
            else:
                print("[WARN] Ingen order lagrad.")
                return {
                    "status": "NACK",
                    "message": "Ingen order att bearbeta.",
                    "timestamp": request.get("timestamp")
                }
        elif cmd == "stop_dobot":
            system_started = False
            print("[INFO] Dobot stoppad.")
            return {
                "status": "ACK",
                "message": "Dobot stoppad.",
                "timestamp": request.get("timestamp")
            }
        else:
            print(f"[WARN] Okänt kommando {cmd}.")
            return {
                "status": "NACK",
                "message": f"Okänt kommando: {cmd}.",
                "timestamp": request.get("timestamp")
            }

def process_orders(order_id, combination, robot):
    """
    Hanterar orderprocessen med hjälp av Dobot.
    Använder den manuella implementeringen från conveyor_and_positioning.
    """
    print(f"[PROCESS] Startar bearbetning av order {order_id} med kombination {combination}")
    
    # Fördefinierade positioner
    ir_switch_position = (-26.11945, 233.6191 ,13.95112 ,94.66878)
    color_sensor_position = (192.3015, 187.2161 ,40.88316 ,42.52172 )
    place_positions = {
        "R": (61.088, -275.6851 ,20.89368 ,-79.21651 ),
        "G": (18.42763, -276.5861 ,19.48933 ,-87.89887),
        "B": (-29.04118, -275.8976 ,18.77997 ,-97.71946  ),
        "trash": (252.3113, 3.38048 ,26.79184 ,-0.9429869 )
    }
    
        # Fördefinierade positioner
#     color_sensor_position = (187.5455, 198.9772, 36.794, 44.98348)
#     ir_switch_position = (-46.53043, 240.8973, 15.95725, 99.22173)
#     place_positions = 
#         "R": (-90.33964, -252.3899, 23.48224, -111.4048),
#         "G": (-8.424411, -246.3143, 29.41533, -93.66946),
#         "B": (72.90192, -241.329, 36.89011, -74.90181),
#         "trash": (234.8106, -53.96931, 45.74065, -14.65475)

    # Skapa en färgbehovslista baserat på orderkombinationen
    needed = {"R": 0, "G": 0, "B": 0}
    for c in combination:
        if c in needed:
            needed[c] += 1
        else:
            print(f"[WARN] Ogiltig färgbokstav '{c}' i ordern. Avbryter.")
            return

    print(f"[INFO] Vi behöver följande färger: {needed}")

    # Starta IR-sensor och transportband
    robot.set_ir(enable=True, port=PORT_GP4)
    robot.conveyor_belt(speed=0.25, direction=1)

    try:
        while sum(needed.values()) > 0:
            # Kontrollera IR-sensorn för att detektera objekt
            if robot.get_ir(port=PORT_GP4) == 1:
                print("[PROCESS] Objekt upptäckt, stoppar bandet...")
                robot.conveyor_belt(speed=0.0)
                time.sleep(1)

                # Flytta till IR-switch-position och plocka objekt
                print("[DEBUG] Flyttar till IR-switch-position...")
                robot._set_ptp_cmd(*ir_switch_position, mode=PTPMode.JUMP_XYZ, wait=True)
                robot.suck(enable=True)
                print("[PROCESS] Objektet plockat.")

                # Flytta till färgsensorn
                print("[DEBUG] Flyttar till färgsensor-position...")
                robot._set_ptp_cmd(*color_sensor_position, mode=PTPMode.JUMP_XYZ, wait=True)
                time.sleep(1)

                # Aktivera färgsensorn och identifiera färg
                print("[DEBUG] Aktiverar färgsensorn...")
                robot.set_color(enable=True)
                time.sleep(0.25)
                color = robot.get_color(port=PORT_GP2, version=0x1)
                robot.set_color(enable=False)

                # Färgidentifiering
                if color == [0, 0, 0]:  # Om ingen färg identifieras
                    print("[WARN] Ingen färg identifierad. Flyttar till trash.")
                    target_position = place_positions["trash"]
                elif color[0] > color[1] and color[0] > color[2]:  # Rött objekt
                    print("[INFO] Identifierad färg: Rött.")
                    letter = "R"
                elif color[1] > color[0] and color[1] > color[2]:  # Grönt objekt
                    print("[INFO] Identifierad färg: Grönt.")
                    letter = "G"
                elif color[2] > color[0] and color[2] > color[1]:  # Blått objekt
                    print("[INFO] Identifierad färg: Blått.")
                    letter = "B"
                else:  # Okänd färg
                    print("[WARN] Okänd färg identifierad. Flyttar till trash.")
                    letter = "trash"

                # Bestäm placering baserat på identifierad färg
                if letter in needed and needed[letter] > 0:
                    needed[letter] -= 1
                    target_position = place_positions[letter]
                    print(f"[INFO] Färgen '{letter}' behövs. Återstående behov: {needed}")
                else:
                    target_position = place_positions["trash"]
                    print("[WARN] Färgen behövs inte längre eller är okänd. Flyttar till trash.")

                # Flytta till målet och placera objektet
                print(f"[DEBUG] Flyttar till målposition: {target_position}")
                robot._set_ptp_cmd(*target_position, mode=PTPMode.JUMP_XYZ, wait=True)
                robot.suck(enable=False)
                print("[PROCESS] Objektet placerat.")

                # Starta transportbandet igen
                robot.conveyor_belt(speed=0.25, direction=1)
                time.sleep(1)
            else:
                # Ingen detektion: håll transportbandet igång
                print("[DEBUG] Inget objekt upptäckt. Transportbandet körs...")
                robot.conveyor_belt(speed=0.25, direction=1)
                time.sleep(0.1)
    finally:
        # Stäng av IR-sensorn och transportbandet
        print("[PROCESS] Stänger av sensorer och transportband.")
        robot.suck(enable=False)
        robot.set_ir(enable=False, port=PORT_GP4)
        robot.conveyor_belt(speed=0.0)


def rgb_to_letter(self, r, g, b):
    """
    Mycket enkel metod för att avgöra dominanta färgkanalen.
    Returnerar 'R','G','B' eller '?' om oklart.
    """
    if (r > g) and (r > b):
        return 'R'
    elif (g > r) and (g > b):
        return 'G'
    elif (b > r) and (b > g):
        return 'B'
    else:
        return '?'
