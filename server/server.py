import ssl
import queue
import random
import sys
import socket
import json
import threading


BUFF_SIZE = 1024


def send_dict(dict_data, ssock):
    dict_data = json.dumps(dict_data)
    ssock.sendall(bytes(dict_data, encoding="utf-8"))


def receive_dict(ssock):
    data = ssock.recv(BUFF_SIZE)
    data = data.decode("utf-8")
    data = json.loads(data)

    return data


def accept_registrations(communication_queue, game_pin):
    while True:
        conn, (ip, port) = s.accept()

        # I know this is bad code style - better solution needed
        if communication_queue.full():
            conn.close()
            return

        ssock = context.wrap_socket(conn, server_side=True)

        data = receive_dict(ssock)
        username = data["username"]
        given_game_pin = data["game_pin"]

        # Error handling
        if game_pin != given_game_pin:
            send_dict({ "message": "Wrong game pin!" }, ssock)
            ssock.close()
            continue

        if username in established_connections.keys():
            send_dict({ "message": "Username is already taken! Try again." }, ssock)
            ssock.close()
            continue

        established_connections[username] = ssock
        send_dict({ "message": "You are registered! Get ready for some action ;-)" }, ssock)


def wait_for_registration_end(communication_queue):
    print("Type \"end\" to end the registration phase")

    while input("> ") != "end":
        print()

    print("Registration is over")
    communication_queue.put(1)


def start_registration_phase():
    game_pin = str(random.randint(1000, 9999))

    print("Registration is open!")
    print("Game pin: ", game_pin, "\n")

    communication_queue = queue.Queue(1)

    registration_thread = threading.Thread(target=accept_registrations, args=(communication_queue, game_pin))
    registration_thread.start()

    wait_for_registration_end(communication_queue)

    print("Participants:\n")

    for name in established_connections.keys():
        print(" - ", name)

    print()


def start_quiz_phase():
    for ssock in established_connections.values():
        send_dict({ "message": "The quiz will start now!" }, ssock)

    print("Starting quiz...")

    sys.exit(0)


if __name__ == "__main__":
    global established_connections
    global accepting
    global s

    established_connections = {}
    accepting = True

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(
            certfile="/etc/letsencrypt/live/grahoot.fabianspecht.xyz/fullchain.pem",
            keyfile="/etc/letsencrypt/live/grahoot.fabianspecht.xyz/privkey.pem")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 8004))
    s.listen()

    start_registration_phase()
    start_quiz_phase()
