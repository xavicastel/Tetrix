import pygame
import random
import os

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
SIDE_PANEL_WIDTH = 200
BLOCK_SIZE = 30

# Colors
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)
COLORS = [
    (0, 255, 255),  # I
    (0, 0, 255),    # J
    (255, 165, 0),  # L
    (255, 255, 0),  # O
    (0, 255, 0),    # S
    (128, 0, 128),  # T
    (255, 0, 0)     # Z
]

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH + SIDE_PANEL_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")

# Clock for controlling the frame rate
clock = pygame.time.Clock()

# Define the shapes of the tetrominoes
TETROMINOES = {
    'I': [
        [[1, 1, 1, 1]],
        [[1],
         [1],
         [1],
         [1]]
    ],
    'J': [
        [[1, 0, 0],
         [1, 1, 1]],
        [[1, 1],
         [1, 0],
         [1, 0]],
        [[1, 1, 1],
         [0, 0, 1]],
        [[0, 1],
         [0, 1],
         [1, 1]]
    ],
    'L': [
        [[0, 0, 1],
         [1, 1, 1]],
        [[1, 0],
         [1, 0],
         [1, 1]],
        [[1, 1, 1],
         [1, 0, 0]],
        [[1, 1],
         [0, 1],
         [0, 1]]
    ],
    'O': [
        [[1, 1],
         [1, 1]]
    ],
    'S': [
        [[0, 1, 1],
         [1, 1, 0]],
        [[1, 0],
         [1, 1],
         [0, 1]]
    ],
    'T': [
        [[0, 1, 0],
         [1, 1, 1]],
        [[1, 0],
         [1, 1],
         [1, 0]],
        [[1, 1, 1],
         [0, 1, 0]],
        [[0, 1],
         [1, 1],
         [0, 1]]
    ],
    'Z': [
        [[1, 1, 0],
         [0, 1, 1]],
        [[0, 1],
         [1, 1],
         [1, 0]]
    ]
}

# Load sound effects
line_clear_sound = pygame.mixer.Sound(os.path.join('sounds', 'line_clear.wav'))
game_over_sound = pygame.mixer.Sound(os.path.join('sounds', 'game_over.wav'))
#rotate_sound = pygame.mixer.Sound(os.path.join('sounds', 'rotate.wav'))
#drop_sound = pygame.mixer.Sound(os.path.join('sounds', 'move.wav'))

# Tetromino class representing each Tetris piece
class Tetromino:
    def __init__(self, shape):
        self.shape = shape
        self.rotations = TETROMINOES[shape]
        self.rotation = 0  # Index for current rotation
        self.color = COLORS[list(TETROMINOES.keys()).index(shape)]  # Assign color based on shape
        # Start piece in the middle of the grid, considering its width
        self.x = SCREEN_WIDTH // BLOCK_SIZE // 2 - len(self.get_current_shape()[0]) // 2
        self.y = 0

    def get_current_shape(self):
        # Return the current shape after considering rotation
        return self.rotations[self.rotation]

    def rotate(self):
        # Rotate to the next orientation
        self.rotation = (self.rotation + 1) % len(self.rotations)

    def rotate_back(self):
        # Rotate back if current rotation is not valid
        self.rotation = (self.rotation - 1) % len(self.rotations)


