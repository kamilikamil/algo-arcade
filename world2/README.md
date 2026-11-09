# ALGO ARCADE WORLD 2

World 1 is algorithms. World 2 is how the AI and dev systems you use every day actually work, each one played as a
dungeon level. Every level is one small Python file: run it and the level plays in your terminal, with the same
numbers you see in the video.

Python 3.8 or newer, standard library only. Everything runs offline: where a real AI model would answer, the file
uses a small scripted stand-in, so you need no API key.

| level | file | the idea in one line |
|---|---|---|
| 2-1 | `context_window.py` | THE BAG RULE: the model only sees what fits in its context window; when it is full, the oldest messages go first |

```sh
cd world2
python3 context_window.py                         # play level 2-1
python3 context_window.py mychat.txt --window 2000 # your own chat: tokens per message, what falls out first
python3 -m unittest -v                            # check every level
```

Every file starts with a docstring that says how to run it and where the game picture stops matching the real thing.
