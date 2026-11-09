"""ALGO ARCADE World 2-3: THE COIN FOUNTAIN (rate limits, HTTP 429 and Retry-After).

A rate limiter as a bucket of coins: every request pays one coin at the door. A fountain drips coins back in at a
steady rate, and the bucket holds only so many. A burst works until the bucket is empty; then the guard answers
429 Too Many Requests, often with a Retry-After header saying how long to wait. Retrying right away just gets
bounced again. Waiting the time the server gives you, then retrying, gets everyone through.

Run it (Python 3.8 or newer, nothing to install, works offline):

    python3 token_bucket.py           # play the level: 7 requests at a bucket of 5 that refills 1 coin a second
    python3 token_bucket.py --json    # the level as JSON (the reel is drawn from this)

Use it in your own code:
    TokenBucket(capacity, rate)       a limiter for your own API (allow() is True or False, and the wait)
    retry_after_seconds(header)       reads a Retry-After header: seconds ("3") or an HTTP date (RFC 9110)
    call_with_retry(send)             retries a call on 429: waits Retry-After if given, else backs off 1, 2, 4 s

The clock in the level is a fake one, so the level runs in an instant and always gives the same numbers.
Where the game picture stops: the token bucket is a common rule, not every API's rule (Anthropic's API documents
that it uses one; check your provider's rate limit page). Real limits count requests and often tokens per minute,
and not every 429 carries a Retry-After header.
"""
import email.utils
import json
import math
import random
import sys
import time


class TokenBucket:
    """capacity coins at most; `rate` coins drip back in every second, continuously."""

    def __init__(self, capacity, rate, now=0.0):
        self.capacity, self.rate = capacity, rate
        self.coins, self.last = float(capacity), now

    def refill(self, now):
        self.coins = min(self.capacity, self.coins + (now - self.last) * self.rate)
        self.last = now

    def allow(self, now, cost=1):
        """(True, 0) and pay the coin, or (False, seconds until the coin is there): the Retry-After to send."""
        self.refill(now)
        if self.coins >= cost:
            self.coins -= cost
            return True, 0
        return False, math.ceil((cost - self.coins) / self.rate)


def retry_after_seconds(value, now=None):
    """Retry-After is either a number of seconds ("120") or an HTTP date (RFC 9110, section 10.2.3)."""
    if value is None:
        return None
    value = value.strip()
    if value.isdigit():
        return int(value)
    when = email.utils.parsedate_to_datetime(value).timestamp()
    return max(0, math.ceil(when - (time.time() if now is None else now)))


def call_with_retry(send, tries=5, sleep=time.sleep):
    """send() returns (status, headers, body). On 429: wait Retry-After (else 1, 2, 4 s plus a little jitter)."""
    for attempt in range(tries):
        status, headers, body = send()
        if status != 429:
            return status, headers, body
        wait = retry_after_seconds(headers.get("retry-after") or headers.get("Retry-After"))
        sleep(wait if wait is not None else 2 ** attempt + random.random())
    return status, headers, body


# ---- the level ---------------------------------------------------------------------------------------------------
def level(burst=7, capacity=5, rate=1.0):
    bucket = TokenBucket(capacity, rate)
    log = []

    def knock(now, who, why):
        ok, wait = bucket.allow(now)
        log.append({"t": now, "who": who, "why": why, "status": 200 if ok else 429,
                    "retry_after": None if ok else wait, "coins": math.floor(bucket.coins + 1e-9)})
        return ok, wait

    bounced = []
    for who in range(1, burst + 1):                       # a burst: everyone at once
        ok, wait = knock(0.0, who, "burst")
        if not ok:
            bounced.append(who)
    knock(0.0, bounced[0], "instant retry")              # retrying right away: bounced again
    now, wait = 0.0, log[-1]["retry_after"]
    for who in bounced:                                    # the right way: wait Retry-After before each retry
        now += wait
        ok, w = knock(now, who, "retry after wait")
        while not ok:
            now += w
            ok, w = knock(now, who, "retry after wait")
    passed = sum(e["status"] == 200 for e in log)
    return {"capacity": capacity, "rate": rate, "burst": burst, "log": log,
            "totals": {"sent": burst, "through": passed, "bounced": sum(e["status"] == 429 for e in log),
                       "burst_through": sum(e["status"] == 200 and e["why"] == "burst" for e in log), "waited": now}}


def play():
    d = level()
    print(f'bucket of {d["capacity"]} coins, the fountain adds {d["rate"]:g} a second; {d["burst"]} requests arrive at once\n')
    for e in d["log"]:
        tail = "pays a coin, goes through" if e["status"] == 200 else f'Too Many Requests, Retry-After: {e["retry_after"]}'
        print(f'clock {e["t"]:>4.1f} s  request {e["who"]}  ({e["why"]:<16})  {e["status"]}  {tail:<42} coins left {e["coins"]}')
    t = d["totals"]
    print(f'\n{t["sent"]} sent, {t["through"]} through, {t["bounced"]} bounced, done after {t["waited"]:g} s of waiting')


if __name__ == "__main__":
    if "--json" in sys.argv:
        print(json.dumps(level(), indent=1))
    else:
        play()
