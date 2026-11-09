# ALGO ARCADE WORLD 2

World 1 is algorithms. World 2 is how the AI and dev systems you use every day actually work, each one played as a
dungeon level. Every level is one small Python file: run it and the level plays in your terminal, with the same
numbers you see in the video.

Python 3.8 or newer, standard library only. Everything runs offline: where a real AI model would answer, the file
uses a small scripted stand-in, so you need no API key.

| level | file | the idea in one line |
|---|---|---|
| 2-1 | `context_window.py` | THE BAG RULE: the model only sees what fits in its context window; when it is full, the oldest messages go first |
| 2-2 | `agent_loop.py` | THE NOTE SLOT: the model only writes tool calls; your code runs them, sends the result back, and its allow list says no |
| 2-3 | `token_bucket.py` | THE COIN FOUNTAIN: a token bucket rate limiter, HTTP 429 and Retry-After, and retry code that waits the right time |

```sh
cd world2
python3 context_window.py                         # play level 2-1
python3 context_window.py mychat.txt --window 2000 # your own chat: tokens per message, what falls out first
python3 agent_loop.py                             # play level 2-2 (in a throwaway folder)
python3 token_bucket.py                           # play level 2-3
python3 -m unittest -v                            # check every level
```

Every file starts with a docstring that says how to run it and where the game picture stops matching the real thing.
