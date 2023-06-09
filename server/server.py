import ssl
import socket
import json

BUFF_SIZE = 1024

if __name__ == "__main__":
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

            with context.wrap_socket(conn, server_side=True) as secure_conn:
                print(f"New connection from {ip}")

                data = secure_conn.recv(BUFF_SIZE)
                data = data.decode('utf-8')
                data = json.loads(data)

                print(data["username"])

    except socket.timeout:
        pass
