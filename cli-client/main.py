import sys
import tls_connection as conn
from helpers import *

def registration_phase(hostname, port, game_pin, display_name):
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

    server_answer = conn.receive_dict()

    if server_answer["status"] != "0":
        print(server_answer["message"])
        sys.exit()


def quiz_phase():
    print("The quiz begins!\n")

    while True:
        question = conn.receive_dict()

        if "message" in question.keys() and question["message"] == "registration end":
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

    registration_phase(hostname, port, game_pin, display_name)
    quiz_phase()


if __name__ == "__main__":
    main(sys.argv[1:])

