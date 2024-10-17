import pygame
import random

# Initialize Pygame
pygame.init()
pygame.font.init()
pygame.mixer.init()

# Game Constants
CELL_SIZE = 30
COLS = 10
ROWS = 20
WIDTH = CELL_SIZE * COLS
HEIGHT = CELL_SIZE * ROWS
SIDE_WIDTH = 200
WINDOW_WIDTH = WIDTH + SIDE_WIDTH
WINDOW_HEIGHT = HEIGHT
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
COLORS = [
    (0, 255, 255),  # I
    (255, 255, 0),  # O
    (128, 0, 128),  # T
    (0, 255, 0),  # S
    (255, 0, 0),  # Z
    (0, 0, 255),  # J
    (255, 165, 0)  # L
]

# Load Sounds
try:
    #move_sound = pygame.mixer.Sound('sounds/move.wav')
    #rotate_sound = pygame.mixer.Sound('sounds/rotate.wav')
    move_sound = rotate_sound = None
    clear_sound = pygame.mixer.Sound('../Sounds/clear.wav')
    game_over_sound = pygame.mixer.Sound('../Sounds/game_over.wav')
except:
    print("Sound files not found. Continuing without sounds.")
    move_sound = rotate_sound = clear_sound = game_over_sound = None

# Define Tetromino shapes
S = [['.....',
      '.....',
      '..XX.',
      '.XX..',
      '.....'],
     ['.....',
      '..X..',
      '..XX.',
      '...X.',
      '.....']]

Z = [['.....',
      '.....',
      '.XX..',
      '..XX.',
      '.....'],
     ['.....',
      '..X..',
      '.XX..',
      '.X...',
      '.....']]

I = [['..X..',
      '..X..',
      '..X..',
      '..X..',
      '.....'],
     ['.....',
      'XXXX.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.XX..',
      '.XX..',
      '.....']]

J = [['.....',
      '.X...',
      '.XXX.',
      '.....',
      '.....'],
     ['.....',
      '..XX.',
      '..X..',
      '..X..',
      '.....'],
     ['.....',
      '.....',
      '.XXX.',
      '...X.',
      '.....'],
     ['.....',
      '..X..',
      '..X..',
      '.XX..',
      '.....']]

L = [['.....',
      '...X.',
      '.XXX.',
      '.....',
      '.....'],
     ['.....',
      '..X..',
      '..X..',
      '..XX.',
      '.....'],
     ['.....',
      '.....',
      '.XXX.',
      '.X...',
      '.....'],
     ['.....',
      '.XX..',
      '..X..',
      '..X..',
      '.....']]

T = [['.....',
      '..X..',
      '.XXX.',
      '.....',
      '.....'],
     ['.....',
      '..X..',
      '..XX.',
      '..X..',
      '.....'],
     ['.....',
      '.....',
      '.XXX.',
      '..X..',
      '.....'],
     ['.....',
      '..X..',
      '.XX..',
      '..X..',
      '.....']]

SHAPES = [S, Z, I, O, J, L, T]
SHAPE_COLORS = COLORS


# Tetromino Class
class Tetromino:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = SHAPE_COLORS[SHAPES.index(shape)]
        self.rotation = 0

    def image(self):
        return self.shape[self.rotation % len(self.shape)]

    def get_cells(self):
        positions = []
        format = self.image()

        for i, line in enumerate(format):
            row = list(line)
            for j, column in enumerate(row):
                if column == 'X':
                    positions.append((self.x + j - 2, self.y + i - 4))
        return positions


# Game Functions
def create_grid(locked_positions={}):
    grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]
    for (x, y), color in locked_positions.items():
        if y >= 0:
            grid[y][x] = color
    return grid


def convert_shape_format(shape):
    positions = shape.get_cells()
    return positions


def valid_space(shape, grid):
    accepted_positions = [[(x, y) for x in range(COLS) if grid[y][x] == BLACK] for y in range(ROWS)]
    accepted_positions = [x for sub in accepted_positions for x in sub]
    formatted = convert_shape_format(shape)

    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False
    return True


def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False


def get_shape():
    return Tetromino(5, 0, random.choice(SHAPES))


