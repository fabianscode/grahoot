# grahoot

## installation

the cli client can be installed via the python package index:

```
pip install grahoot-py
```

or with automatically managed environments

```
pipx install grahoot-py
```


## TODO
- option not to use tls
- show live clock in client
- cleaner input handling in client
- make backend controlable through stdin/stdout

## protcol

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
