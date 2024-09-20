import pygame
import random

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 10
CELL_SIZE = WIDTH // GRID_SIZE

# Colors
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
GRAY = (169, 169, 169)
WHITE = (255, 255, 255)

# Rule constraints
rules = {
    'B': [['Y']],  
    'Y': [['G']], 
    'G': [['GRAY']],
    'GRAY': []
}

TILE_TYPES = {
    'B': BLUE,
    'Y': YELLOW,
    'G': GREEN,
    'GRAY': GRAY
}

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wave Function Collapse - Pygame")

def draw_grid(grid):
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            tile = grid[row][col]
            if tile:
                color = TILE_TYPES[tile]
                pygame.draw.rect(screen, color, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, WHITE, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, WHITE, (0, y), (WIDTH, y))

def get_valid_neighbors(tile):
    if tile in rules:
        return rules[tile]
    return []

def get_neighbors(row, col):
    neighbors = []
    if row > 0:  # Up
        neighbors.append((row - 1, col))
    if col < GRID_SIZE - 1:  # Right
        neighbors.append((row, col + 1))
    if row < GRID_SIZE - 1:  # Down
        neighbors.append((row + 1, col))
    if col > 0:  # Left
        neighbors.append((row, col - 1))
    return neighbors


def collapse(grid, possibilities, row, col):
    chosen_tile = random.choice(possibilities[row][col])
    grid[row][col] = chosen_tile
    possibilities[row][col] = [chosen_tile]

    neighbors = get_neighbors(row, col)
    for n_row, n_col in neighbors:
        if grid[n_row][n_col] is None:
            valid_neighbors = get_valid_neighbors(chosen_tile)
            possibilities[n_row][n_col] = [tile for tile in possibilities[n_row][n_col] if tile in valid_neighbors]


def wave_function_collapse():
    # Create a grid and initialize all cells as empty (None)
    grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    possibilities = [[list(TILE_TYPES.keys()) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        uncollapsed_cells = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if grid[r][c] is None]
        if uncollapsed_cells:

            row, col = random.choice(uncollapsed_cells)
            collapse(grid, possibilities, row, col)

        screen.fill((0, 0, 0))

        draw_grid(grid)

        pygame.display.flip()

        pygame.time.delay(100)

    pygame.quit()

if __name__ == "__main__":
    wave_function_collapse()
