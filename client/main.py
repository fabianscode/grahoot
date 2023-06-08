import sys
import getopt
import json
import ssl

def print_usage():
    print("""main.py [-s server_address[:port]] [-g game_pin] [-d display_name]""")


def read_user_input(argv):
    server_address = ""
    game_pin = ""
    display_name = ""

    opts, _ = getopt.getopt(argv, "hs:g:d:")

    for opt, arg in opts:
        if opt == '-h':
            print_usage()
            sys.exit()
        elif opt in ("-s"):
            server_address = arg
        elif opt in ("-g"):
            game_pin = arg
        elif opt in ("-d"):
            display_name = arg

    if "" in [server_address, game_pin, display_name]:
        print_usage()
        sys.exit()

    return server_address, game_pin, display_name


def connect(server_address, game_pin, display_name):
    print(f"Connecting to {server_address} ...")


def main(argv):
    server_address, game_pin, display_name = read_user_input(argv)
    connect(server_address, game_pin, display_name)


if __name__ == "__main__":
    main(sys.argv[1:])

