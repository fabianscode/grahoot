# grahoot

# this repo is no longer maintained. Moved to https://git.sr.ht/~fabiancodes/grahoot

## installation

the cli client can be installed via the python package index:

```
pip install grahoot-py
```

or with automatically managed environments

```
pipx install grahoot-py
```


## todo
- option not to use tls
- show live clock in client
- cleaner input handling in client
- make backend controlable through stdin/stdout

## protocol quiz-client <-> server

All data is exchanged via the JSON format because it's easy to use in python.
TLS will be used by default.

### registration phase

client -> server:
```
{
    "username": "<username>",
    "game_pin": "<game_pin>"
}
```

server -> client:

```
{
    "status": "<0 when successful; 1 otherwise>",
    "message": "<descriptive message>"
}
```

server -> clients:
```
{
    "message": "registration end"
}
```

### quiz phase

server -> clients:
```
{
    "title": "<title>",
    "time": "<time_in_seconds>",
    "points": "<points>",
    "type": "single choice" | "multiple choice" | "guess number" | "guess string",
    "options": [
        { "text": "<text>" },
        ...
    ], -- only used for single and multiple choice
    "solution": "Index <indicies of correct choices comma separated>" | "Guess <correct number>" -- if type is not "guess string",
    "solution": [
        { "text": "<possible solution>" },
        ...
    ], -- if type is "guess string"
    "rad": "<radius to get points in>" -- this entry exists only for number guesses
}
```

client -> server:
```
{
    "answer": "<answer>"
}
```

server -> clients:
```
{
    "solution": "<solution>",
    "score": "<new_user_score>"
}
```

### end phase

server -> clients:
```
{
    "message": "end"
}
```

## server control protocol via stdin/stdout (WIP)
This protocol gives the user the control over the server using it's stdin/stdout, 
which might be useful for remote control. For example, there could be a supervising
process - acting as a server - responsible for multiple quizzes at once, 
giving the 'quiz master' the ability to start a quiz via a website or any other client.

controller will be C and server S

### registration phase

```
S: <game_pin>
C: ok

foreach new_user:
    S: <new_user>
    C: ok

C: end
S: ok
S: <num of participants>
C: ok

```

If an ok is expected but something else is received, "error" will be written to
stdout.

### quiz phase

### end phase
