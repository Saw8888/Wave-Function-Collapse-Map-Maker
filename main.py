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
    'B': ['Y'],  # Blue (B) can only have Yellow (Y)
    'Y': ['G'],  # Yellow (Y) can only have Green (G)
    'G': ['GRAY'],  # Green (G) can only have Gray (Gray)
    'GRAY': []  # Gray (Gray) has no restrictions
}

# Possible tile types with their associated color
TILE_TYPES = {
    'B': BLUE,
    'Y': YELLOW,
    'G': GREEN,
    'GRAY': GRAY
}

# Create the display window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wave Function Collapse - Pygame")

# Helper function to draw the grid
def draw_grid(grid):
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            tile = grid[row][col]
            if tile:
                color = TILE_TYPES[tile]
                pygame.draw.rect(screen, color, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # Draw grid lines
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, WHITE, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, WHITE, (0, y), (WIDTH, y))

# Function to check valid neighbors based on rules
def get_valid_neighbors(tile):
    if tile in rules:
        return rules[tile]
    return []

# Function to get the neighboring cells (up, right, down, left)
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

# Function to collapse the wave function at a specific cell
def collapse(grid, possibilities, row, col):
    # Randomly pick a tile from the possible tiles for this cell
    chosen_tile = random.choice(possibilities[row][col])
    grid[row][col] = chosen_tile
    possibilities[row][col] = [chosen_tile]

    # Update neighbors based on the chosen tile
    neighbors = get_neighbors(row, col)
    for n_row, n_col in neighbors:
        if grid[n_row][n_col] is None:  # If neighbor is not yet collapsed
            valid_neighbors = get_valid_neighbors(chosen_tile)
            possibilities[n_row][n_col] = [tile for tile in possibilities[n_row][n_col] if tile in valid_neighbors]

# Main game loop
def wave_function_collapse():
    # Create a grid and initialize all cells as empty (None)
    grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    # Create a possibilities array where each cell has all possible tile types initially
    possibilities = [[list(TILE_TYPES.keys()) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Check for uncollapsed cells
        uncollapsed_cells = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if grid[r][c] is None]
        if uncollapsed_cells:
            # Select a random uncollapsed cell and collapse it
            row, col = random.choice(uncollapsed_cells)
            collapse(grid, possibilities, row, col)

        # Fill screen with black
        screen.fill((0, 0, 0))
        
        # Draw the grid
        draw_grid(grid)

        # Update display
        pygame.display.flip()

        # Delay to visualize the collapse
        pygame.time.delay(100)

    pygame.quit()

if __name__ == "__main__":
    wave_function_collapse()
