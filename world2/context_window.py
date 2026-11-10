"""ALGO ARCADE World 2-1: THE MEMORY PIPE (the context window).

A chat model only sees what fits in its context window, a pipe with room for a fixed number of tokens.
Every message goes in at one end. When it is full, the app that talks to the model has to make room:
chat apps often push the oldest turns out first (or compact them into a summary), and an API request that is
simply too long is rejected. The model does not "forget": the words are no longer in what it is sent.

Run it (Python 3.8 or newer, nothing to install, works offline):

    python3 context_window.py                       # play the level from the reel: a 16-token pipe
    python3 context_window.py mychat.txt            # your own chat: tokens per message, what falls out first
    python3 context_window.py mychat.txt --window 2000 --pin "my name is sam"
    python3 context_window.py --json                # the level as JSON (the reel is drawn from this)

A chat file is one message per line, optionally starting with "you:" or "ai:".

Token counts here are an ESTIMATE: about 4 characters of English per token (OpenAI's rule of thumb).
Every model has its own tokenizer, so real counts differ a bit; for exact numbers use your provider's
token counter. The 16-token pipe is a toy size; real windows hold hundreds of thousands of tokens.

Three fixes (the level plays the first one):
  1. Compact: replace old messages with one short summary (what /compact does in a coding agent).
  2. New task, new chat: an empty pipe, no old messages taking room.
  3. Pin what must stay: put it in your instructions (system prompt, CLAUDE.md, AGENTS.md); the app sends
     it first on every request, so it is never the oldest message that gets pushed out (--pin below).
"""
import json
import math
import sys

CHARS_PER_TOKEN = 4


def count_tokens(text):
    """Estimate: about 4 characters per token, at least 1."""
    return max(1, math.ceil(len(text) / CHARS_PER_TOKEN))


class Window:
    """The context window: pinned items first, then the chat, oldest first."""

    def __init__(self, window, pinned=(), squeeze=False, summary=None):
        self.window = window
        self.pinned = list(pinned)
        self.chat = []                  # the messages, oldest first
        self.squeeze = squeeze          # True: compact old messages into a summary instead of dropping them
        self.summary = summary          # the summary text to use (a real app asks the model to write it)
        self.log = []                   # every event, for the terminal and for the reel

    def used(self):
        return sum(count_tokens(m) for m in self.pinned + self.chat)

    def note(self, event, text):
        self.log.append({"event": event, "text": text, "tokens": count_tokens(text), "used": self.used(),
                         "window": self.window, "pinned": list(self.pinned), "chat": list(self.chat)})

    def add(self, message):
        self.chat.append(message)
        self.note("add", message)
        while self.used() > self.window and len(self.chat) > 1:
            if self.squeeze and len(self.chat) > 2:
                old, self.chat = self.chat[:-1], self.chat[-1:]       # everything but the newest message
                text = self.summary or "summary: " + " / ".join(" ".join(m.split()[:2]) for m in old)
                self.chat.insert(0, text)
                self.note("compact", text)
                self.squeeze = False                                   # compact once, then drop if still full
            else:
                self.note("drop", self.chat.pop(0))                   # the oldest message falls out
        if self.used() > self.window:
            self.note("too_long", message)    # pins plus the newest message still do not fit: an API rejects this


def answer(window, question):
    """A scripted stand-in for the model: it can only answer from what is in the window right now."""
    for m in window.pinned + window.chat:
        words = m.lower().replace(":", " ").split()
        for k in range(len(words) - 3):
            if words[k:k + 3] == ["my", "name", "is"]:
                return words[k + 3].strip(".,!?").upper()
    return "?"


DEMO = ["my name is sam", "hi sam", "TypeError at app.js:42", "see line 42"]
QUESTION = "what is my name?"
WINDOW = 16
SUMMARY = "summary: my name is sam"   # a real app asks the model to write this


def level():
    """The two rounds of the reel, the same chat both times. Round 1: the oldest message is pushed out.
    Round 2: compact is on, so the old messages are squeezed into one summary that still has the name."""
    rounds = []
    plain = Window(WINDOW)
    for m in DEMO:
        plain.add(m)
    plain.add(QUESTION)
    plain.note("answer", answer(plain, QUESTION))
    rounds.append({"name": "plain", "events": plain.log})

    compact = Window(WINDOW, squeeze=True, summary=SUMMARY)
    for m in DEMO:
        compact.add(m)
    compact.add(QUESTION)                               # full, so the old messages get compacted
    compact.note("answer", answer(compact, QUESTION))
    rounds.append({"name": "compact", "events": compact.log})
    return {"window": WINDOW, "chars_per_token": CHARS_PER_TOKEN, "rounds": rounds}


def show(event):
    used, window = event["used"], event["window"]
    bar = "#" * min(used, window) + "." * max(0, window - used) + "+" * max(0, used - window)   # + = over the top
    kind = event["event"].upper().replace("_", " ")
    text = event["text"]
    if event["event"] in ("add", "drop", "pin", "compact"):
        text = f'"{text}" ({event["tokens"]} tokens)'
    print(f"[{bar}] {used:>3}/{window}  {kind:<9} {text}")


def play():
    data = level()
    for r in data["rounds"]:
        print(f'\n== {r["name"]}: a pipe of {data["window"]} tokens')
        for e in r["events"]:
            show(e)
    print('\nRound 1 lost the name: it was the oldest message. Round 2 compacted the old messages and kept it.')


def your_chat(path, window, pins):
    lines = [ln.strip() for ln in open(path, encoding="utf-8") if ln.strip()]
    messages = [ln.split(":", 1)[1].strip() if ln.lower().startswith(("you:", "ai:")) else ln for ln in lines]
    win = Window(window, pinned=pins)
    for m in messages:
        win.add(m)
    total = sum(count_tokens(m) for m in pins + messages)
    print(f"{len(messages)} messages, about {total} tokens (estimate, {CHARS_PER_TOKEN} characters per token)")
    for m in pins:
        print(f"  pinned  {count_tokens(m):>6}  {m[:60]}")
    dropped = sum(1 for e in win.log if e["event"] == "drop")           # drops are always the oldest first
    for k, m in enumerate(messages):
        print(f"  {'OUT' if k < dropped else 'kept':<7} {count_tokens(m):>6}  {m[:60]}")
    print(f"window {window}: the {dropped} oldest messages would fall out" if dropped else f"window {window}: everything fits")
    if any(e["event"] == "too_long" for e in win.log):
        print("and the pinned items plus the newest message are still over the window: an API would reject that request")


def main(argv):
    if "--json" in argv:
        print(json.dumps(level(), indent=1))
    elif argv and not argv[0].startswith("--"):
        window = int(argv[argv.index("--window") + 1]) if "--window" in argv else 200000
        pins = [argv[k + 1] for k, a in enumerate(argv) if a == "--pin"]
        your_chat(argv[0], window, pins)
    else:
        play()


if __name__ == "__main__":
    main(sys.argv[1:])
