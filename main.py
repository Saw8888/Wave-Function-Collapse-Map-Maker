import pygame
import random

pygame.init()

# Screen settings
WIDTH, HEIGHT = 600, 600
grid_x = 30
grid_y = 30
tile_x = 16
tile_y = 16

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CS IA")

# Define the Tile class
class tile:
    def __init__(self, file):
        self.file = file
        self.right = []
        self.left = []
        self.bottom = []
        self.top = []

    def right(self, neibour):
        if(type(neibour) == list):
            self.right.extend(neibour)
        else:
            self.right.append(neibour)
    def left(self, neibour):
        if(type(neibour) == list):
            self.left.extend(neibour)
        else:
            self.left.append(neibour)
    def bottom(self, neibour):
        if(type(neibour) == list):
            self.bottom.extend(neibour)
        else:
            self.bottom.append(neibour)
    def top(self, neibour):
        if(type(neibour) == list):
            self.top.extend(neibour)
        else:
            self.top.append(neibour)

grass = tile("Sprites/Grass")
horizontal = tile("Sprites/Horizontal_Fence")
vertical = tile("Sprites/Vertical_Fence")
tl = tile("Sprites/Top_Left_Fence")
tr = tile("Sprites/Top_Right_Fence")
bl = tile("Sprites/Bottom_Left_Fence")
br = tile("Sprites/Bottom_Right_Fence")

horizontal.left([tl,bl])
horizontal.right([tr,br])
horizontal.top([grass,horizontal])
horizontal.bottom([grass,horizontal])

vertical.left([grass,vertical])
vertical.right([grass,vertical])
vertical.top([tl,tr])
vertical.bottom([bl,br])

tl.left([grass,vertical])
tl.right([horizontal,tr,br])
tl.top([grass,horizontal])
tl.bottom([vertical, bl,br])

tr.left([tl,horizontal,br])
tr.right([horizontal,tr])
tr.top([grass,horizontal])
tr.bottom([vertical, bl,br])

bl.left([grass,vertical])
bl.right([horizontal,tl,tr])
bl.top([vertical,tl,bl])
bl.bottom([grass,vertical])

br.left([horizontal,tl,tr])
br.right([grass,vertical])
br.top([vertical,tr,br])
br.bottom([grass,vertical])

grass.left([grass,vertical,tl,bl])
grass.right([grass,vertical,tr,br])
grass.top([grass,horizontal,tl,tr])
grass.bottom([grass,horizontal,bl,br])

# List of all tile types
all_tiles = [grass, horizontal, vertical, tl, tr, bl, br]

# WFC Algorithm (simplified)
class WFC:
    def __init__(self, grid_width, grid_height, tiles):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.tiles = tiles
        self.grid = [[self.initialize_tile_options() for _ in range(grid_height)] for _ in range(grid_width)]

    def initialize_tile_options(self):
        """Each grid cell starts with all possible tiles (uncollapsed)."""
        return list(self.tiles)

    def collapse_tile(self, x, y):
        """Collapse a single tile at grid[x][y]."""
        possible_tiles = self.grid[x][y]

        # Randomly select a tile if it's not collapsed yet
        if len(possible_tiles) > 1:
            selected_tile = random.choice(possible_tiles)
            self.grid[x][y] = [selected_tile]  # Collapse to this tile
            self.propagate_constraints(x, y, selected_tile)

    def propagate_constraints(self, x, y, tile):
        """Propagate constraints to neighboring tiles after collapsing a tile."""
        # Check and update the right neighbor
        if x < self.grid_width - 1:
            self.update_neighbors(x + 1, y, tile.right)

        # Check and update the left neighbor
        if x > 0:
            self.update_neighbors(x - 1, y, tile.left)

        # Check and update the top neighbor
        if y > 0:
            self.update_neighbors(x, y - 1, tile.top)

        # Check and update the bottom neighbor
        if y < self.grid_height - 1:
            self.update_neighbors(x, y + 1, tile.bottom)

    def update_neighbors(self, x, y, allowed_neighbors):
        """Reduce the tile options for a neighboring cell based on allowed neighbors."""
        current_options = self.grid[x][y]
        self.grid[x][y] = [tile for tile in current_options if tile in allowed_neighbors]

    def is_fully_collapsed(self):
        """Check if all grid cells have been collapsed."""
        return all(len(self.grid[x][y]) == 1 for x in range(self.grid_width) for y in range(self.grid_height))

    def collapse(self):
        """Main loop to collapse the entire grid step by step."""
        while not self.is_fully_collapsed():
            # Find a random cell to collapse
            x, y = self.find_uncollapsed_cell()
            if x is None:
                break

            # Collapse the tile at this cell
            self.collapse_tile(x, y)

    def find_uncollapsed_cell(self):
        """Find a random uncollapsed cell in the grid."""
        uncollapsed_cells = [(x, y) for x in range(self.grid_width) for y in range(self.grid_height) if len(self.grid[x][y]) > 1]
        return random.choice(uncollapsed_cells) if uncollapsed_cells else (None, None)

    def draw(self):
        """Draw the grid."""
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                if len(self.grid[x][y]) == 1:  # If collapsed, draw the tile
                    tile = self.grid[x][y][0]
                    image = pygame.image.load(tile.file)
                    image = pygame.transform.scale(image, (tile_x, tile_y))
                    screen.blit(image, (x * tile_x, y * tile_y))


# Initialize the WFC grid
wfc = WFC(grid_x, grid_y, all_tiles)

# Main game loop
running = True
while running:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Collapse the grid and draw it
    wfc.collapse()
    wfc.draw()

    pygame.display.flip()

pygame.quit()

