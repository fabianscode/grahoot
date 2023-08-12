import ssl
import os
import time
import queue
import random
import sys
import socket
import json
import getopt
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


def accept_registrations(context, communication_queue, game_pin):
    while True:
        conn, (ip, port) = socket.accept()

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
            send_dict({ "status": 1, "message": "Wrong game pin!" }, ssock)
            ssock.close()
            continue

        if username in connections.keys():
            send_dict({ "status": 1, "message": "Username is already taken! Try again." }, ssock)
            ssock.close()
            continue

        connections[username] = ssock
        scoreboard[username] = 0
        send_dict({ "status": 0, "message": "You are registered! Get ready for some action ;-)" }, ssock)


def wait_for_registration_end(communication_queue):
    print("Type \"end\" to end the registration phase")

    while input(" > ") != "end":
        print()

    print("Registration is over")
    communication_queue.put(1)


def start_registration_phase(context):
    game_pin = str(random.randint(1000, 9999))

    print("Registration is open!")
    print("Game pin: ", game_pin, "\n")

    communication_queue = queue.Queue(1)

    registration_thread = threading.Thread(target=accept_registrations, args=(context, communication_queue, game_pin))
    registration_thread.start()

    wait_for_registration_end(communication_queue)

    print("Participants:\n")

    for name in connections.keys():
        print(" - ", name)

    print()


def read_questions(path):
    questions = []

    with open(path, "r") as quiz_file:
        content = quiz_file.read()
        questions = json.loads(content)

        quiz_file.close()

    return questions


def receive_answer(username, question_id, correct_answer, begin_timestamp, question_time, points):
    ssock = connections[username]

    try:
        user_answer = receive_dict(ssock)
        user_answer = user_answer["selected_answer"]

        received_timestamp = time.time()
        time_passed = received_timestamp - begin_timestamp

        answers[question_id] = (username, user_answer)

        if user_answer == correct_answer:
            score = int(points * ((1 - time_passed / question_time)) ** 2) + 500
            scoreboard[username] += score

    except:
        pass


def print_question(question):
    print(question["question"])
    print("You've got ", question["time"], " seconds!\n")

    for answer in question["answers"]:
        print("\t", answer["id"], ": ", answer["answer"])

    print()


def print_leaderboard():
    print("\n--- LEADERBOARD ---\n")

    sorted_leaderboard = sorted(scoreboard.items(), key=lambda x:x[1], reverse=True)

    for index, (user, score) in enumerate(sorted_leaderboard):
        print("  ", index + 1, "\t", score, "\t - ", user)

    print()


def print_solution(solution):
    print("Solution:")
    print(solution)


def countdown(timespan):
    for i in range (0, timespan):
        time.sleep(1)

        print("Time left: {:02d} s".format(timespan - i - 1), end='\r')
        sys.stdout.flush()


def handle_question(question):
    print_question(question)

    correct_answer = str(question["correct"])
    del question["correct"]

    begin_timestamp = time.time()

    for ssock in connections.values():
        send_dict(question, ssock)

    for username, ssock in connections.items():
        user_answer_thread = threading.Thread(
                target=receive_answer, 
                args=(username, ssock, correct_answer, begin_timestamp, question["time"], question["points"]))
        user_answer_thread.start()

    countdown(question["time"])

    for username, ssock in connections.items():
        send_dict({
            "solution": correct_answer,
            "score": scoreboard[username]
        }, ssock)

    print("\n\nSolution: ", correct_answer, "\n")
    print_leaderboard()


def end_quiz_phase():
    for ssock in connections.values():
        send_dict({ "message": "registration end" }, ssock)


def start_quiz_phase(inputfile):
    print("Starting quiz...\n")

    questions = read_questions(inputfile)

    for question in questions:
        print("Type \"next\" to start the next round")

        while input(" > ") != "next":
            pass

        handle_question(question)

    end_quiz_phase()
    os._exit(0)


def print_usage():
    print("""server.py [-i inputfile] [-p port] [-f tls_fullchain] [-k tls_private_key]""")


def read_user_input(argv):
    inputfile = ""
    port = ""
    tls_fullchain = ""
    tls_private_key = ""

    opts, _ = getopt.getopt(argv, "hi:p:f:k:")

    for opt, arg in opts:
        if opt == '-h':
            print_usage()
            sys.exit()
        elif opt in ("-i"):
            inputfile = arg
        elif opt in ("-p"):
            port = arg
        elif opt in ("-f"):
            tls_fullchain = arg
        elif opt in ("-k"):
            tls_private_key = arg

    if "" in [inputfile, port, tls_fullchain, tls_private_key]:
        print_usage()
        sys.exit()

    return inputfile, int(port, base=10), tls_fullchain, tls_private_key


def main(argv):
    global connections
    global answers
    global scoreboard
    global socket

    connections = {}
    answers = {}
    scoreboard = {}

    inputfile, port, fullchain, private_key = read_user_input(argv)

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(
            certfile=fullchain,
            keyfile=private_key)

    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.bind(("", port))
    socket.listen()

    start_registration_phase(context)
    start_quiz_phase(inputfile)


if __name__ == "__main__":
    main(sys.argv[1:])
