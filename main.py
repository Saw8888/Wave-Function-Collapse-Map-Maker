import pygame
import random
import sys
import math
import json
from tkinter import filedialog, Tk

# Local imports
from wfc import Cell, init_grid, propagate, find_lowest_entropy, draw_grid
from ui import Button
from ruleset import (
  Arrow, handle_scrolling, ruleset_Screen, draw_arrows, 
  generateRulesetFromArrows, saveRulesetToFile, loadRulesetFromFile
)

pygame.init()

# ---------------- CONSTANTS & GLOBALS ----------------
screen_x = 1080
screen_y = 1080
screen = pygame.display.set_mode((screen_x, screen_y))
pygame.display.set_caption("Wave Function Collapse")

# UI / Layout constants
TILE_SIZE = int(0.05 * screen_x)
grid_x, grid_y = 20, 20

RUN_BUTTON_POS      = (int(0.85 * screen_x), int(0.15 * screen_y))
RULESET_BUTTON_POS  = (int(0.85 * screen_x), int(0.30 * screen_y))
EXIT_BUTTON_POS     = (int(0.15 * screen_x), int(0.15 * screen_y))
SAVE_BUTTON_POS     = (int(0.85 * screen_x), int(0.50 * screen_y))
LOAD_BUTTON_POS     = (int(0.85 * screen_x), int(0.65 * screen_y))

SELECTION_X      = int(0.10 * screen_x)
SELECTION_WIDTH  = int(0.11 * screen_x)
SELECTION_HEIGHT = 400
SELECTION_Y      = (screen_y - SELECTION_HEIGHT) // 2

scroll_offset = 0
scroll_speed = 10
is_scrolling = False

tile_id_counter = 0
arrows = []
creating_arrow = None
arrow_start_tile_id = None
arrow_start_edge = None
arrow_start_pos = None

dragging_tile = None
dragging_offset = (0, 0)
placed_tiles = []

# --------------- TILE DEFINITIONS ---------------
grass      = Cell("grass",      r"Sprites\Grass.png")
horizontal = Cell("horizontal", r"Sprites\Horizontal_Fence.png")
vertical   = Cell("vertical",   r"Sprites\Vertical_Fence.png")
tl         = Cell("top-left",   r"Sprites\Top_Left_Fence.png")
tr         = Cell("top-right",  r"Sprites\Top_Right_Fence.png")
bl         = Cell("bottom-left",r"Sprites\Bottom_Left_Fence.png")
br         = Cell("bottom-right",r"Sprites\Bottom_Right_Fence.png")
all_tiles  = [grass, horizontal, vertical, tl, tr, bl, br]

# --------------- SET UP FONTS & BUTTONS ---------------
main_font = pygame.font.SysFont("cambria", int(screen_x * 0.03))
button_surface = pygame.image.load("Sprites/button.png")
button_surface = pygame.transform.scale(button_surface, (int(0.1 * screen_x), int(0.05 * screen_y)))

run_button               = Button(button_surface, RUN_BUTTON_POS[0],      RUN_BUTTON_POS[1],      "RUN",     main_font)
ruleset_button           = Button(button_surface, RULESET_BUTTON_POS[0],  RULESET_BUTTON_POS[1],  "RULESET", main_font)
exit_ruleset_screen_btn  = Button(button_surface, EXIT_BUTTON_POS[0],     EXIT_BUTTON_POS[1],     "EXIT",    main_font)
save_ruleset_button      = Button(button_surface, SAVE_BUTTON_POS[0],     SAVE_BUTTON_POS[1],     "SAVE",    main_font)
load_ruleset_button      = Button(button_surface, LOAD_BUTTON_POS[0],     LOAD_BUTTON_POS[1],     "LOAD",    main_font)

# For saving/loading with Tk
tk_root = Tk()
tk_root.withdraw()
tk_root.attributes("-topmost", True)

def main():
  running = True
  WFC_running = 0
  ruleset_screen = False
  lowest_entropy_cell = True

  # Initialize the grid (used by the WFC)
  grid = init_grid(all_tiles, grid_x, grid_y)

  while running:
    screen.fill((0, 0, 0))
    draw_grid(screen, grid, TILE_SIZE, grid_x, grid_y)

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_q:
          running = False
      # Handle scrolling if needed
      handle_scrolling(event, all_tiles, TILE_SIZE)

    # Check main menu button inputs
    if run_button.checkForInput():
      WFC_running += 1
    elif ruleset_button.checkForInput():
      ruleset_screen = True

    # Wave Function Collapse logic
    if WFC_running == 1:
      # Build adjacency data from the arrows
      generateRulesetFromArrows(placed_tiles, arrows)
      # Re-init the grid so WFC uses the new adjacency
      grid = init_grid(all_tiles, grid_x, grid_y)

      # Simple WFC approach
      while lowest_entropy_cell:
        screen.fill((0, 0, 0))
        lowest_entropy_cell = find_lowest_entropy(grid, grid_x, grid_y)
        if lowest_entropy_cell:
          x, y = lowest_entropy_cell
          cell = grid[y][x]
          cell.collapsed = True
          cell.options = [random.choice(cell.options)]
          propagate(x, y, grid, grid_x, grid_y)
        draw_grid(screen, grid, TILE_SIZE, grid_x, grid_y)
        pygame.display.flip()

      WFC_running = 0
      lowest_entropy_cell = True

    # Handle the ruleset screen in a separate sub-loop
    if ruleset_screen:
      exit_ruleset_screen = False
      while not exit_ruleset_screen:
        screen.fill((0, 0, 0))

        if exit_ruleset_screen_btn.checkForInput():
          exit_ruleset_screen = True
          ruleset_screen = False

        for event in pygame.event.get():
          handle_scrolling(event, all_tiles, TILE_SIZE)
          if event.type == pygame.QUIT:
            exit_ruleset_screen = True
            ruleset_screen = False
            running = False
          if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
              exit_ruleset_screen = True
              ruleset_screen = False
              running = False

        # Draw the entire ruleset screen (tiles, panel, dragging, etc.)
        ruleset_Screen(
          screen, all_tiles, placed_tiles, tile_id_counter,
          TILE_SIZE, scroll_offset, scroll_speed, is_scrolling,
          dragging_tile, dragging_offset, creating_arrow,
          arrow_start_tile_id, arrow_start_edge, arrow_start_pos
        )
        # Draw the arrows currently placed
        draw_arrows(screen, placed_tiles, arrows, TILE_SIZE)

        # Check save/load
        save_ruleset_button.update(screen)
        if save_ruleset_button.checkForInput():
          saveRulesetToFile(placed_tiles, arrows)

        load_ruleset_button.update(screen)
        if load_ruleset_button.checkForInput():
          loadRulesetFromFile(all_tiles, placed_tiles, arrows)

        exit_ruleset_screen_btn.update(screen)
        pygame.display.flip()

    # Draw main menu buttons (RUN, RULESET, etc.)
    run_button.update(screen)
    ruleset_button.update(screen)

    pygame.display.flip()

  pygame.quit()
  sys.exit()

if __name__ == "__main__":
  main()
