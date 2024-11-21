import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Define screen and grid size
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
TILE_SIZE = 50
grid_x, grid_y = SCREEN_WIDTH // TILE_SIZE, SCREEN_HEIGHT // TILE_SIZE

# Create a screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Wave Function Collapse")

# Define the Cell class
class Cell:
    def __init__(self, name, image_path, top=None, bottom=None, left=None, right=None):
        self.name = name
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.top = top or []
        self.bottom = bottom or []
        self.left = left or []
        self.right = right or []
        self.collapsed = False
        self.options = []  # This will be initialized in the grid setup

# Define all tile types as instances of the Cell class
grass = Cell("grass", r"Sprites\Grass.png")
horizontal = Cell("horizontal", r"Sprites\Horizontal_Fence.png")
vertical = Cell("vertical", r"Sprites\Vertical_Fence.png")
tl = Cell("top-left", r"Sprites\Top_Left_Fence.png")
tr = Cell("top-right", r"Sprites\Top_Right_Fence.png")
bl = Cell("bottom-left", r"Sprites\Bottom_Left_Fence.png")
br = Cell("bottom-right", r"Sprites\Bottom_Right_Fence.png")

# Define adjacency rules
horizontal.top = [grass, horizontal]
horizontal.bottom = [grass, horizontal]
horizontal.left = [tl, bl, horizontal]
horizontal.right = [tr, br, horizontal]

vertical.top = [tl, tr, vertical]
vertical.bottom = [bl, br, vertical]
vertical.left = [grass, vertical]
vertical.right = [grass, vertical]

tl.top = [grass, horizontal, br]
tl.bottom = [vertical, bl, br]
tl.left = [grass, vertical, br]
tl.right = [horizontal, tr, br]

tr.top = [grass, horizontal, bl]
tr.bottom = [vertical, bl, br]
tr.left = [tl, horizontal, br]
tr.right = [horizontal, tr, bl]

bl.top = [vertical, tl, tr]
bl.bottom = [grass, tl, tr, horizontal]
bl.left = [grass, vertical, br, tr]
bl.right = [horizontal, tr, br]

br.top = [vertical, tl, tr]
br.bottom = [grass, horizontal, tl, tr]
br.left = [horizontal, tl, bl]
br.right = [grass, vertical, tl, bl]

grass.top = [grass, horizontal, bl, br]
grass.bottom = [grass, horizontal, tl, tr]
grass.left = [grass, vertical, tr, br]
grass.right = [grass, vertical, tl, bl]

# Define the global list of all possible tiles
all_tiles = [grass, horizontal, vertical, tl, tr, bl, br]

# Initialize the grid with Cell instances
class GridCell:
    def __init__(self):
        self.collapsed = False
        self.options = all_tiles.copy()  # Initially, all tiles are possible

grid = [[GridCell() for _ in range(grid_x)] for _ in range(grid_y)]

# Helper functions for Wave Function Collapse
def check_rules(x, y):
    if x < 0 or x >= grid_x or y < 0 or y >= grid_y:
        return None
    return grid[y][x]

def collapse_cell(x, y):
    cell = grid[y][x]
    cell.collapsed = True
    cell.options = [random.choice(cell.options)]

def propagate(x, y):
    cell = grid[y][x]
    if not cell.collapsed:
        return

    tile = cell.options[0]  # The collapsed tile of this cell

    neighbors = {
        "top": (x, y - 1, tile.top),
        "bottom": (x, y + 1, tile.bottom),
        "left": (x - 1, y, tile.left),
        "right": (x + 1, y, tile.right)
    }

    for direction, (nx, ny, allowed_tiles) in neighbors.items():
        if 0 <= nx < grid_x and 0 <= ny < grid_y:
            neighbor = grid[ny][nx]
            if neighbor.collapsed:
                continue

            new_options = [opt for opt in neighbor.options if opt in allowed_tiles]
            if len(new_options) < len(neighbor.options):
                neighbor.options = new_options

def find_lowest_entropy():
    lowest_entropy = float('inf')
    lowest_cell = None
    for y in range(grid_y):
        for x in range(grid_x):
            cell = grid[y][x]
            if not cell.collapsed and 1 < len(cell.options) < lowest_entropy:
                lowest_entropy = len(cell.options)
                lowest_cell = (x, y)
    return lowest_cell

# Render the grid
def draw_grid():
    font = pygame.font.Font(None, 24)  # Set up font for displaying text
    for y in range(grid_y):
        for x in range(grid_x):
            cell = grid[y][x]
            if cell.collapsed:
                tile = cell.options[0]
                screen.blit(tile.image, (x * TILE_SIZE, y * TILE_SIZE))
            else:
                pygame.draw.rect(screen, (200, 200, 200), (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)
                # Show the number of possibilities (entropy) as text
                text = font.render(str(len(cell.options)), True, (255, 255, 255))
                screen.blit(text, (x * TILE_SIZE + TILE_SIZE // 4, y * TILE_SIZE + TILE_SIZE // 4))

# Main game loop
running = True
while running:
    screen.fill((0, 0, 0))
    draw_grid()

    # Wave Function Collapse step
    lowest_entropy_cell = find_lowest_entropy()
    if lowest_entropy_cell:
        x, y = lowest_entropy_cell
        collapse_cell(x, y)
        propagate(x, y)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()
    pygame.time.delay(50)

pygame.quit()
sys.exit()
