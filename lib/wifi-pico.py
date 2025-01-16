import network
import time
import socket
import ujson as json
from machine import Pin
from order_data import is_valid_order
# Om du har en riktig DobotManager-klass, importera den
# from dobot_manager import DobotManager
# Annars kan du skapa en dummy-klass nedan:
class DobotManager:
    def start(self):
        # Simulerar att Dobot startar korrekt
        print("Dobot startad (dummy)")
        return True

    def stop(self):
        # Simulerar att Dobot stoppas korrekt
        print("Dobot stoppad (dummy)")
        return True

# -------------------------
# 1) WiFi-uppgifter och funktioner
# -------------------------
SSID = "najiib - iPhone"
PASSWORD = "Badboys3"

def connect_to_wifi(ssid, password, timeout=10):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("Ansluter till WiFi...")
        wlan.connect(ssid, password)
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1

    if wlan.isconnected():
        print("WiFi ansluten:", wlan.ifconfig())
        # Returnerar IP-adressen så vi kan binda vår server mot denna
        return wlan.ifconfig()[0]
    else:
        raise Exception("Misslyckades med att ansluta till WiFi.")

# -------------------------
# 2) TCPServer-klass
# -------------------------
class TCPServer:
    def __init__(self, ip, port, dobot_manager=None):
        self.ip = ip
        self.port = port
        self.dobot_manager = dobot_manager  # Håller en referens till DobotManager (eller dummy-klass)

        # Exempel: LED för feedback (justera pinnar om behövs)
        self.led1 = Pin(15, Pin.OUT)  # LED1
        self.led2 = Pin(14, Pin.OUT)  # LED2

        # Skapa server-socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(1)
        print(f"Server körs på {self.ip}:{self.port}")

    def start(self):
        while True:
            conn, addr = self.server_socket.accept()
            print(f"Anslutning från {addr}")

            try:
                data = conn.recv(1024).decode('utf-8')
                print(f"Mottaget data: {data}")

                # Försök tolka data som JSON
                try:
                    request = json.loads(data)
                except json.JSONDecodeError:
                    response = {
                        "status": "NACK",
                        "message": "Ogiltigt JSON-format."
                    }
                    conn.send(json.dumps(response).encode("utf-8"))
                    conn.close()
                    continue

                # Hämta nycklar (fält) ur JSON
                cmd         = request.get("command")       # t.ex. "start_dobot" eller "stop_dobot"
                order_id    = request.get("order_id")      # t.ex. "001"
                combination = request.get("combination")   # t.ex. "BGR"

                # 1) Om vi har ett "command"-fält (start/stop dobot)
                if cmd:
                    response = self.handle_command(cmd, request)

                # 2) Om inget "command" finns, men "order_id" & "combination" finns => hantera beställning
                elif order_id and combination:
                    response = self.handle_order(order_id, combination, request)
                    self.led1.value(0)
                    self.led2.value(0)

                # 3) Annars -> NACK
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

    def handle_command(self, cmd, request):
        """
        Hanterar dobot-kommandon: start/stop eller okänt.
        Använder self.dobot_manager för att anropa start/stop-funktionerna.
        """
        if cmd == "start_dobot":
            # Kalla på dobot_manager.start()
            if self.dobot_manager and self.dobot_manager.start():
                self.led1.value(1)  # Tänd LED1
                return {
                    "status": "ACK",
                    "message": "Dobot startad. LED1 tänd.",
                    "timestamp": request.get("timestamp")
                }
            else:
                return {
                    "status": "NACK",
                    "message": "Dobot kunde inte startas eller dobot_manager saknas."
                }

        elif cmd == "stop_dobot":
            # Kalla på dobot_manager.stop()
            if self.dobot_manager and self.dobot_manager.stop():
                self.led2.value(1)  # Tänd LED2
                return {
                    "status": "ACK",
                    "message": "Dobot stoppad. LED2 tänd.",
                    "timestamp": request.get("timestamp")
                }
            else:
                return {
                    "status": "NACK",
                    "message": "Dobot kunde inte stoppas eller dobot_manager saknas."
                }

        else:
            # Okänt kommando
            self.led1.value(0)
            self.led2.value(0)
            return {
                "status": "NACK",
                "message": f"Okänt kommando: {cmd}"
            }

    def handle_order(self, order_id, combination, request):
        """
        Hanterar beställning genom att kolla om ordern är giltig.
        Här anropas is_valid_order från order_data.py
        """
        if is_valid_order(order_id, combination):
            return {
                "status": "ACK",
                "message": f"Order {order_id} med kombination {combination} är giltig.",
                "timestamp": request.get("timestamp")
            }
        else:
            return {
                "status": "NACK",
                "message": (f"Order {order_id} med kombination '{combination}' finns inte i Pico "
                            f"eller matchar inte förväntad kombination."),
                "timestamp": request.get("timestamp")
            }

# -------------------------
# 3) Huvudfunktion
# -------------------------
def main():
    try:
        # 1. Anslut till WiFi
        ip_address = connect_to_wifi(SSID, PASSWORD)
        
        # 2. Skapa en DobotManager-instans (eller en dummy om du saknar riktig implementation)
        dobot_manager = DobotManager()
        
        # 3. Starta TCP-servern
        port = 7471
        server = TCPServer(ip=ip_address, port=port, dobot_manager=dobot_manager)
        server.start()

    except Exception as e:
        print("Fel i main:", e)

# -------------------------
# 4) Starta programmet (om filen körs som main)
# -------------------------
if __name__ == "__main__":
    main()
