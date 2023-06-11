import ssl
import socket
import json

BUFF_SIZE = 1024

def open_connection(hostname, port, chain_file):
    try:
        context = ssl.create_default_context()
        context.load_verify_locations(chain_file)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            global ssock 
            ssock = context.wrap_socket(sock, server_hostname=hostname)
            ssock.connect((hostname, port))

            return True
    except:
        return False


def send_dict(dict_data):
    dict_data = json.dumps(dict_data)
    ssock.sendall(bytes(dict_data, encoding="utf-8"))

def receive_dict():
    data = ssock.recv(BUFF_SIZE)
    data = data.decode("utf-8")
    data = json.loads(data)

    return data


def close_connection():
    ssock.close()
