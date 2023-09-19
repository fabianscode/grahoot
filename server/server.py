import ssl
import os
import time
import queue
import random
import sys
import socket
import threading
from helpers import *


def registration_phase(context, connections, socket, interactive_mode):
    game_pin = str(random.randint(1000, 9999))

    if interactive_mode:
        print("Registration is open!")
        print("Game pin: ", game_pin, "\n")
    else:
        print(game_pin)

    communication_queue = queue.Queue(1)

    registration_thread = threading.Thread(target=accept_registrations, args=(context, socket, connections, communication_queue, game_pin, interactive_mode))
    registration_thread.start()

    wait_for_registration_end(communication_queue, interactive_mode)


def wait_for_registration_end(communication_queue, interactive_mode):
    if interactive_mode:
        print("Type \"end\" to end the registration phase")

        while input(" > ") != "end":
            print()

        print("Registration is over")
    else:
        while input() != "end":
            pass

        print("ok")

    communication_queue.put(1)


def accept_registrations(context, socket, connections, communication_queue, game_pin, interactive_mode):
    while True:
        conn, _ = socket.accept()

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
            send_dict({ 
                "status": "1", 
                "message": "Wrong game pin!"
            }, ssock)

            ssock.close()
            continue

        if username in connections.keys():
            send_dict({ 
                "status": "1", 
                "message": "Username is already taken! Try again."
            }, ssock)

            ssock.close()
            continue

        connections[username] = ssock

        send_dict({ 
            "status": "0", 
            "message": "You are registered! Get ready for some action ;-)"
        }, ssock)

        if interactive_mode:
            print(username, " joined")
        else:
            print(username)
            check_ok()


def quiz_phase(inputfile, connections, interactive_mode):
    print("Starting quiz...\n")

    questions = read_questions(inputfile)
    answers = {}
    scoreboard = {}

    for username in connections.keys():
        scoreboard[username] = 0

    for question in questions:
        print("Type \"next\" to start the next round")

        while input(" > ") != "next":
            pass

        handle_question(question, connections, answers, scoreboard)

    end_quiz_phase(connections)
    os._exit(0)


def handle_question(question, connections, answers, scoreboard):
    print_question(question)

    solution = question["solution"]
    del question["solution"]

    begin_timestamp = time.time()

    for ssock in connections.values():
        send_dict(question, ssock)

    question["solution"] = solution

    for username, ssock in connections.items():
        user_answer_thread = threading.Thread(
                target=receive_answer, 
                args=(username, question, begin_timestamp, connections, answers, scoreboard))
        user_answer_thread.start()

    countdown(question["time"])

    for username, ssock in connections.items():
        send_dict({
            "solution": solution,
            "score": scoreboard[username]
        }, ssock)

    print("\n\nSolution: ", solution, "\n")

    print_scoreboard(scoreboard)


def end_quiz_phase(connections):
    for ssock in connections.values():
        send_dict({ "message": "registration end" }, ssock)


def main(argv):
    connections = {}

    inputfile, port, fullchain, private_key, interactive_mode = read_user_input(argv)

    # load tls certificate
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(
            certfile=fullchain,
            keyfile=private_key)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("", port))
        sock.listen()

        registration_phase(context, connections, sock, interactive_mode)
        quiz_phase(inputfile, connections, interactive_mode)


if __name__ == "__main__":
    main(sys.argv[1:])

