import pygame

TILE_SIZE = 30
grid_x, grid_y = 30, 30

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

# Tile definitions
grass = Cell("grass", "Sprites/Grass.png")
horizontal = Cell("horizontal", "Sprites/Horizontal_Fence.png")
vertical = Cell("vertical", "Sprites/Vertical_Fence.png")
tl = Cell("top-left", "Sprites/Top_Left_Fence.png")
tr = Cell("top-right", "Sprites/Top_Right_Fence.png")
bl = Cell("bottom-left", "Sprites/Bottom_Left_Fence.png")
br = Cell("bottom-right", "Sprites/Bottom_Right_Fence.png")

all_tiles = [grass, horizontal, vertical, tl, tr, bl, br]

def init_grid():
  return [[Cell("") for _ in range(grid_x)] for _ in range(grid_y)]
