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
    Numera placeras första behövda objektet i P1, andra i P2, tredje i P3,
    och om objektet inte behövs (eller vi redan fyllt alla P1..P3) läggs det i P4 (trash).
    """
    print(f"[PROCESS] Startar bearbetning av order {order_id} med kombination {combination}")

    # Fördefinierade positioner för IR-switch och färgsensor (justera själv)
    ir_switch_position = (-26.11945, 233.6191, 13.95112, 94.66878)
    color_sensor_position = (192.3015, 187.2161, 40.88316, 42.52172)

    # P1, P2, P3 (första, andra, tredje behövda objektet), P4 (trash)
    place_positions = [
        (61.088,    -275.6851, 20.89368,  -79.21651),   # P1
        (18.42763,  -276.5861, 19.48933,  -87.89887),   # P2
        (-27.24912, -277.3195 ,23.38783 ,-97.3224 ),   # P3
        (252.3113,  3.38048,   26.79184,  -0.9429869)   # P4 (trash)
    ]

    # Räkna hur många av varje färg vi *totalt* behöver:
    # Exempel: combination="GGR" => needed = {"G":2, "R":1, "B":0}
    needed = {"R": 0, "G": 0, "B": 0}
    for c in combination:
        if c in needed:
            needed[c] += 1
        else:
            print(f"[WARN] Ogiltig färgbokstav '{c}' i ordern. Avbryter.")
            return

    print(f"[INFO] Totalt behov: {needed}")

    # Håll koll på vilken plats (P1, P2, P3) vi ska fylla härnäst
    next_position_index = 0  # 0 => P1, 1 => P2, 2 => P3
    
    # Starta IR-sensor och transportband
    robot.set_ir(enable=True, port=PORT_GP4)
    robot.conveyor_belt(speed=0.25, direction=1)

    try:
        # Exempel: Loopar tills vi antingen fyllt P1..P3 (eller tills man vill avbryta).
        # Vill du *alltid* köra vidare och lägga allt i trash efter P3, kör "while True:".
        while next_position_index < 3:  
            if robot.get_ir(port=PORT_GP4) == 1:
                print("[PROCESS] Objekt upptäckt, stoppar bandet...")
                robot.conveyor_belt(speed=0.0)
                time.sleep(1)

                # Flytta till IR-switch-position och plocka objekt
                robot._set_ptp_cmd(*ir_switch_position, mode=PTPMode.JUMP_XYZ, wait=True)
                robot.suck(enable=True)
                print("[PROCESS] Objektet plockat.")

                # Flytta till färgsensor-position
                robot._set_ptp_cmd(*color_sensor_position, mode=PTPMode.JUMP_XYZ, wait=True)
                time.sleep(1)

                # Aktivera färgsensorn och identifiera färg
                robot.set_color(enable=True)
                time.sleep(0.25)
                color = robot.get_color(port=PORT_GP2, version=0x1)
                robot.set_color(enable=False)

                # Färgidentifiering -> 'R','G','B' eller 'trash'
                letter = "trash"
                if color == [0, 0, 0]:
                    letter = "trash"
                elif color[0] > color[1] and color[0] > color[2]:
                    letter = "R"
                elif color[1] > color[0] and color[1] > color[2]:
                    letter = "G"
                elif color[2] > color[0] and color[2] > color[1]:
                    letter = "B"
                
                print(f"[INFO] Identifierad färg: {letter}")

                # Om vi fortfarande BEHÖVER den färgen -> lägg i P1..P3
                # Annars -> P4 (trash)
                if letter in needed and needed[letter] > 0:
                    # Vi använder "nästa lediga position" => next_position_index
                    target_position = place_positions[next_position_index]
                    needed[letter] -= 1
                    print(f"[INFO] Färgen '{letter}' behövs. Lägger i P{next_position_index+1}.")
                    next_position_index += 1
                else:
                    # Antingen behövs inte färgen, eller vi har redan fyllt kvoten
                    target_position = place_positions[3]  # P4
                    print(f"[INFO] Färgen '{letter}' behövs inte längre / okänd. Lägger i trash (P4).")

                # Flytta till vald målposition
                robot._set_ptp_cmd(*target_position, mode=PTPMode.JUMP_XYZ, wait=True)
                robot.suck(enable=False)
                print("[PROCESS] Objektet placerat.")

                # Kolla om vi redan fyllt vårt totala behov (valfritt)
                if sum(needed.values()) == 0:
                    print("[PROCESS] Alla behövda objekt är nu placerade.")
                    break

                # Starta bandet igen
                robot.conveyor_belt(speed=0.25, direction=1)
                time.sleep(1)
            else:
                # Ingen detektion just nu, håll bandet igång
                robot.conveyor_belt(speed=0.25, direction=1)
                time.sleep(0.1)
    finally:
        # Stäng av IR-sensorn och transportbandet när vi är klara
        print("[PROCESS] Avslutar - stänger av sensorer och transportband.")
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

