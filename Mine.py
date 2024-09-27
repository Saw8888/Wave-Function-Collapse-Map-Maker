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

grass = tile("Sprites/Grass")
horizontal = tile("Sprites/Horizontal_Fence")
vertical = tile("Sprites/Vertical_Fence")
tl = tile("Sprites/Top_Left_Fence")
tr = tile("Sprites/Top_Right_Fence")
bl = tile("Sprites/Bottom_Left_Fence")
br = tile("Sprites/Bottom_Right_Fence")

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
    for y in range(grid_y):
        for x in range(grid_x):
            if len(grid[y][x].possibilities) < len(grid[y_coord][x_coord].possibilities):
                x_coord = x
                y_coord = y
                
    print(grid[y_coord][x_coord].possibilities)
    return [x_coord, y_coord]

def collapse_cell(coords):
   x=coords[0]
   y=coords[1]
   tile = grid[y][x]
   tile.file = random.choice(tile.possibilities)
   for i in range(len(grid[y-1][x].possibilities)):
      if grid[y-1][x].possibilities[i] not in tile.top:
             grid[y-1][x].possibilities = grid[y-1][x].possibilities.pop(i)
   for i in range(len(grid[y+1][x].possibilities)):
      if grid[y+1][x].possibilities[i] not in tile.bottom:
             grid[y+1][x].possibilities = grid[y+1][x].possibilities.pop(i)
   for i in range(len(grid[y][x+1].possibilities)):
      if grid[y][x+1].possibilities[i] not in tile.right:
             grid[y][x+1].possibilities = grid[y][x+1].possibilities.pop(i)
   for i in range(len(grid[y][x-1].possibilities)):
      if grid[y][x-1].possibilities[i] not in tile.left:
             grid[y][x-1].possibilities = grid[y][x-1].possibilities.pop(i)

def draw_grid(grid):
  for y in range(grid_y):
    for x in range(grid_x):
      tile = grid[y][x]
      if tile.file == "":
        img = font.render(str(len(tile.possibilities)), True, (150,150,150))
        screen.blit(img, (x*tile_x, y*tile_y))
      else:
        image = pygame.image.load(tile.file)
        image = pygame.transform.scale(image, (tile_x,tile_y))
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

