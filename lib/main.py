# main.py
from machine import UART
from lib.test import ConnectionManager
from lib.robot import Dobot
import time

from order_data import is_valid_order  # om du vill testa lokalt

# Nätverk
# ssid = "najiib – iPhone"
# password = "Badboys3"
ssid="Dekemhare"
password = "Mehari123"
port = 7471

# Dobot-pin
TX_PIN = 0
RX_PIN = 1
PORT_GP1 = 0x00
PORT_GP2 = 0x01
PORT_GP4 = 0x02
PORT_GP5 = 0x03


def main():
    # 1) Skapa Dobot
    dobot = Dobot(tx=TX_PIN, rx=RX_PIN)
    if not dobot.connected():
        print("[FEL] Dobot not connected.")
        return

    # 2) Skapa ConnectionManager
    cm = ConnectionManager(ssid, password, port)

    # 3) Länka Dobot
    cm.dobot = dobot

    # 4) Koppla WiFi
    cm.connect_wifi()

    # 5) Starta server (blockerande)
    cm.start_server()
#     cm.conveyor_and_positioning()

if __name__ == "__main__":
    main()
