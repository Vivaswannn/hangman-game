import pygame
import random
import sys
import os

# Initialize pygame
pygame.init()

# Screen dimensions - increased for better layout
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hangman Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
LIGHT_BLUE = (173, 216, 230)
LIGHT_GREEN = (144, 238, 144)

# Fonts - reduced sizes to prevent overlapping
LETTER_FONT = pygame.font.SysFont('comicsans', 30)
WORD_FONT = pygame.font.SysFont('comicsans', 45)
TITLE_FONT = pygame.font.SysFont('comicsans', 60)
CATEGORY_FONT = pygame.font.SysFont('comicsans', 24)

# Load words from file or use default list
def load_words(filename):
    try:
        with open(filename, 'r') as file:
            return [word.strip().upper() for word in file.readlines()]
    except FileNotFoundError:
        # Default words if file not found
        return ['PYTHON', 'PYGAME', 'HANGMAN', 'DEVELOPER', 'CODING', 'ALGORITHM', 'COMPUTER']

# Word categories - added more words to each category
categories = {
    "Programming": ['PYTHON', 'JAVASCRIPT', 'JAVA', 'ALGORITHM', 'VARIABLE', 'FUNCTION', 'DATABASE', 'COMPILER', 
                    'CODING', 'HTML', 'CSS', 'REACT', 'ANGULAR', 'NODEJS', 'DJANGO', 'FLASK', 'RUBY', 'PHP', 'SQL'],
    "Animals": ['ELEPHANT', 'GIRAFFE', 'PENGUIN', 'DOLPHIN', 'TIGER', 'LEOPARD', 'KANGAROO', 'RHINOCEROS',
                'LION', 'ZEBRA', 'MONKEY', 'PANDA', 'KOALA', 'EAGLE', 'SHARK', 'WHALE', 'CROCODILE', 'GORILLA'],
    "Countries": ['AUSTRALIA', 'CANADA', 'BRAZIL', 'GERMANY', 'JAPAN', 'MEXICO', 'EGYPT', 'THAILAND',
                  'INDIA', 'CHINA', 'RUSSIA', 'FRANCE', 'ITALY', 'SPAIN', 'PORTUGAL', 'SWEDEN', 'NORWAY', 'KENYA'],
    "Sports": ['FOOTBALL', 'BASKETBALL', 'TENNIS', 'SWIMMING', 'VOLLEYBALL', 'CRICKET', 'HOCKEY', 'BASEBALL',
               'GOLF', 'RUGBY', 'BOXING', 'CYCLING', 'SKIING', 'ARCHERY', 'BADMINTON', 'KARATE', 'WRESTLING']
}

# Difficulty levels
difficulty_levels = {
    "Easy": [word for category in categories.values() for word in category if len(word) <= 5],
    "Medium": [word for category in categories.values() for word in category if 6 <= len(word) <= 8],
    "Hard": [word for category in categories.values() for word in category if len(word) > 8]
}

# Game variables
hangman_status = 0
current_category = "Programming"  # Default category
current_difficulty = "Medium"     # Default difficulty
word = random.choice(categories[current_category])
guessed = []
score = 0
time_started = 0
hint_used = False
game_state = "menu"  # menu, category, difficulty, game, end

# Sound effects
try:
    pygame.mixer.init()
    correct_sound = pygame.mixer.Sound('correct.wav')
    wrong_sound = pygame.mixer.Sound('wrong.wav')
    win_sound = pygame.mixer.Sound('win.wav')
    lose_sound = pygame.mixer.Sound('lose.wav')
    sound_available = True
except:
    sound_available = False

