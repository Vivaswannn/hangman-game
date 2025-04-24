from flask import Flask, render_template_string, request
import random

app = Flask(__name__)

hangman_art = {
    0: ("   ", "   ", "   "),
    1: (" o ", "   ", "   "),
    2: (" o ", " | ", "   "),
    3: (" o ", "/| ", "   "),
    4: (" o ", "/|\\", "   "),
    5: (" o ", "/|\\", "/  "),
    6: (" o ", "/|\\", "/ \\")
}

words = (
    "aardvark", "alligator", "alpaca", "ant", "anteater", "antelope", "ape", "armadillo", "baboon", "badger", "bat",
    "bear", "beaver", "bee", "bison", "boar", "buffalo", "butterfly", "camel", "capybara", "caribou", "cat", "caterpillar",
    "cattle", "chamois", "cheetah", "chicken", "chimpanzee", "chinchilla", "chough", "clam", "cobra", "cockroach", "cod",
    "coyote", "crab", "crane", "crocodile", "crow", "curlew", "deer", "dinosaur", "dog", "dogfish", "dolphin", "donkey",
    "dormouse", "dotterel", "dove", "dragonfly", "duck", "dugong", "dunlin", "eagle", "echidna", "eel", "eland", "elephant",
    "elk", "emu", "falcon", "ferret", "finch", "fish", "flamingo", "fly", "fox", "frog", "gaur", "gazelle", "gerbil", "giraffe"
    # Add more words here...
)

def display_man(wrong_guesses):
    return "\n".join(hangman_art[wrong_guesses])

def display_hint(hint):
    return " ".join(hint)

def display_answer(answer):
    return " ".join(answer)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # Game logic
        answer = request.form.get("answer")
        hint = request.form.get("hint").split()
        wrong_guesses = int(request.form.get("wrong_guesses"))
        guessed_letters = set(request.form.get("guessed_letters").split(","))
        guess = request.form.get("guess").lower()

        if len(guess) != 1 or not guess.isalpha():
            return render_template_string(game_template, message="Invalid input", hint=display_hint(hint), man=display_man(wrong_guesses), guessed_letters=",".join(guessed_letters))

        if guess in guessed_letters:
            return render_template_string(game_template, message=f"{guess} is already guessed", hint=display_hint(hint), man=display_man(wrong_guesses), guessed_letters=",".join(guessed_letters))

        guessed_letters.add(guess)

        if guess in answer:
            for i in range(len(answer)):
                if answer[i] == guess:
                    hint[i] = guess
        else:
            wrong_guesses += 1

        if "_" not in hint:
            return render_template_string(game_template, message="YOU WIN!", hint=display_hint(hint), answer=display_answer(answer), man=display_man(wrong_guesses), guessed_letters=",".join(guessed_letters))
        elif wrong_guesses >= len(hangman_art) - 1:
            return render_template_string(game_template, message="YOU LOSE!", hint=display_hint(hint), answer=display_answer(answer), man=display_man(wrong_guesses), guessed_letters=",".join(guessed_letters))

        return render_template_string(game_template, hint=display_hint(hint), man=display_man(wrong_guesses), guessed_letters=",".join(guessed_letters), wrong_guesses=wrong_guesses, answer="".join(answer))

    # Starting new game
    answer = random.choice(words)
    hint = ["_"] * len(answer)
    guessed_letters = set()
    wrong_guesses = 0
    return render_template_string(game_template, hint=display_hint(hint), man=display_man(wrong_guesses), guessed_letters=",".join(guessed_letters), wrong_guesses=wrong_guesses, answer="".join(answer))

game_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hangman Game</title>
</head>
<body>
    <h1>Hangman Game</h1>

    <div>
        <h2>Hangman:</h2>
        <pre>{{ man }}</pre>
    </div>

    <div>
        <h3>Hint: </h3>
        <p>{{ hint }}</p>
    </div>

    {% if message %}
        <p>{{ message }}</p>
    {% endif %}

    {% if answer %}
        <h3>Answer:</h3>
        <p>{{ answer }}</p>
    {% endif %}

    <form method="POST">
        <input type="hidden" name="answer" value="{{ answer }}">
        <input type="hidden" name="hint" value="{{ hint }}">
        <input type="hidden" name="wrong_guesses" value="{{ wrong_guesses }}">
        <input type="hidden" name="guessed_letters" value="{{ guessed_letters }}">

        <label for="guess">Guess a letter: </label>
        <input type="text" name="guess" id="guess" required>

        <button type="submit">Submit Guess</button>
    </form>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)
