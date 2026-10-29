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

class Tetromino:
    def __init__(self, shape):
        self.shape = shape
        self.rotations = TETROMINOES[shape]
        self.rotation = 0
        self.color = COLORS[list(TETROMINOES.keys()).index(shape)]
        self.x = SCREEN_WIDTH // BLOCK_SIZE // 2 - len(self.get_current_shape()[0]) // 2
        self.y = 0

    def get_current_shape(self):
        return self.rotations[self.rotation]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.rotations)

    def rotate_back(self):
        self.rotation = (self.rotation - 1) % len(self.rotations)

def create_grid(locked_positions={}):
    grid = [[BLACK for _ in range(SCREEN_WIDTH // BLOCK_SIZE)] for _ in range(SCREEN_HEIGHT // BLOCK_SIZE)]
    for y in range(SCREEN_HEIGHT // BLOCK_SIZE):
        for x in range(SCREEN_WIDTH // BLOCK_SIZE):
            if (x, y) in locked_positions:
                grid[y][x] = locked_positions[(x, y)]
    return grid

def convert_shape_format(shape):
    positions = []
    format = shape.get_current_shape()
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column:
                positions.append((shape.x + j, shape.y + i))
    return positions

def valid_space(shape, grid):
    accepted_positions = [[(x, y) for x in range(SCREEN_WIDTH // BLOCK_SIZE) if grid[y][x] == BLACK] for y in range(SCREEN_HEIGHT // BLOCK_SIZE)]
    accepted_positions = [x for sub in accepted_positions for x in sub]
    formatted = convert_shape_format(shape)
    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] >= 0:
                return False
    return True

def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False

def clear_rows(grid, locked):
    cleared = 0
    for y in range(len(grid)-1, -1, -1):
        row = grid[y]
        if BLACK not in row:
            cleared += 1
            del grid[y]
            grid.insert(0, [BLACK for _ in range(SCREEN_WIDTH // BLOCK_SIZE)])
            # Update locked positions
            keys_to_remove = [pos for pos in locked if pos[1] == y]
            for key in keys_to_remove:
                del locked[key]
            # Shift down the locked positions
            new_locked = {}
            for pos in locked:
                x, y_pos = pos
                if y_pos < y:
                    new_locked[(x, y_pos + 1)] = locked[pos]
                else:
                    new_locked[pos] = locked[pos]
            locked.clear()
            locked.update(new_locked)
    return cleared

def get_new_piece():
    return Tetromino(random.choice(list(TETROMINOES.keys())))

def draw_grid(surface, grid):
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
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            f.write("0")
    with open(file_path, 'r') as f:
        try:
            return int(f.read())
        except ValueError:
            return 0

def save_high_score(file_path, score):
    high_score = load_high_score(file_path)
    if score > high_score:
        with open(file_path, 'w') as f:
            f.write(str(score))

def draw_text_middle(text, size, color, surface):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, True, color)
    surface.blit(label, (SCREEN_WIDTH//2 - label.get_width()//2, SCREEN_HEIGHT//2 - label.get_height()//2))

def draw_side_panel(surface, score, high_score, level):
    font = pygame.font.SysFont('comicsans', 20)
    label = font.render(f"Score: {score}", True, WHITE)
    surface.blit(label, (SCREEN_WIDTH + 20, 50))

    label = font.render(f"High Score: {high_score}", True, WHITE)
    surface.blit(label, (SCREEN_WIDTH + 20, 100))

    label = font.render(f"Level: {level}", True, WHITE)
    surface.blit(label, (SCREEN_WIDTH + 20, 150))

    font = pygame.font.SysFont('comicsans', 15)
    label = font.render("Press 'P' to Pause", True, WHITE)
    surface.blit(label, (SCREEN_WIDTH + 20, SCREEN_HEIGHT - 50))

# Load sounds
line_clear_sound_path = os.path.join('sounds', 'line_clear.wav')
game_over_sound_path = os.path.join('sounds', 'game_over.wav')
line_clear_sound = pygame.mixer.Sound(line_clear_sound_path) if os.path.exists(line_clear_sound_path) else None
game_over_sound = pygame.mixer.Sound(game_over_sound_path) if os.path.exists(game_over_sound_path) else None

def main():
    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    paused = False
    current_piece = get_new_piece()
    next_piece = get_new_piece()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.25
    level_time = 0
    score = 0
    high_score = load_high_score('high_score.txt')
    level = 1
    move_time = 0
    rotate_time = 0
    move_delay = 100

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        move_time += clock.get_rawtime()
        rotate_time += clock.get_rawtime()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                if not paused:
                    if event.key == pygame.K_LEFT and move_time > move_delay:
                        current_piece.x -= 1
                        if not valid_space(current_piece, grid):
                            current_piece.x += 1
                        move_time = 0
                    if event.key == pygame.K_RIGHT and move_time > move_delay:
                        current_piece.x += 1
                        if not valid_space(current_piece, grid):
                            current_piece.x -= 1
                        move_time = 0
                    if event.key == pygame.K_DOWN and move_time > move_delay:
                        current_piece.y += 1
                        if not valid_space(current_piece, grid):
                            current_piece.y -= 1
                        move_time = 0
                    if event.key == pygame.K_UP and rotate_time > move_delay:
                        current_piece.rotate()
                        if not valid_space(current_piece, grid):
                            current_piece.rotate_back()
                        rotate_time = 0

        if paused:
            continue

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and move_time > move_delay:
            current_piece.x -= 1
            if not valid_space(current_piece, grid):
                current_piece.x += 1
            move_time = 0
        if keys[pygame.K_RIGHT] and move_time > move_delay:
            current_piece.x += 1
            if not valid_space(current_piece, grid):
                current_piece.x -= 1
            move_time = 0
        if keys[pygame.K_DOWN] and move_time > move_delay:
            current_piece.y += 1
            if not valid_space(current_piece, grid):
                current_piece.y -= 1
            move_time = 0
        if keys[pygame.K_UP] and rotate_time > move_delay:
            current_piece.rotate()
            if not valid_space(current_piece, grid):
                current_piece.rotate_back()
            rotate_time = 0

        # Increase difficulty over time
        if level_time / 1000 > 60:
            level_time = 0
            level += 1
            if fall_speed > 0.1:
                fall_speed -= 0.05

        # Handle piece falling
        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        shape_pos = convert_shape_format(current_piece)

        # Add piece to the grid for drawing
        for pos in shape_pos:
            x, y = pos
            if y > -1:
                grid[y][x] = current_piece.color

        # Check if piece hit the ground
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_new_piece()
            change_piece = False
            # Check for cleared rows
            while True:
                cleared = clear_rows(grid, locked_positions)
                if cleared == 0:
                    break
                score += cleared * 100
                if line_clear_sound:
                    line_clear_sound.play()

        # Check for game over
        if check_lost(locked_positions):
            if game_over_sound:
                game_over_sound.play()
            draw_text_middle("GAME OVER", 40, WHITE, screen)
            save_high_score('high_score.txt', score)
            pygame.display.update()
            pygame.time.delay(2000)
            run = False

        # Draw everything
        screen.fill(BLACK)
        draw_grid(screen, grid)
        draw_side_panel(screen, score, high_score, level)

        # Draw next piece
        font = pygame.font.SysFont('comicsans', 20)
        label = font.render("Next:", True, WHITE)
        screen.blit(label, (SCREEN_WIDTH + 20, 200))
        format = next_piece.get_current_shape()
        for i, line in enumerate(format):
            for j, column in enumerate(line):
                if column:
                    pygame.draw.rect(screen, next_piece.color,
                                     (SCREEN_WIDTH + 20 + j * BLOCK_SIZE, 230 + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
