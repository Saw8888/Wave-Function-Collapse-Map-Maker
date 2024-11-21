import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Define screen and grid size
TILE_SIZE = 30
grid_x, grid_y = 30,30
# Create a screen
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Wave Function Collapse")


class Cell:
    def __init__(self, name, image_path=None, top=None, bottom=None, left=None, right=None):
        self.name = name
        self.image = None
        if image_path:
            self.image = pygame.image.load(image_path)
            self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.top = top or []
        self.bottom = bottom or []
        self.left = left or []
        self.right = right or []
        self.collapsed = False
        self.options = []

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

all_tiles = [grass, horizontal, vertical, tl, tr, bl, br]

# Initialize the grid
def init_grid():
    grid = [[Cell("") for _ in range(grid_x)] for _ in range(grid_y)]
    for y in range(grid_y):
        for x in range(grid_x):
            grid[y][x].options = all_tiles.copy()
    return grid

grid = init_grid()

def propagate(x, y):
    cell = grid[y][x]
    if not cell.collapsed:
        return

    tile = cell.options[0]

    neighbor_offsets = [
        [0, -1, tile.top], 
        [0, 1, tile.bottom],
        [-1, 0, tile.left],
        [1, 0, tile.right] 
    ]

    for offset in neighbor_offsets:
        offset_x, offset_y, allowed_tiles = offset
        neighbor_x = x + offset_x
        neighbor_y = y + offset_y

        if 0 <= neighbor_x < grid_x and 0 <= neighbor_y < grid_y: #nOt out of bounds
            neighbor = grid[neighbor_y][neighbor_x]
            if neighbor.collapsed:
                continue

            new_options = []
            for option in neighbor.options:
                if option in allowed_tiles:
                    new_options.append(option)

            neighbor.options = new_options


def find_lowest_entropy(grid):
    lowest_entropy = float('inf')
    lowest_cell = None
    for y in range(grid_y):
        for x in range(grid_x):
            cell = grid[y][x]
            if not cell.collapsed and len(cell.options) < lowest_entropy:
                lowest_entropy = len(cell.options)
                lowest_cell = (x, y)
    return lowest_cell

def draw_grid():
    font = pygame.font.Font(None, 24)
    offset_x = (screen.get_width()-(grid_x*TILE_SIZE))/2
    offset_y = (screen.get_height()-(grid_y*TILE_SIZE))/2
    for y in range(grid_y):
        for x in range(grid_x):
            cell = grid[y][x]
            if cell.collapsed:
                tile = cell.options[0]
                screen.blit(tile.image, (x * TILE_SIZE + offset_x, y * TILE_SIZE + offset_y))
            else:
                pygame.draw.rect(screen, (200, 200, 200), (x * TILE_SIZE + offset_x, y * TILE_SIZE + offset_y, TILE_SIZE, TILE_SIZE), 1)
                text = font.render(str(len(cell.options)), True, (255, 255, 255))
                screen.blit(text, (x * TILE_SIZE + TILE_SIZE // 4 + offset_x, y * TILE_SIZE + TILE_SIZE // 4 + offset_y))



main_font = pygame.font.SysFont("cambria", 50)

class Button():
    def __init__(self, image, x_pos, y_pos, text_input):
        self.image = image
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_input = text_input
        self.text = main_font.render(self.text_input, True, "white")
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

    def update(self):
       screen.blit(self.image, self.rect)
       screen.blit(self.text, self.text_rect)

    def checkForInput(self):
       position = pygame.mouse.get_pos()
       if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom) and pygame.mouse.get_pressed()[0]:
        return True

    def changeColor(self):
        position = pygame.mouse.get_pos()
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
         self.text = main_font.render(self.text_input, True, "green")
        else:
         self.text = main_font.render(self.text_input, True, "white")

button_surface = pygame.image.load("Sprites/button.png")
button_surface = pygame.transform.scale(button_surface, (250, 120))

run_button = Button(button_surface,1650,200,"RUN")
ruleset_button = Button(button_surface,1650,350,"RULESET")
exit_ruleset_screen_button = Button(button_surface,1650,350,"EXIT")

running = True
WFC_running = 0
ruleset_screen = False
lowest_entropy_cell = True
while running:
    screen.fill((0, 0, 0))
    draw_grid()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
    
    if run_button.checkForInput() == True:
        WFC_running += 1
    elif ruleset_button.checkForInput() == True:
        ruleset_screen = True

    if WFC_running == 1:
        grid = init_grid()
        while lowest_entropy_cell:
            screen.fill((0, 0, 0))
            lowest_entropy_cell = find_lowest_entropy(grid)
            if lowest_entropy_cell:
                x, y = lowest_entropy_cell
                cell = grid[y][x]
                cell.collapsed = True
                cell.options = [random.choice(cell.options)]
                propagate(x, y)
            draw_grid()
            pygame.display.flip()
        WFC_running = 0
        lowest_entropy_cell = True

    if ruleset_screen == True:
        exit_ruleset_screen = False

        while not exit_ruleset_screen:
            screen.fill((0, 0, 0))
            if exit_ruleset_screen_button.checkForInput() == True:
                exit_ruleset_screen = True
                ruleset_screen = False
                print("aa")
                
            exit_ruleset_screen_button.update()
            pygame.display.flip()
                


    run_button.update()
    ruleset_button.update()
    pygame.display.flip()
pygame.quit()
sys.exit()
