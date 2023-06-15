import sys
import signal
import time
import getopt
import tls_connection as conn
from inputimeout import inputimeout

def print_usage():
    print("""main.py [-n hostname] [-p port] [-g game_pin] [-d display_name]""")


def read_user_input(argv):
    hostname = ""
    port = ""
    game_pin = ""
    display_name = ""

    opts, _ = getopt.getopt(argv, "hn:p:g:d:")

    for opt, arg in opts:
        if opt == '-h':
            print_usage()
            sys.exit()
        elif opt in ("-n"):
            hostname = arg
        elif opt in ("-p"):
            port = arg
        elif opt in ("-g"):
            game_pin = arg
        elif opt in ("-d"):
            display_name = arg

    if "" in [hostname, port, game_pin, display_name]:
        print_usage()
        sys.exit()

    return hostname, int(port, base=10), game_pin, display_name


def connect(hostname, port, game_pin, display_name):
    print(f"Connecting to {hostname}:{port} ...")

    successfull = conn.open_connection(hostname, port)

    if not successfull:
        print("Connection failed!")
        sys.exit()

    print("Connection established!")

    data = {
        "username": display_name,
        "game_pin": game_pin
    }

    conn.send_dict(data)

    recv = conn.receive_dict()

    if recv["status"] != 0:
        print(recv["message"])
        sys.exit()


def print_question(question):
    print(question["question"])
    print("You've got ", question["time"], " seconds!\n")

    for answer in question["answers"]:
        print("\t", answer["id"], ": ", answer["answer"])

    print()


def print_solution(solution):
    print("Correct answer: ", solution)


def print_score(score):
    print("Score: ", score)


def get_user_answer(timeout):
    user_answer = ""

    try:
        user_answer = inputimeout(prompt="Your answer: ", timeout=timeout)
    except:
        print("No answer was given.")

    user_answer = {
        "selected_answer": user_answer
    }

    return user_answer


def quiz():
    print("The quiz begins!\n")

    while True:
        question = conn.receive_dict()

        if "message" in question.keys() and question["message"] == "end":
            break

        print_question(question)



        user_answer = get_user_answer(question["time"])
        conn.send_dict(user_answer)

        response = conn.receive_dict()
        print_solution(response["solution"])
        print_score(response["score"])

        print()


def main(argv):
    hostname, port, game_pin, display_name = read_user_input(argv)
    connect(hostname, port, game_pin, display_name)

    quiz()


if __name__ == "__main__":
    main(sys.argv[1:])

