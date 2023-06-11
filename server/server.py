import ssl
import socket
import json

BUFF_SIZE = 1024

def send_dict(dict_data, ssock):
    dict_data = json.dumps(dict_data)
    ssock.sendall(bytes(dict_data, encoding="utf-8"))

def receive_dict(ssock):
    data = ssock.recv(BUFF_SIZE)
    data = data.decode("utf-8")
    data = json.loads(data)

    return data


if __name__ == "__main__":
    global established_connections
    established_connections = []

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(
            certfile="/etc/letsencrypt/live/grahoot.fabianspecht.xyz/fullchain.pem",
            keyfile="/etc/letsencrypt/live/grahoot.fabianspecht.xyz/privkey.pem")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 8004))
    s.listen()

    accepting = True
    try:
        while accepting:
            conn, (ip, port) = s.accept()

            with context.wrap_socket(conn, server_side=True) as ssock:
                print(f"New connection from {ip}")

                established_connections.append(ssock)

                data = receive_dict(ssock)

                print(data["username"])

                response = {
                    "dieter": "hallo Mensch"
                }

                send_dict(response, ssock)


    except socket.timeout:
        pass