# Button variables - adjusted for better layout
RADIUS = 18
GAP = 15
letters = []
startx = round((WIDTH - (RADIUS * 2 + GAP) * 13) / 2)
starty = 450  # Moved down to make more space
A = 65
for i in range(26):
    x = startx + GAP * 2 + ((RADIUS * 2 + GAP) * (i % 13))
    y = starty + ((i // 13) * (GAP + RADIUS * 2))
    letters.append([x, y, chr(A + i), True])

# Load images
hangman_images = []
# Update the image loading section to account for 10 stages instead of 7
try:
    for i in range(11):  # Changed from 8 to 11 (0-10 = 11 images)
        image = pygame.image.load(f"hangman{i}.png")
        # Scale images to fit the screen better
        image = pygame.transform.scale(image, (180, 180))
        hangman_images.append(image)
    images_available = True
except:
    images_available = False

# Button class with improved visual feedback
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=BLACK):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.clicked = False
        self.active = True
        
    def draw(self, win):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.x < mouse_pos[0] < self.x + self.width and self.y < mouse_pos[1] < self.y + self.height
        
        # Draw button with border
        if not self.active:
            pygame.draw.rect(win, DARK_GRAY, (self.x, self.y, self.width, self.height), 0)
        elif is_hovered:
            pygame.draw.rect(win, self.hover_color, (self.x, self.y, self.width, self.height), 0)
        else:
            pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), 0)
        
        # Add border
        pygame.draw.rect(win, BLACK, (self.x, self.y, self.width, self.height), 2)
            
        # Use smaller font for buttons
        button_font = pygame.font.SysFont('comicsans', 28)
        text = button_font.render(self.text, 1, self.text_color)
        win.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))
        
        return is_hovered
    
    def is_clicked(self, pos):
        if not self.active:
            return False
        if self.x < pos[0] < self.x + self.width and self.y < pos[1] < self.y + self.height:
            return True
        return False

# Animation class for transitions
class Animation:
    def __init__(self, start_value, end_value, duration):
        self.start_value = start_value
        self.end_value = end_value
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        
    def get_value(self):
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time
        if elapsed >= self.duration:
            return self.end_value
        
        progress = elapsed / self.duration
        return self.start_value + (self.end_value - self.start_value) * progress

# Game functions with improved UI
def draw_game():
    screen.fill(LIGHT_BLUE)  # Use a more pleasant background color
    
    # Draw a game area
    pygame.draw.rect(screen, WHITE, (50, 50, WIDTH-100, HEIGHT-100), 0)
    pygame.draw.rect(screen, BLACK, (50, 50, WIDTH-100, HEIGHT-100), 2)
    
    # Draw title
    title = TITLE_FONT.render("HANGMAN", 1, BLACK)
    screen.blit(title, (WIDTH/2 - title.get_width()/2, 20))
    
    # Draw category and difficulty with smaller font
    category_text = CATEGORY_FONT.render(f"Category: {current_category} | Difficulty: {current_difficulty}", 1, BLUE)
    screen.blit(category_text, (WIDTH/2 - category_text.get_width()/2, 90))
    
    # Draw score
    score_text = CATEGORY_FONT.render(f"Score: {score}", 1, BLACK)
    screen.blit(score_text, (WIDTH - score_text.get_width() - 70, 70))
    
    # Draw word with better spacing
    display_word = ""
    for letter in word:
        if letter in guessed:
            display_word += letter + " "
        else:
            display_word += "_ "
    text = WORD_FONT.render(display_word, 1, BLACK)
    screen.blit(text, (WIDTH/2 - text.get_width()/2, 200))
    
    # Draw letter buttons with improved visibility
    for letter in letters:
        x, y, ltr, visible = letter
        if visible:
            # Draw filled circle with border
            pygame.draw.circle(screen, LIGHT_GREEN, (x, y), RADIUS, 0)
            pygame.draw.circle(screen, BLACK, (x, y), RADIUS, 2)
            text = LETTER_FONT.render(ltr, 1, BLACK)
            screen.blit(text, (x - text.get_width()/2, y - text.get_height()/2))
    
    # Draw hangman in a specific area - moved to the left side
    if images_available:
        # Make the hangman image smaller
        small_hangman = pygame.transform.scale(hangman_images[hangman_status], (150, 150))
        screen.blit(small_hangman, (120, 180))
    else:
        # If images aren't available, draw a simple hangman in a specific area
        draw_hangman(hangman_status)
    
    # Draw hint button with improved visibility - moved to avoid overlap
    hint_button = Button(70, 70, 80, 35, "HINT", YELLOW, DARK_GRAY)
    if hint_used:
        hint_button.active = False
    hint_button.draw(screen)
    
    pygame.display.update()
    return hint_button