def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, 1, color)
    surface.blit(label, (WIDTH / 2 - label.get_width() / 2, HEIGHT / 2 - label.get_height() / 2))


def draw_grid(surface, grid):
    for y in range(ROWS):
        for x in range(COLS):
            pygame.draw.rect(surface, grid[y][x],
                             (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 0)

    # Draw grid lines
    for y in range(ROWS):
        pygame.draw.line(surface, GRAY, (0, y * CELL_SIZE), (WIDTH, y * CELL_SIZE))
    for x in range(COLS):
        pygame.draw.line(surface, GRAY, (x * CELL_SIZE, 0), (x * CELL_SIZE, HEIGHT))


def clear_rows(grid, locked):
    inc = 0
    for y in range(len(grid) - 1, -1, -1):
        row = grid[y]
        if BLACK not in row:
            inc += 1
            # Clear the row
            del grid[y]
            grid.insert(0, [BLACK for _ in range(COLS)])
            # Remove locked positions
            keys = sorted([key for key in locked], key=lambda x: x[1])[::-1]
            for key in keys:
                x, y_pos = key
                if y_pos < y:
                    new_key = (x, y_pos + 1)
                    locked[new_key] = locked.pop(key)
    return inc


def draw_window(surface, grid, score=0, next_shape=None):
    surface.fill(BLACK)

    # Draw grid and locked positions
    draw_grid(surface, grid)

    # Draw score
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render(f"Score: {score}", 1, WHITE)
    surface.blit(label, (WIDTH + 20, HEIGHT / 2 - 100))

    # Draw next shape
    if next_shape:
        label = font.render("Next:", 1, WHITE)
        surface.blit(label, (WIDTH + 20, HEIGHT / 2 - 50))
        format = next_shape.image()
        for i, line in enumerate(format):
            row = list(line)
            for j, column in enumerate(row):
                if column == 'X':
                    pygame.draw.rect(surface, next_shape.color,
                                     (
                                     WIDTH + 20 + j * CELL_SIZE, HEIGHT / 2 - 50 + i * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                                     0)

    # Draw border
    pygame.draw.rect(surface, WHITE, (0, 0, WIDTH, HEIGHT), 5)
    pygame.draw.rect(surface, WHITE, (WIDTH, 0, SIDE_WIDTH, HEIGHT), 5)

    pygame.display.update()


def main(win):
    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27
    level_time = 0
    score = 0

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick(FPS)

        # Increase speed over time
        if level_time / 1000 > 5:
            level_time = 0
            if fall_speed > 0.12:
                fall_speed -= 0.005

        # Handle falling
        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not (valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                    else:
                        if move_sound:
                            move_sound.play()

                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                    else:
                        if move_sound:
                            move_sound.play()

                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                    else:
                        if move_sound:
                            move_sound.play()

                elif event.key == pygame.K_UP:
                    current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = (current_piece.rotation - 1) % len(current_piece.shape)
                    else:
                        if rotate_sound:
                            rotate_sound.play()

                elif event.key == pygame.K_SPACE:
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1
                    if move_sound:
                        move_sound.play()

        shape_pos = convert_shape_format(current_piece)

        # Add piece to the grid for drawing
        for x, y in shape_pos:
            if y > -1:
                grid[y][x] = current_piece.color

        # Check if piece is landed
        if change_piece:
            for pos in shape_pos:
                locked_positions[pos] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            # Clear rows
            cleared = clear_rows(grid, locked_positions)
            if cleared > 0:
                if clear_sound:
                    clear_sound.play()
                score += {1: 100, 2: 300, 3: 500, 4: 800}.get(cleared, 0)

        draw_window(win, grid, score, next_piece)

        if check_lost(locked_positions):
            if game_over_sound:
                game_over_sound.play()
            draw_text_middle(win, "GAME OVER", 80, WHITE)
            pygame.display.update()
            pygame.time.delay(2000)
            run = False


def main_menu(win):
    run = True
    while run:
        win.fill(BLACK)
        draw_text_middle(win, "Press Any Key To Play", 60, WHITE)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main(win)
    pygame.quit()


win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Tetris')

main_menu(win)
