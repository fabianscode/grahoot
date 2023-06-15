import sys
import time
import getopt
import tls_connection as conn

def print_usage():
    print("""main.py [-n hostname] [-p port] [-g game_pin] [-d display_name] [-c certificate]""")


def read_user_input(argv):
    hostname = ""
    port = ""
    game_pin = ""
    display_name = ""
    certificate_path = ""

    opts, _ = getopt.getopt(argv, "hn:p:g:d:c:")

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
        elif opt in ("-c"):
            certificate_path = arg

    if "" in [hostname, port, game_pin, display_name, certificate_path]:
        print_usage()
        sys.exit()

    return hostname, int(port, base=10), game_pin, display_name, certificate_path


def connect(hostname, port, game_pin, display_name, certificate_path):
    print(f"Connecting to {hostname}:{port} ...")

    successfull = conn.open_connection(hostname, port, certificate_path)

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
    print(recv["message"])


def print_question(question):
    print(question["question"])
    print("You've got ", question["time"], " seconds!\n")

    for answer in question["answers"]:
        print("\t", answer["id"], ": ", answer["answer"])

    print()


def get_user_answer():
    user_answer = input("Type your answer > ")

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
        user_answer = get_user_answer()

        conn.send_dict(user_answer)


def main(argv):
    hostname, port, game_pin, display_name, certificate_path = read_user_input(argv)
    connect(hostname, port, game_pin, display_name, certificate_path)

    quiz()


if __name__ == "__main__":
    main(sys.argv[1:])