def draw_menu():
    screen.fill(LIGHT_BLUE)
    
    # Draw a decorative frame
    pygame.draw.rect(screen, WHITE, (100, 50, WIDTH-200, HEIGHT-100), 0)
    pygame.draw.rect(screen, BLACK, (100, 50, WIDTH-200, HEIGHT-100), 3)
    
    # Draw title with shadow effect
    title_shadow = TITLE_FONT.render("HANGMAN", 1, DARK_GRAY)
    screen.blit(title_shadow, (WIDTH/2 - title_shadow.get_width()/2 + 3, 103))
    
    title = TITLE_FONT.render("HANGMAN", 1, BLACK)
    screen.blit(title, (WIDTH/2 - title.get_width()/2, 100))
    
    # Draw buttons with improved visibility
    play_button = Button(WIDTH/2 - 100, 250, 200, 50, "Play Game", GREEN, LIGHT_GREEN)
    play_button.draw(screen)
    
    quit_button = Button(WIDTH/2 - 100, 320, 200, 50, "Quit", RED, DARK_GRAY)
    quit_button.draw(screen)
    
    # Draw a decorative hangman icon
    if images_available and len(hangman_images) > 0:
        small_icon = pygame.transform.scale(hangman_images[0], (100, 100))
        screen.blit(small_icon, (WIDTH/2 - 50, 150))
    
    pygame.display.update()
    return play_button, quit_button

def draw_category_selection():
    screen.fill(LIGHT_BLUE)
    
    # Draw a decorative frame
    pygame.draw.rect(screen, WHITE, (100, 50, WIDTH-200, HEIGHT-100), 0)
    pygame.draw.rect(screen, BLACK, (100, 50, WIDTH-200, HEIGHT-100), 3)
    
    # Draw title
    title = TITLE_FONT.render("Select Category", 1, BLACK)
    screen.blit(title, (WIDTH/2 - title.get_width()/2, 50))
    
    # Draw category buttons with improved visibility
    category_buttons = []
    y_pos = 150
    for category in categories.keys():
        button = Button(WIDTH/2 - 150, y_pos, 300, 50, category, BLUE, LIGHT_BLUE, WHITE)
        button.draw(screen)
        category_buttons.append((button, category))
        y_pos += 70
    
    back_button = Button(20, 20, 80, 35, "Back", GRAY, DARK_GRAY)
    back_button.draw(screen)
    
    pygame.display.update()
    return category_buttons, back_button

def draw_difficulty_selection():
    screen.fill(LIGHT_BLUE)
    
    # Draw a decorative frame
    pygame.draw.rect(screen, WHITE, (100, 50, WIDTH-200, HEIGHT-100), 0)
    pygame.draw.rect(screen, BLACK, (100, 50, WIDTH-200, HEIGHT-100), 3)
    
    # Draw title
    title = TITLE_FONT.render("Select Difficulty", 1, BLACK)
    screen.blit(title, (WIDTH/2 - title.get_width()/2, 50))
    
    # Draw difficulty buttons with improved visibility
    difficulty_buttons = []
    y_pos = 150
    
    # Use different colors for different difficulties
    difficulty_colors = {
        "Easy": (LIGHT_GREEN, GREEN),
        "Medium": (YELLOW, (200, 200, 0)),
        "Hard": (RED, (200, 0, 0))
    }
    
    for difficulty in difficulty_levels.keys():
        color, hover = difficulty_colors.get(difficulty, (PURPLE, DARK_GRAY))
        button = Button(WIDTH/2 - 150, y_pos, 300, 50, difficulty, color, hover, BLACK)
        button.draw(screen)
        difficulty_buttons.append((button, difficulty))
        y_pos += 70
    
    back_button = Button(20, 20, 80, 35, "Back", GRAY, DARK_GRAY)
    back_button.draw(screen)
    
    pygame.display.update()
    return difficulty_buttons, back_button

