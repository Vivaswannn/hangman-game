import pytest
from hangman import display_hint, display_answer  # Import functions from your Hangman game

def test_display_hint():
    hint = ["_", "_", "_"]
    assert " ".join(hint) == "_ _ _"

def test_display_answer():
    answer = list("cat")
    assert " ".join(answer) == "c a t"

def test_correct_guess():
    answer = "hangman"
    hint = ["_"] * len(answer)
    guess = "h"

    for i in range(len(answer)):
        if answer[i] == guess:
            hint[i] = guess
    
    assert hint == ["h", "_", "_", "_", "_", "_", "_"]

def test_wrong_guess():
    answer = "hangman"
    wrong_guesses = 0
    guess = "z"

    if guess not in answer:
        wrong_guesses += 1

    assert wrong_guesses == 1
