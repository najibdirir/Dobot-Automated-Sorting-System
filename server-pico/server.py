# server.py
import socket
import json

def create_server(ip, port=7471):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((ip, port))
    server_socket.listen(1)
    server_socket.setblocking(False)  # Icke-blockerande
    print(f"Server lyssnar på {ip}:{port}")
    return server_socket

def handle_incoming_connections(server_socket, color_list, order_received):
    """
    - Försök accept() en anslutning
    - Om ingen ansluter => OSError [Errno 11] EAGAIN => fånga och returnera
    - Annars ta emot data, parse ev. JSON, lagra i color_list osv.
    """
    try:
        conn, addr = server_socket.accept()
    except OSError as e:
        # Kolla om det är EAGAIN
        if hasattr(e, 'errno') and e.errno == 11:
            # Ingen anslutning just nu, returnera lugnt
            return order_received
        # Annars är det ett annat OSError som vi vill se
        raise e

    print(f"Anslutning från {addr}")
    
    # Försök läsa data
    try:
        data = conn.recv(1024)
    except OSError as e:
        if hasattr(e, 'errno') and e.errno == 11:
            # Ingen data just nu
            conn.close()
            return order_received
        else:
            raise e

    if not data:
        # Ingen data, stäng
        conn.close()
        return order_received

    # Exempel: tolka JSON
    decoded = data.decode('utf-8')
    print(f"Mottagen data: {decoded}")
    try:
        order_json = json.loads(decoded)
        # Exempel: "Colors": "RBB"
        if "Colors" in order_json:
            color_list.clear()
            for c in order_json["Colors"]:  # t.ex. "RBB" -> ['R','B','B']
                color_list.append(c)
            order_received = True
            response = '{"status": "ACK", "message": "Order mottagen"}'
        else:
            response = '{"status": "NACK", "message": "Ingen \\"Colors\\"-nyckel"}'
    except Exception as ex:
        print(f"Fel vid JSON-läsning: {ex}")
        response = '{"status":"NACK","message":"Felaktig JSON"}'

    # Svara
    conn.send(response.encode('utf-8'))
    conn.close()
    return order_received
