import ssl
import socket

hostname = "185.183.159.167"
context = ssl.create_default_context()

with socket.create_connection((hostname, 8004)) as sock:
    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
        print(ssock.version())