def draw_hangman(status):
    # Simple hangman drawing if images aren't available - moved to a better position
    # Make the hangman smaller and position it on the left side
    hangman_x = 120
    hangman_y = 180
    scale = 0.7  # Scale factor to make hangman smaller
    
    if status >= 0:  # Base
        pygame.draw.rect(screen, BLACK, (hangman_x, hangman_y + 150*scale, 80*scale, 8*scale))
    if status >= 1:  # Vertical pole
        pygame.draw.rect(screen, BLACK, (hangman_x + 40*scale, hangman_y, 8*scale, 150*scale))
    if status >= 2:  # Horizontal pole
        pygame.draw.rect(screen, BLACK, (hangman_x + 40*scale, hangman_y, 80*scale, 8*scale))
    if status >= 3:  # Rope
        pygame.draw.rect(screen, BLACK, (hangman_x + 120*scale, hangman_y, 4*scale, 25*scale))
    if status >= 4:  # Head
        pygame.draw.circle(screen, BLACK, (hangman_x + 122*scale, hangman_y + 40*scale), 15*scale, 2)
    if status >= 5:  # Neck
        pygame.draw.rect(screen, BLACK, (hangman_x + 120*scale, hangman_y + 55*scale, 4*scale, 10*scale))
    if status >= 6:  # Body
        pygame.draw.rect(screen, BLACK, (hangman_x + 120*scale, hangman_y + 65*scale, 4*scale, 40*scale))
    if status >= 7:  # Left arm
        pygame.draw.line(screen, BLACK, (hangman_x + 120*scale, hangman_y + 70*scale), 
                         (hangman_x + 100*scale, hangman_y + 85*scale), 2)
    if status >= 8:  # Right arm
        pygame.draw.line(screen, BLACK, (hangman_x + 124*scale, hangman_y + 70*scale), 
                         (hangman_x + 144*scale, hangman_y + 85*scale), 2)
    if status >= 9:  # Left leg
        pygame.draw.line(screen, BLACK, (hangman_x + 120*scale, hangman_y + 105*scale), 
                         (hangman_x + 100*scale, hangman_y + 135*scale), 2)
    if status >= 10:  # Right leg - FINAL STAGE
        pygame.draw.line(screen, BLACK, (hangman_x + 124*scale, hangman_y + 105*scale), 
                         (hangman_x + 144*scale, hangman_y + 135*scale), 2)

def display_message(message, color):
    # Create a fade animation
    fade_surface = pygame.Surface((WIDTH, HEIGHT))
    fade_surface.fill(BLACK)
    
    for alpha in range(0, 175, 5):
        screen.fill(WHITE)
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.update()
        pygame.time.delay(30)
    
    screen.fill(WHITE)
    
    # Draw a decorative frame
    pygame.draw.rect(screen, LIGHT_BLUE, (100, 100, WIDTH-200, HEIGHT-200), 0)
    pygame.draw.rect(screen, BLACK, (100, 100, WIDTH-200, HEIGHT-200), 3)
    
    # Make the message text smaller if it's too long
    if len(message) > 15:
        message_font = pygame.font.SysFont('comicsans', 36)  # Smaller font for long messages
    else:
        message_font = pygame.font.SysFont('comicsans', 45)  # Smaller than original WORD_FONT
    
    # Draw message with shadow
    text_shadow = message_font.render(message, 1, DARK_GRAY)
    screen.blit(text_shadow, (WIDTH/2 - text_shadow.get_width()/2 + 2, HEIGHT/2 - text_shadow.get_height()/2 - 50 + 2))
    
    text = message_font.render(message, 1, color)
    screen.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/2 - text.get_height()/2 - 50))
    
    # Display final score
    score_text = CATEGORY_FONT.render(f"Final Score: {score}", 1, BLACK)
    screen.blit(score_text, (WIDTH/2 - score_text.get_width()/2, HEIGHT/2))
    
    # Play again button
    play_again = Button(WIDTH/2 - 150, HEIGHT/2 + 50, 300, 50, "Play Again", GREEN, LIGHT_GREEN)
    play_again.draw(screen)
    
    # Main menu button
    main_menu = Button(WIDTH/2 - 150, HEIGHT/2 + 120, 300, 50, "Main Menu", BLUE, LIGHT_BLUE, WHITE)
    main_menu.draw(screen)
    
    pygame.display.update()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_again.is_clicked(pygame.mouse.get_pos()):
                    reset_game()
                    return "game"
                if main_menu.is_clicked(pygame.mouse.get_pos()):
                    reset_game()
                    return "menu"
    
    return "menu"

def reset_game():
    global hangman_status, word, guessed, letters, score, time_started, hint_used
    hangman_status = 0
    
    # Select word based on category and difficulty
    if current_difficulty == "Easy":
        possible_words = [w for w in categories[current_category] if len(w) <= 5]
    elif current_difficulty == "Medium":
        possible_words = [w for w in categories[current_category] if 6 <= len(w) <= 8]
    else:  # Hard
        possible_words = [w for w in categories[current_category] if len(w) > 8]
    
    # If no words match the criteria, use any word from the category
    if not possible_words:
        possible_words = categories[current_category]
    
    word = random.choice(possible_words)
    guessed = []
    hint_used = False
    
    # Reset letters
    for letter in letters:
        letter[3] = True  # Set visibility to True
    
    time_started = pygame.time.get_ticks()

