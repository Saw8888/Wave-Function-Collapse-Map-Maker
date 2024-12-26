import pygame
import random

# ---------------- CELL CLASS ----------------
class Cell:
  def __init__(self, name, image_path=None, top=None, bottom=None, left=None, right=None):
    self.name = name
    self.image = None
    if image_path:
      self.image = pygame.image.load(image_path)
    # We'll scale it when we actually draw to match TILE_SIZE
    self.top = top or []
    self.bottom = bottom or []
    self.left = left or []
    self.right = right or []
    self.collapsed = False
    self.options = []

# ---------------- INIT GRID ----------------
def init_grid(all_tiles, grid_x, grid_y):
  grid = [[Cell("") for _ in range(grid_x)] for _ in range(grid_y)]
  for y in range(grid_y):
    for x in range(grid_x):
      grid[y][x].options = all_tiles.copy()
  return grid

# ---------------- PROPAGATE ----------------
def propagate(x, y, grid, grid_x, grid_y):
  cell = grid[y][x]
  if not cell.collapsed:
    return
  tile = cell.options[0]
  neighbor_offsets = [
    (0, -1, tile.top),
    (0,  1, tile.bottom),
    (-1, 0, tile.left),
    ( 1, 0, tile.right)
  ]
  for ox, oy, allowed_tiles in neighbor_offsets:
    nx = x + ox
    ny = y + oy
    if 0 <= nx < grid_x and 0 <= ny < grid_y:
      neighbor = grid[ny][nx]
      if neighbor.collapsed:
        continue
      neighbor.options = [opt for opt in neighbor.options if opt in allowed_tiles]

# ---------------- FIND LOWEST ENTROPY ----------------
def find_lowest_entropy(grid, grid_x, grid_y):
  lowest_entropy = float('inf')
  lowest_cell = None
  for y in range(grid_y):
    for x in range(grid_x):
      cell = grid[y][x]
      if not cell.collapsed and len(cell.options) < lowest_entropy:
        lowest_entropy = len(cell.options)
        lowest_cell = (x, y)
  return lowest_cell

# ---------------- DRAW GRID ----------------
def draw_grid(screen, grid, tile_size, grid_x, grid_y):
  font = pygame.font.Font(None, 24)
  offset_x = (screen.get_width() - (grid_x * tile_size)) / 2
  offset_y = (screen.get_height() - (grid_y * tile_size)) / 2

  for y in range(grid_y):
    for x in range(grid_x):
      cell = grid[y][x]
      rect_x = offset_x + x * tile_size
      rect_y = offset_y + y * tile_size

      if cell.collapsed:
        tile = cell.options[0]
        if tile.image:
          scaled_img = pygame.transform.scale(tile.image, (tile_size, tile_size))
          screen.blit(scaled_img, (rect_x, rect_y))
      else:
        pygame.draw.rect(screen, (200, 200, 200),
                         (rect_x, rect_y, tile_size, tile_size), 1)
        text = font.render(str(len(cell.options)), True, (255, 255, 255))
        screen.blit(text, (rect_x + tile_size // 4, rect_y + tile_size // 4))
