import sys
import getopt
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
        if opt == "-h":
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


def print_question(question):
    qtype = question["type"]
    print(qtype.upper())
    print("=" * len(qtype))

    print(question["title"])

    if qtype == "guess number":
        pass

    elif qtype == "guess string":
        pass

    elif qtype in ["single choice", "multiple choice"]:
        for i, answer in enumerate(question["options"]):
            print("\t", i + 1, ": ", answer["text"])

        if qtype == "multiple choice":
            print("\nenter the numbers comma separated")

    else:
        print("wrong question type")

    print("\nYou've got ", question["time"], " seconds!\n\n")


def print_solution(solution):
    print("Solution: ", solution)


def print_score(score):
    print("Score: ", score)


def get_user_answer(timeout):
    user_answer = ""

    try:
        user_answer = inputimeout(prompt="Your answer: ", timeout=timeout)
    except:
        print("No answer was given.")

    user_answer = {
        "answer": user_answer
    }

    return user_answer