def create_grid(locked_positions={}):
    # Create a grid filled with BLACK color and apply locked positions
    grid = [[BLACK for _ in range(SCREEN_WIDTH // BLOCK_SIZE)] for _ in range(SCREEN_HEIGHT // BLOCK_SIZE)]
    for y in range(SCREEN_HEIGHT // BLOCK_SIZE):
        for x in range(SCREEN_WIDTH // BLOCK_SIZE):
            if (x, y) in locked_positions:
                grid[y][x] = locked_positions[(x, y)]
    return grid


def convert_shape_format(shape):
    # Convert shape into grid positions for drawing and collision detection
    positions = []
    format = shape.get_current_shape()
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column:
                positions.append((shape.x + j, shape.y + i))
    return positions


def valid_space(shape, grid):
    # Check if the current shape is in a valid position on the grid
    accepted_positions = [[(x, y) for x in range(SCREEN_WIDTH // BLOCK_SIZE) if grid[y][x] == BLACK] for y in range(SCREEN_HEIGHT // BLOCK_SIZE)]
    accepted_positions = [x for sub in accepted_positions for x in sub]
    formatted = convert_shape_format(shape)
    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] >= 0:  # Ensure position is within bounds
                return False
    return True


def check_lost(positions):
    # Check if any locked position is above the top of the screen
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False


def clear_rows(grid, locked):
    # Clear filled rows and update locked positions
    rows_to_clear = []

    # Identify all full rows FIRST (before modifying anything)
    for y in range(len(grid)):
        if BLACK not in grid[y]:
            rows_to_clear.append(y)

    if not rows_to_clear:
        return 0

    # Sort in descending order to delete from bottom up
    rows_to_clear.sort(reverse=True)

    # Delete all full rows from the grid
    for y in rows_to_clear:
        del grid[y]

    # Add empty rows at the top
    for _ in range(len(rows_to_clear)):
        grid.insert(0, [BLACK for _ in range(SCREEN_WIDTH // BLOCK_SIZE)])

    # Update locked positions in ONE pass
    new_locked = {}
    for pos in locked:
        x, y_pos = pos
        # Count how many cleared rows were below this position
        shift_amount = sum(1 for row in rows_to_clear if row > y_pos)
        if y_pos not in rows_to_clear:
            new_locked[(x, y_pos + shift_amount)] = locked[pos]

    locked.clear()
    locked.update(new_locked)

    return len(rows_to_clear)


def get_new_piece():
    # Generate a new random piece
    return Tetromino(random.choice(list(TETROMINOES.keys())))


def draw_grid(surface, grid):
    # Draw each block of the grid and the grid lines
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            pygame.draw.rect(surface, grid[y][x],
                             (x*BLOCK_SIZE, y*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
    # Draw grid lines
    for y in range(len(grid)):
        pygame.draw.line(surface, GRAY, (0, y*BLOCK_SIZE), (SCREEN_WIDTH, y*BLOCK_SIZE))
    for x in range(len(grid[0])):
        pygame.draw.line(surface, GRAY, (x*BLOCK_SIZE, 0), (x*BLOCK_SIZE, SCREEN_HEIGHT))


def load_high_score(file_path):
    # Load the high score from a file
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            f.write("0")
    with open(file_path, 'r') as f:
        try:
            return int(f.read())
        except ValueError:
            return 0


def save_high_score(file_path, score):
    # Save the new high score if it is higher than the current one
    high_score = load_high_score(file_path)
    if score > high_score:
        with open(file_path, 'w') as f:
            f.write(str(score))


def draw_text_middle(text, size, color, surface):
    # Draw text in the middle of the screen
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, True, color)
    surface.blit(label, (SCREEN_WIDTH//2 - label.get_width()//2, SCREEN_HEIGHT//2 - label.get_height()//2))


def draw_side_panel(surface, score, high_score, level, held_piece):
    # Draw the side panel with score, high score, level, and held piece
    font = pygame.font.SysFont('comicsans', 20)
    label = font.render(f"Score: {score}", True, WHITE)
    surface.blit(label, (SCREEN_WIDTH + 20, 50))

    label = font.render(f"High Score: {high_score}", True, WHITE)
    surface.blit(label, (SCREEN_WIDTH + 20, 100))

    label = font.render(f"Level: {level}", True, WHITE)
    surface.blit(label, (SCREEN_WIDTH + 20, 150))

    font = pygame.font.SysFont('comicsans', 15)
    label = font.render("Press 'P' to Pause", True, WHITE)
    surface.blit(label, (SCREEN_WIDTH + 20, SCREEN_HEIGHT - 70))

    label = font.render("Press 'C' to Hold Piece", True, WHITE)
    surface.blit(label, (SCREEN_WIDTH + 20, SCREEN_HEIGHT - 50))

    # Draw held piece
    if held_piece:
        label = font.render("Held Piece:", True, WHITE)
        surface.blit(label, (SCREEN_WIDTH + 20, 200))
        format = held_piece.get_current_shape()
        for i, line in enumerate(format):
            for j, column in enumerate(line):
                if column:
                    pygame.draw.rect(surface, held_piece.color,
                                     (SCREEN_WIDTH + 20 + j * BLOCK_SIZE, 230 + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)


def main():
    # Main game function
    locked_positions = {}  # Dictionary to store locked block positions
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    paused = False
    current_piece = get_new_piece()
    next_piece = get_new_piece()
    held_piece = None
    hold_used = False  # Flag to check if hold is already used during the turn
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.25  # Base speed for falling pieces
    level_time = 0
    score = 0
    high_score = load_high_score('high_score.txt')
    level = 1
    rotate_time = 0
    rotate_delay = 100  # Delay for rotation
    soft_drop_speed = 0.1  # Speed for soft drop
    soft_drop = False  # Flag for soft drop
    
    # Smooth lateral movement variables
    move_repeat_delay = 50  # ms between repeated moves when key is held
    last_left_move = 0
    last_right_move = 0
    left_key_held = False
    right_key_held = False

    while run:
        # Create a new grid with updated locked positions
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        rotate_time += clock.get_rawtime()
        clock.tick(60)  # Limit to 60 frames per second

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    # Toggle pause
                    paused = not paused
                if not paused:
                    if event.key == pygame.K_LEFT:
                        # Move piece left immediately on key press
                        current_piece.x -= 1
                        if not valid_space(current_piece, grid):
                            current_piece.x += 1
                        left_key_held = True
                        last_left_move = pygame.time.get_ticks()
                    if event.key == pygame.K_RIGHT:
                        # Move piece right immediately on key press
                        current_piece.x += 1
                        if not valid_space(current_piece, grid):
                            current_piece.x -= 1
                        right_key_held = True
                        last_right_move = pygame.time.get_ticks()
                    if event.key == pygame.K_DOWN:
                        # Activate soft drop
                        soft_drop = True
                    if event.key == pygame.K_UP and rotate_time > rotate_delay:
                        # Rotate piece
                        current_piece.rotate()
                        #rotate_sound.play()  # Play rotate sound
                        if not valid_space(current_piece, grid):
                            current_piece.rotate_back()
                        rotate_time = 0
                    if event.key == pygame.K_c:  # Hold piece
                        if not hold_used:
                            if held_piece is None:
                                # Hold current piece and use next piece
                                held_piece = current_piece
                                current_piece = next_piece
                                next_piece = get_new_piece()
                            else:
                                # Swap current piece with held piece
                                held_piece, current_piece = current_piece, held_piece
                                current_piece.x = SCREEN_WIDTH // BLOCK_SIZE // 2 - len(current_piece.get_current_shape()[0]) // 2
                                current_piece.y = 0
                            hold_used = True  # Prevent multiple holds in one turn
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    # Deactivate soft drop
                    soft_drop = False
                if event.key == pygame.K_LEFT:
                    left_key_held = False
                if event.key == pygame.K_RIGHT:
                    right_key_held = False

        if paused:
            continue

        # Handle smooth horizontal movement based on keys held down
        current_time = pygame.time.get_ticks()
        if left_key_held and current_time - last_left_move > move_repeat_delay:
            current_piece.x -= 1
            if not valid_space(current_piece, grid):
                current_piece.x += 1
            last_left_move = current_time
        if right_key_held and current_time - last_right_move > move_repeat_delay:
            current_piece.x += 1
            if not valid_space(current_piece, grid):
                current_piece.x -= 1
            last_right_move = current_time
        if soft_drop:
            # Handle soft drop movement
            current_piece.y += 1
            #drop_sound.play()  # Play drop sound
            if not valid_space(current_piece, grid):
                current_piece.y -= 1
            fall_time = 0  # Reset fall time to maintain smooth soft drop

        # Increase difficulty over time
        if level_time / 1000 > 60:
            level_time = 0
            level += 1
            if fall_speed > 0.1:
                fall_speed -= 0.05

        # Handle piece falling based on fall speed or soft drop speed
        if fall_time / 1000 >= (soft_drop_speed if soft_drop else fall_speed):
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        # Convert shape to grid positions
        shape_pos = convert_shape_format(current_piece)

        # Add piece to the grid for drawing
        for pos in shape_pos:
            x, y = pos
            if y > -1:
                grid[y][x] = current_piece.color

        # Check if the piece hit the ground or another locked piece
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_new_piece()
            change_piece = False
            hold_used = False  # Reset hold after piece is locked
            # Check for cleared rows
            cleared = clear_rows(grid, locked_positions)
            if cleared > 0:
                if cleared == 4:
                    draw_text_middle("Tetris!", 40, WHITE, screen)
                    pygame.display.update()
                    pygame.time.delay(2000)
                # Score multiplier based on number of rows cleared
                if cleared == 1:
                    score += 100
                elif cleared == 2:
                    score += 400
                elif cleared == 3:
                    score += 600
                elif cleared == 4:
                    score += 800
                line_clear_sound.play()  # Play line clear sound

        # Check for game over
        if check_lost(locked_positions):
            game_over_sound.play()  # Play game over sound
            draw_text_middle("GAME OVER", 40, WHITE, screen)
            save_high_score('high_score.txt', score)
            pygame.display.update()
            pygame.time.delay(2000)
            run = False

        # Draw everything on the screen
        screen.fill(BLACK)
        draw_grid(screen, grid)
        draw_side_panel(screen, score, high_score, level, held_piece)

        # Draw next piece
        font = pygame.font.SysFont('comicsans', 20)
        label = font.render("Next:", True, WHITE)
        screen.blit(label, (SCREEN_WIDTH + 20, 300))
        format = next_piece.get_current_shape()
        for i, line in enumerate(format):
            for j, column in enumerate(line):
                if column:
                    pygame.draw.rect(screen, next_piece.color,
                                     (SCREEN_WIDTH + 20 + j * BLOCK_SIZE, 330 + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
