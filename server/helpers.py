import json
import sys
import time
import getopt

BUFF_SIZE = 1024

def send_dict(dict_data, ssock):
    dict_data = json.dumps(dict_data)
    ssock.sendall(bytes(dict_data, encoding="utf-8"))


def receive_dict(ssock):
    data = ssock.recv(BUFF_SIZE)
    data = data.decode("utf-8")
    data = json.loads(data)

    return data


def read_questions(path):
    questions = []

    with open(path, "r") as quiz_file:
        content = quiz_file.read()
        questions = json.loads(content)

        quiz_file.close()

    return questions


def receive_answer(username, question, begin_timestamp, connections, answers, scoreboard):
    ssock = connections[username]

    user_answer = receive_dict(ssock)
    user_answer = user_answer["answer"]

    points = int(question["points"])
    question_time = int(question["time"])
    question_title = question["title"]

    if question["type"] in ["multiple choice", "single choice", "guess string"]:
        received_timestamp = time.time()
        time_passed = received_timestamp - begin_timestamp

        answers[question_title] = (username, user_answer)

        correct = False

        if question["type"] == "single choice":
            correct = question["solution"] == user_answer

        elif question["type"] == "multiple choice":
            user_answer = set(user_answer.split(','))
            solution = set(question["solution"].split(','))

            correct = user_answer == solution

        else:
            # in this case, the solution contains an array
            for solution in question["solution"]:
                if solution["text"] == user_answer:
                    correct = True
                    break
        
        if correct:
            score = int(points * ((1 - time_passed / question_time)) ** 2)
            scoreboard[username] += score

    elif question["type"] == "guess number":
        radius = float(question["rad"])
        user_answer = float(user_answer)
        solution = float(question["solution"])

        diff = abs(user_answer - solution)

        if diff < radius:
            # maybe put time into the score
            score = int(points - points * diff / radius)
            scoreboard[username] += score

    else:
        print("wrong question type")
        pass


def print_question(question):
    print(question["title"])
    print("You've got ", question["time"], " seconds!\n")

    if question["type"] in ["single choice", "multiple choice"]:
        for i, answer in enumerate(question["options"]):
            print("\t", i + 1, ": ", answer["text"])

    print()


def print_scoreboard(scoreboard):
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

