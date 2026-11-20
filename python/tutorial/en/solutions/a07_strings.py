"""Basics A7: Strings.

Run: python3 python/tutorial/en/run.py A07
"""
from check import lesson, eq, done


def initials(full_name):
    """Initials: initials("ada lovelace") returns "AL".
    full_name.split() splits it into words; word[0] is the first letter; .upper() makes it a capital."""
    # >>>
    out = ""
    for word in full_name.split():
        out += word[0].upper()
    return out
    # <<<


def has_digit(password):
    """Does the password contain a digit? Look at each character; ch.isdigit() tells you."""
    # >>>
    for ch in password:
        if ch.isdigit():
            return True
    return False
    # <<<


def reverse(s):
    """Reverse a string. The slice s[::-1] does it in one step."""
    # >>>
    return s[::-1]
    # <<<


def mask_phone(phone):
    """Hide the middle of a phone number: mask_phone("5551234567") returns "555****4567".
    Slices: phone[:3] is the first 3 characters, phone[-4:] the last 4."""
    # >>>
    return phone[:3] + "****" + phone[-4:]
    # <<<


def guess_compare():
    """🤔 Guess, then run: don't run it yet! Read the line below, guess the result, write your guess after return,
    then run and see if you were right.

        "3" < "10"   ← True or False?
    """
    # >>>
    return False
    # <<<


lesson("Basics A7: Strings")
eq('initials("ada lovelace") is "AL"', "AL", lambda: initials("ada lovelace"))
eq('initials("Guido van Rossum") is "GVR"', "GVR", lambda: initials("Guido van Rossum"))
eq('"abc123" contains a digit', True, lambda: has_digit("abc123"))
eq('"password" has no digit', False, lambda: has_digit("password"))
eq('reverse("stressed") is "desserts"', "desserts", lambda: reverse("stressed"))
eq('mask_phone("5551234567")', "555****4567", lambda: mask_phone("5551234567"))
eq('🤔 guess: "3" < "10"', "3" < "10", guess_compare)
done()
