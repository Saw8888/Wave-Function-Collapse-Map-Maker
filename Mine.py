import pygame
import random

pygame.init()

pygame.font.init()

font = pygame.font.SysFont(None, 30)

WIDTH, HEIGHT = 1300, 700
grid_x = 30
grid_y = 30
tile_x = 16
tile_y = 16

screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("CS IA")

possible_tiles = []

class tile:
    global possible_tiles
    def __init__(self, file):
        self.file = file
        self.right = []
        self.left = []
        self.bottom = []
        self.top = []
        self.possibilities = []
        if file not in possible_tiles:
         possible_tiles.append(file)

    def add_right(self, neibour):
        if(type(neibour) == list):
            self.right.extend(neibour)
        else:
            self.right.append(neibour)
    def add_left(self, neibour):
        if(type(neibour) == list):
            self.left.extend(neibour)
        else:
            self.left.append(neibour)
    def add_bottom(self, neibour):
        if(type(neibour) == list):
            self.bottom.extend(neibour)
        else:
            self.bottom.append(neibour)
    def add_top(self, neibour):
        if(type(neibour) == list):
            self.top.extend(neibour)
        else:
            self.top.append(neibour)

grid = [[None for x in range(grid_x)] for y in range(grid_y)]

grass = tile(r"Sprites\Grass.png")
horizontal = tile(r"Sprites\Horizontal_Fence.png")
vertical = tile(r"Sprites\Vertical_Fence.png")
tl = tile(r"Sprites\Top_Left_Fence.png")
tr = tile(r"Sprites\Top_Right_Fence.png")
bl = tile(r"Sprites\Bottom_Left_Fence.png")
br = tile(r"Sprites\Bottom_Right_Fence.png")

horizontal.add_left([tl,bl])
horizontal.add_right([tr,br])
horizontal.add_top([grass,horizontal])
horizontal.add_bottom([grass,horizontal])

vertical.add_left([grass,vertical])
vertical.add_right([grass,vertical])
vertical.add_top([tl,tr])
vertical.add_bottom([bl,br])

tl.add_left([grass,vertical])
tl.add_right([horizontal,tr,br])
tl.add_top([grass,horizontal])
tl.add_bottom([vertical, bl,br])

tr.add_left([tl,horizontal,br])
tr.add_right([horizontal,tr])
tr.add_top([grass,horizontal])
tr.add_bottom([vertical, bl,br])

bl.add_left([grass,vertical])
bl.add_right([horizontal,tl,tr])
bl.add_top([vertical,tl,bl])
bl.add_bottom([grass,vertical])

br.add_left([horizontal,tl,tr])
br.add_right([grass,vertical])
br.add_top([vertical,tr,br])
br.add_bottom([grass,vertical])

grass.add_left([grass,vertical,tl,bl])
grass.add_right([grass,vertical,tr,br])
grass.add_top([grass,horizontal,tl,tr])
grass.add_bottom([grass,horizontal,bl,br])

def init_grid():
    for y in range(grid_y):
        for x in range(grid_x):
            grid[y][x] = tile("")
            grid[y][x].possibilities = possible_tiles

def find_uncollapsed_cell():
    x_coord = random.randrange(grid_x)
    y_coord = random.randrange(grid_y)
    while len(grid[y_coord][x_coord].possibilities) <= 1:
       x_coord = random.randrange(grid_x)
       y_coord = random.randrange(grid_y)
    for y in range(grid_y):
        for x in range(grid_x):
            if (len(grid[y][x].possibilities) < len(grid[y_coord][x_coord].possibilities)) and len(grid[y][x].possibilities)>1:
                x_coord = x
                y_coord = y
                
    return [x_coord, y_coord]

def collapse_cell(coords):
  x = coords[0]
  y = coords[1]

  # Collapse the selected cell by choosing one possibility
  tile = grid[y][x]
  print(tile.possibilities)
  tile.file = random.choice(tile.possibilities)

  # After collapsing, the possibilities for this tile are reduced to the chosen one
  tile.possibilities = []

  # Propagate constraints to neighboring cells
  propagate(x, y)

def propagate(x, y):
    stack = [(x, y)]  # Stack for cells that need propagation

    while stack:
        cx, cy = stack.pop()  # Get the current cell
        current_tile = grid[cy][cx]

        # Check neighboring cells (top, bottom, left, right)
        neighbors = [
            (cx, cy - 1, current_tile.top),     # Top neighbor
            (cx, cy + 1, current_tile.bottom),  # Bottom neighbor
            (cx + 1, cy, current_tile.right),   # Right neighbor
            (cx - 1, cy, current_tile.left)     # Left neighbor
        ]

        for nx, ny, valid_tiles in neighbors:
            # Ensure the neighbor coordinates are within bounds
            if 0 <= nx < grid_x and 0 <= ny < grid_y:
                neighbor_tile = grid[ny][nx]

                # Filter out invalid possibilities for the neighbor
                new_possibilities = [
                    tile for tile in neighbor_tile.possibilities if tile in valid_tiles
                ]

                # If the neighbor's possibilities have changed, update and propagate
                if len(new_possibilities) < len(neighbor_tile.possibilities):
                    if len(new_possibilities) == 0:
                        # This means we've filtered too much and there are no valid possibilities left.
                        # This should not happen in a properly functioning WFC algorithm.
                        print(f"Error: Tile at ({nx}, {ny}) has no valid possibilities left!")
                        return

                    neighbor_tile.possibilities = new_possibilities

                    # If the neighbor is down to one possibility, collapse it and continue propagation
                    if len(neighbor_tile.possibilities) == 1:
                        neighbor_tile.file = neighbor_tile.possibilities[0]
                        neighbor_tile.possibilities = []  # Collapse the neighbor

                    # Add neighbor to stack for further propagation
                    stack.append((nx, ny))

def draw_grid(grid):
  for y in range(grid_y):
    for x in range(grid_x):
      tile = grid[y][x]
      if tile.file == "":
        img = font.render(str(len(tile.possibilities)), True, (150,150,150))
        screen.blit(img, (x*tile_x, y*tile_y))
      else:
        image = pygame.image.load(tile.file)
        grass_image = pygame.image.load(grass.file)
        image = pygame.transform.scale(image, (tile_x,tile_y))
        screen.blit(grass_image, (x*tile_x, y*tile_y))
        screen.blit(image, (x*tile_x, y*tile_y))

  for x in range(grid_x + 1): 
    pygame.draw.line(screen, (255,255,255), (x*tile_x, 0), (x*tile_x, grid_y*tile_y))

  for y in range(grid_y + 1):
    pygame.draw.line(screen, (255,255,255), (0, y*tile_y), (grid_x*tile_x, y*tile_y))

init_grid()
running = True
while running:
    screen.fill((0, 0, 0))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    draw_grid(grid)
    collapse_cell(find_uncollapsed_cell())

    pygame.display.flip()

pygame.quit()

