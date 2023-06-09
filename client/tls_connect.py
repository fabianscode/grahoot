import ssl
import socket
import json

if __name__ == "__main__":
    hostname = "grahoot.fabianspecht.xyz"

    context = ssl.create_default_context()
    context.load_verify_locations("fullchain.pem")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            ssock.connect((hostname, 8004))

            reg = {
                "username": "Dieter",
                "pin": "94928"
            }

            data = json.dumps(reg)
            ssock.sendall(bytes(data, encoding="utf-8"))

            ssock.close()
