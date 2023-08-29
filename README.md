# grahoot

## protcol

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
    "message": "<descriptive message>",
    "token": "<token>"
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
    "solution": "Index <indicies of correct choices comma separated>" | "Guess <correct number or string>"
}
```

client -> server:
```
{
    "token": "<token>",
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
