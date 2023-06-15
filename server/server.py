import ssl
import time
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
        conn, _ = s.accept()

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
        scores[username] = 0
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


def read_questions(path):
    questions = []

    with open(path, "r") as quiz_file:
        content = quiz_file.read()
        questions = json.loads(content)

        quiz_file.close()

    return questions


def receive_answer(username, question_id, correct_answer, begin_timestamp, question_time, points):
    ssock = established_connections[username]

    try:
        user_answer = receive_dict(ssock)
        user_answer = user_answer["selected_answer"]

        received_timestamp = time.time()
        time_passed = received_timestamp - begin_timestamp

        answers[question_id] = (username, user_answer)

        if user_answer == correct_answer:
            score = int(points * ((1 - time_passed / question_time)) ** 2) + 500
            scores[username] += score

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

    sorted_leaderboard = sorted(scores.items(), key=lambda x:x[1], reverse=True)

    for index, (user, score) in enumerate(sorted_leaderboard):
        print(score, " - ", user)

    print()



def handle_question(question):
    print_question(question)

    correct_answer = str(question["correct"])
    del question["correct"]

    begin_timestamp = time.time()

    for ssock in established_connections.values():
        send_dict(question, ssock)

    for username, ssock in established_connections.items():
        user_answer_thread = threading.Thread(target=receive_answer, args=(username, ssock, correct_answer, begin_timestamp, question["time"], question["points"]))
        user_answer_thread.start()

    time.sleep(int(question["time"]))

    for username, ssock in established_connections.items():
        send_dict({
            "solution": correct_answer,
            "score": scores[username]
        }, ssock)

    print()
    print_leaderboard()


def end_quiz_phase():
    for ssock in established_connections.values():
        send_dict({ "message": "end" }, ssock)


def start_quiz_phase():
    print("Starting quiz...\n")

    questions = read_questions("quiz.json")

    for question in questions:
        print("Type \"next\" to start the next round")

        while input(" > ") != "next":
            pass

        handle_question(question)

    end_quiz_phase()
    sys.exit(0)


if __name__ == "__main__":
    global established_connections
    global answers
    global scores
    global s

    established_connections = {}
    answers = {}
    scores = {}

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(
            certfile="/etc/letsencrypt/live/grahoot.fabianspecht.xyz/fullchain.pem",
            keyfile="/etc/letsencrypt/live/grahoot.fabianspecht.xyz/privkey.pem")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 8004))
    s.listen()

    start_registration_phase()
    start_quiz_phase()
