def propagate(grid, x, y):
  cell = grid[y][x]
  if not cell.collapsed:
    return
  tile = cell.options[0]
  neighbors = [
    (x, y - 1, tile.top),
    (x, y + 1, tile.bottom),
    (x - 1, y, tile.left),
    (x + 1, y, tile.right),
  ]
  for nx, ny, allowed in neighbors:
    if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid):
      neighbor = grid[ny][nx]
      if not neighbor.collapsed:
        neighbor.options = [opt for opt in neighbor.options if opt in allowed]

def find_lowest_entropy(grid):
  lowest = float('inf')
  lowest_cell = None
  for y, row in enumerate(grid):
    for x, cell in enumerate(row):
      if not cell.collapsed and len(cell.options) < lowest:
        lowest = len(cell.options)
        lowest_cell = (x, y)
  return lowest_cell

def draw_grid(screen, grid):
  offset_x, offset_y = 50, 50
  for y, row in enumerate(grid):
    for x, cell in enumerate(row):
      rect = pygame.Rect(x * TILE_SIZE + offset_x, y * TILE_SIZE + offset_y, TILE_SIZE, TILE_SIZE)
      pygame.draw.rect(screen, (200, 200, 200), rect, 1)
      if cell.collapsed:
        screen.blit(cell.options[0].image, rect.topleft)