def give_hint():
    global hint_used, score
    if hint_used:
        return False
    
    # Find unguessed letters
    unguessed = [letter for letter in word if letter not in guessed]
    if not unguessed:
        return False
    
    # Add a random unguessed letter
    hint_letter = random.choice(unguessed)
    guessed.append(hint_letter)
    
    # Disable the letter button
    for letter in letters:
        if letter[2] == hint_letter:
            letter[3] = False
    
    # Apply score penalty
    score -= 50
    if score < 0:
        score = 0
    
    hint_used = True
    return True

def calculate_score(time_taken, word_length, difficulty_multiplier):
    base_score = word_length * 10
    time_bonus = max(0, 300 - time_taken // 1000) * 2
    
    if difficulty_multiplier == "Easy":
        multiplier = 1
    elif difficulty_multiplier == "Medium":
        multiplier = 1.5
    else:  # Hard
        multiplier = 2
    
    return int((base_score + time_bonus) * multiplier)

def main():
    global hangman_status, game_state, current_category, current_difficulty, score, time_started, word
    
    # Game loop
    FPS = 60
    clock = pygame.time.Clock()
    run = True
    
    # Add a loading screen
    screen.fill(BLACK)
    loading_text = TITLE_FONT.render("Loading...", 1, WHITE)
    screen.blit(loading_text, (WIDTH/2 - loading_text.get_width()/2, HEIGHT/2 - loading_text.get_height()/2))
    pygame.display.update()
    pygame.time.delay(1000)  # Simulate loading time
    
    while run:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                
                if game_state == "menu":
                    play_button, quit_button = draw_menu()
                    if play_button.is_clicked(pos):
                        game_state = "category"
                    elif quit_button.is_clicked(pos):
                        run = False
                
                elif game_state == "category":
                    category_buttons, back_button = draw_category_selection()
                    if back_button.is_clicked(pos):
                        game_state = "menu"
                    else:
                        for button, category in category_buttons:
                            if button.is_clicked(pos):
                                current_category = category
                                game_state = "difficulty"
                
                elif game_state == "difficulty":
                    difficulty_buttons, back_button = draw_difficulty_selection()
                    if back_button.is_clicked(pos):
                        game_state = "category"
                    else:
                        for button, difficulty in difficulty_buttons:
                            if button.is_clicked(pos):
                                current_difficulty = difficulty
                                reset_game()
                                game_state = "game"
                
                elif game_state == "game":
                    hint_button = draw_game()
                    
                    # Check if hint button was clicked
                    if hint_button.is_clicked(pos):
                        give_hint()
                    
                    # Check if letter buttons were clicked
                    for letter in letters:
                        x, y, ltr, visible = letter
                        if visible:
                            dis = ((pos[0] - x) ** 2 + (pos[1] - y) ** 2) ** 0.5
                            if dis < RADIUS:
                                letter[3] = False  # Set visibility to False
                                guessed.append(ltr)
                                
                                if ltr in word:
                                    # Correct guess
                                    # Add points for correct guess
                                    score += 10 * word.count(ltr)
                                else:
                                    # Wrong guess
                                    hangman_status += 1
        
        # Draw the current game state
        if game_state == "menu":
            draw_menu()
        elif game_state == "category":
            draw_category_selection()
        elif game_state == "difficulty":
            draw_difficulty_selection()
        elif game_state == "game":
            draw_game()
            
            # Check win/loss conditions
            won = True
            for letter in word:
                if letter not in guessed:
                    won = False
                    break
            
            if won:
                # Calculate final score based on time, word length, and difficulty
                time_taken = pygame.time.get_ticks() - time_started
                score_bonus = calculate_score(time_taken, len(word), current_difficulty)
                score += score_bonus
                
                game_state = display_message("You WON!", GREEN)
            
            # Only end the game when hangman is completely formed (10 wrong guesses)
            if hangman_status >= 10:
                game_state = display_message(f"You LOST! The word was: {word}", RED)
    
    pygame.quit()

if __name__ == "__main__":
    main()