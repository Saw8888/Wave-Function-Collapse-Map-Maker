import pygame
import random
import sys
import math
import json
from tkinter import filedialog, Tk

pygame.init()

TILE_SIZE = 20
grid_x, grid_y = 20,20
screen_x = 1080
screen_y = 640

screen = pygame.display.set_mode((screen_x, screen_y))
pygame.display.set_caption("Wave Function Collapse")

tile_id_counter = 0

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

grass = Cell("grass", r"Sprites\Grass.png")
horizontal = Cell("horizontal", r"Sprites\Horizontal_Fence.png")
vertical = Cell("vertical", r"Sprites\Vertical_Fence.png")
tl = Cell("top-left", r"Sprites\Top_Left_Fence.png")
tr = Cell("top-right", r"Sprites\Top_Right_Fence.png")
bl = Cell("bottom-left", r"Sprites\Bottom_Left_Fence.png")
br = Cell("bottom-right", r"Sprites\Bottom_Right_Fence.png")

all_tiles = [grass, horizontal, vertical, tl, tr, bl, br]
 
scroll_offset = 0
scroll_speed = 10
is_scrolling = False

dragging_tile = None
dragging_offset = (0, 0)

placed_tiles = []

creating_arrow = None
arrow_start_tile_id = None
arrow_start_edge = None
arrow_start_pos = None

arrows = []

class Arrow:
 def __init__(self, start_tile_id, start_edge, end_tile_id=None, end_edge=None):
  self.start_tile_id = start_tile_id
  self.start_edge = start_edge
  self.end_tile_id = end_tile_id
  self.end_edge = end_edge
  self.start_pos = None
  self.end_pos = None

 def draw(self, screen):
  """Draw the arrow as a line with an arrowhead."""
  if self.start_pos and self.end_pos:
    pygame.draw.line(screen, (0, 255, 0), self.start_pos, self.end_pos, 2)

    # Arrowhead
    arrow_length = 10
    angle = math.atan2(self.end_pos[1] - self.start_pos[1], self.end_pos[0] - self.start_pos[0])
    arrow_tip = self.end_pos
    arrow_left = (arrow_tip[0] - arrow_length * math.cos(angle - math.pi / 6),
                  arrow_tip[1] - arrow_length * math.sin(angle - math.pi / 6))
    arrow_right = (arrow_tip[0] - arrow_length * math.cos(angle + math.pi / 6),
                   arrow_tip[1] - arrow_length * math.sin(angle + math.pi / 6))
    pygame.draw.polygon(screen, (0, 255, 0), [arrow_tip, arrow_left, arrow_right])


def draw_arrows():
 #Draw all arrows each frame, so they follow their tiles
 for arrow in arrows:
  start_found = [(t, x, y, tid) for (t, x, y, tid) in placed_tiles if tid == arrow.start_tile_id]
  end_found = [(t, x, y, tid) for (t, x, y, tid) in placed_tiles if tid == arrow.end_tile_id]

  if len(start_found) == 1 and len(end_found) == 1:
    _, start_tile_x, start_tile_y, _ = start_found[0]
    _, end_tile_x, end_tile_y, _ = end_found[0]

    start_edge_pos = {
      "top": (start_tile_x + TILE_SIZE // 2, start_tile_y),
      "bottom": (start_tile_x + TILE_SIZE // 2, start_tile_y + TILE_SIZE),
      "left": (start_tile_x, start_tile_y + TILE_SIZE // 2),
      "right": (start_tile_x + TILE_SIZE, start_tile_y + TILE_SIZE // 2),
    }[arrow.start_edge]

    end_edge_pos = {
      "top": (end_tile_x + TILE_SIZE // 2, end_tile_y),
      "bottom": (end_tile_x + TILE_SIZE // 2, end_tile_y + TILE_SIZE),
      "left": (end_tile_x, end_tile_y + TILE_SIZE // 2),
      "right": (end_tile_x + TILE_SIZE, end_tile_y + TILE_SIZE // 2),
    }[arrow.end_edge]

    arrow.start_pos = start_edge_pos
    arrow.end_pos = end_edge_pos
    arrow.draw(screen)


def draw_tile_features(tile, tile_x, tile_y, tile_id):
 global creating_arrow, arrow_start_tile_id, arrow_start_edge, arrow_start_pos

 pygame.draw.rect(screen, (255, 255, 255), (tile_x, tile_y, TILE_SIZE, TILE_SIZE), 2)

 center_top = (tile_x + TILE_SIZE // 2, tile_y)
 center_bottom = (tile_x + TILE_SIZE // 2, tile_y + TILE_SIZE)
 center_left = (tile_x, tile_y + TILE_SIZE // 2)
 center_right = (tile_x + TILE_SIZE, tile_y + TILE_SIZE // 2)

 edges = {
   "top": center_top,
   "bottom": center_bottom,
   "left": center_left,
   "right": center_right,
 }

 circle_color = (255, 0, 0)
 circle_radius = 6

 mouse_x, mouse_y = pygame.mouse.get_pos()
 for edge, center in edges.items():
  pygame.draw.circle(screen, circle_color, center, circle_radius)

  circle_rect = pygame.Rect(center[0] - circle_radius, center[1] - circle_radius,
                            circle_radius * 2, circle_radius * 2)
  
  if circle_rect.collidepoint(mouse_x, mouse_y) and pygame.mouse.get_pressed()[0]:
    if not creating_arrow:
      creating_arrow = Arrow(tile_id, edge)
      arrow_start_tile_id = tile_id
      arrow_start_edge = edge
      arrow_start_pos = center

 # If currently creating an arrow, update and draw it
 if creating_arrow:
  snapping_pos = None
  # Try to snap to another tile's edge
  for (p_tile, p_x, p_y, p_id) in placed_tiles:
    placed_edges = {
      "top": (p_x + TILE_SIZE // 2, p_y),
      "bottom": (p_x + TILE_SIZE // 2, p_y + TILE_SIZE),
      "left": (p_x, p_y + TILE_SIZE // 2),
      "right": (p_x + TILE_SIZE, p_y + TILE_SIZE // 2),
    }
    for end_edge, end_center in placed_edges.items():
      end_circle_rect = pygame.Rect(end_center[0] - circle_radius, end_center[1] - circle_radius,
                                    circle_radius * 2, circle_radius * 2)
      if end_circle_rect.collidepoint(mouse_x, mouse_y):
        snapping_pos = end_center
        creating_arrow.end_tile_id = p_id
        creating_arrow.end_edge = end_edge
        break

  creating_arrow.start_pos = arrow_start_pos
  creating_arrow.end_pos = snapping_pos if snapping_pos else (mouse_x, mouse_y)
  creating_arrow.draw(screen)

  if not pygame.mouse.get_pressed()[0]:
    if snapping_pos and creating_arrow.end_tile_id is not None:
      arrows.append(creating_arrow)
    creating_arrow = None


def ruleset_Screen():
    global scroll_offset, is_scrolling, dragging_tile, dragging_offset, placed_tiles, creating_arrow

    selection_x = 100
    selection_height = 400
    selection_width = 100
    selection_y = (screen.get_height() - selection_height) / 2

    inner_rect = pygame.Rect(selection_x, selection_y, selection_width, selection_height)
    pygame.draw.rect(screen, (0, 0, 0), inner_rect)

    tile_size = TILE_SIZE
    spacing = 4
    tiles_per_row = 2
    pair_width = tiles_per_row * tile_size + (tiles_per_row - 1) * spacing
    horizontal_offset = (selection_width - pair_width) // 2
    y_offset = selection_y + scroll_offset

    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Draw the white rectangle containing the tile selection
    pygame.draw.rect(screen, (255, 255, 255), (selection_x, selection_y, selection_width, selection_height), 3)

    # Loop through all tiles in the selection area
    for idx, tile in enumerate(all_tiles):
        row = idx // tiles_per_row
        col = idx % tiles_per_row
        tile_x = selection_x + horizontal_offset + col * (tile_size + spacing)
        tile_y = y_offset + row * (tile_size + spacing)

        # Only draw non-dragging tiles
        if not (dragging_tile and dragging_tile[0] == tile):
            screen.blit(tile.image, (tile_x, tile_y))

        tile_rect = pygame.Rect(tile_x, tile_y, tile_size, tile_size)

        # Only allow dragging new tiles if not creating an arrow
        if tile_rect.collidepoint(mouse_x, mouse_y) and pygame.mouse.get_pressed()[0] \
           and not dragging_tile and not creating_arrow:
            global tile_id_counter
            tile_id_counter += 1

            # Create a new tile instance for dragging
            new_tile = Cell(name=tile.name, image_path=None, top=[], bottom=[], left=[], right=[])
            new_tile.image = tile.image

            dragging_tile = (new_tile, tile_x, tile_y, tile_id_counter)
            dragging_offset = (mouse_x - tile_x, mouse_y - tile_y)

    # Loop through all placed tiles
    for p_tile, p_x, p_y, p_id in placed_tiles:
        # Draw the tile
        screen.blit(p_tile.image, (p_x, p_y))
        # Draw tile features (circles for arrows) and check collisions
        if not dragging_tile:  # Skip arrow creation logic while dragging
            draw_tile_features(p_tile, p_x, p_y, p_id)

    # Only allow dragging placed tiles if not creating an arrow
    if not creating_arrow:
        for p_tile, p_x, p_y, p_id in placed_tiles:
            placed_rect = pygame.Rect(p_x, p_y, TILE_SIZE, TILE_SIZE)
            if placed_rect.collidepoint(mouse_x, mouse_y) and pygame.mouse.get_pressed()[0] and not dragging_tile:
                dragging_tile = (p_tile, p_x, p_y, p_id)
                dragging_offset = (mouse_x - p_x, mouse_y - p_y)
                placed_tiles.remove((p_tile, p_x, p_y, p_id))
                break

    # Handle dragging tiles
    if dragging_tile:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        tile_x_moving = mouse_x - dragging_offset[0]
        tile_y_moving = mouse_y - dragging_offset[1]

        # Draw the dragging tile
        screen.blit(dragging_tile[0].image, (tile_x_moving, tile_y_moving))
        draw_tile_features(dragging_tile[0], tile_x_moving, tile_y_moving, dragging_tile[3])

        # Release the tile
        if not pygame.mouse.get_pressed()[0]:
            # Check if dropped outside the selection area
            if not (selection_x <= mouse_x <= selection_x + selection_width and
                    selection_y <= mouse_y <= selection_y + selection_height):
                placed_tiles.append((dragging_tile[0], tile_x_moving, tile_y_moving, dragging_tile[3]))
            dragging_tile = None

    # Draw scrollbar if needed
    is_scrolling = inner_rect.collidepoint(mouse_x, mouse_y)
    total_content_height = ((len(all_tiles) + 1) // tiles_per_row) * (tile_size + spacing)
    if total_content_height > selection_height:
        scrollbar_width = 10
        scrollbar_x = selection_x + selection_width - scrollbar_width
        scrollbar_height = selection_height * (selection_height / total_content_height)
        scrollbar_y = selection_y + (-scroll_offset / total_content_height) * selection_height

        pygame.draw.rect(screen, (200, 200, 200), (scrollbar_x, selection_y, scrollbar_width, selection_height))
        pygame.draw.rect(screen, (100, 100, 100), (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height))



class Arrow:
 def __init__(self, start_tile_id, start_edge, end_tile_id=None, end_edge=None):
  self.start_tile_id = start_tile_id
  self.start_edge = start_edge
  self.end_tile_id = end_tile_id
  self.end_edge = end_edge
  self.start_pos = None
  self.end_pos = None

 def draw(self, screen):
  if self.start_pos and self.end_pos:
    pygame.draw.line(screen, (0, 255, 0), self.start_pos, self.end_pos, 2)
    arrow_length = 10
    angle = math.atan2(self.end_pos[1] - self.start_pos[1], self.end_pos[0] - self.start_pos[0])
    arrow_tip = self.end_pos
    arrow_left = (arrow_tip[0] - arrow_length * math.cos(angle - math.pi / 6),
                  arrow_tip[1] - arrow_length * math.sin(angle - math.pi / 6))
    arrow_right = (arrow_tip[0] - arrow_length * math.cos(angle + math.pi / 6),
                   arrow_tip[1] - arrow_length * math.sin(angle + math.pi / 6))
    pygame.draw.polygon(screen, (0, 255, 0), [arrow_tip, arrow_left, arrow_right])


arrows = []
creating_arrow = None
arrow_start_tile_id = None
arrow_start_edge = None
arrow_start_pos = None

def handle_scrolling(event):
 global scroll_offset
 tile_size = 16
 spacing = 4
 tiles_per_row = 2
 total_content_height = ((len(all_tiles) + 1) // tiles_per_row) * (tile_size + spacing)
 max_scroll = total_content_height - 400

 if is_scrolling and total_content_height > 400:
  if event.type == pygame.MOUSEBUTTONDOWN:
    if event.button == 4:  # Scroll up
      scroll_offset += scroll_speed
    elif event.button == 5:  # Scroll down
      scroll_offset -= scroll_speed
  scroll_offset = max(min(scroll_offset, 0), -max_scroll)

def generateRulesetFromArrows():
    global placed_tiles, arrows
    
    for (tile, _, _, _) in placed_tiles:
        tile.top = []
        tile.bottom = []
        tile.left = []
        tile.right = []

    placed_tile_dict = {}
    for (tile, _, _, tile_id) in placed_tiles:
        placed_tile_dict[tile_id] = tile

    for arrow in arrows:
        start_id = arrow.start_tile_id
        end_id = arrow.end_tile_id

        # Make sure both ends exist in placed_tile_dict
        if start_id in placed_tile_dict and end_id in placed_tile_dict:
            start_tile = placed_tile_dict[start_id]
            end_tile = placed_tile_dict[end_id]

            # Update the forward connection on the start tile
            if arrow.start_edge == "top":
                start_tile.top.append(end_tile)
            elif arrow.start_edge == "bottom":
                start_tile.bottom.append(end_tile)
            elif arrow.start_edge == "left":
                start_tile.left.append(end_tile)
            elif arrow.start_edge == "right":
                start_tile.right.append(end_tile)

            # Update the reverse connection on the end tile
            if arrow.end_edge == "top":
                end_tile.top.append(start_tile)
            elif arrow.end_edge == "bottom":
                end_tile.bottom.append(start_tile)
            elif arrow.end_edge == "left":
                end_tile.left.append(start_tile)
            elif arrow.end_edge == "right":
                end_tile.right.append(start_tile)

tk_root = Tk()
tk_root.withdraw()
tk_root.attributes("-topmost", True)  # Ensure file dialog appears on top

def saveRulesetToFile():
    """Save the ruleset as a JSON file, including arrows."""
    # OPTIONAL: If you want the tile edges to be up-to-date:
    generateRulesetFromArrows()

    file_path = filedialog.asksaveasfilename(
        title="Save Ruleset",
        defaultextension=".json",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
    )
    if file_path:
        try:
            # --- A) Gather tile data
            tiles_data = []
            for tile, x, y, tile_id in placed_tiles:
                tile_info = {
                    "id": tile_id,
                    "name": tile.name,
                    "x": x,
                    "y": y,
                    "connections": {
                        "top":    [t.name for t in tile.top],
                        "bottom": [t.name for t in tile.bottom],
                        "left":   [t.name for t in tile.left],
                        "right":  [t.name for t in tile.right],
                    }
                }
                tiles_data.append(tile_info)

            # --- B) Gather arrow data
            arrows_data = []
            for arrow in arrows:
                # Create a JSON-friendly dict for each arrow
                arrow_info = {
                    "start_tile_id": arrow.start_tile_id,
                    "start_edge": arrow.start_edge,
                    "end_tile_id": arrow.end_tile_id,
                    "end_edge": arrow.end_edge
                }
                # Convert positions to {"x": float, "y": float}
                if arrow.start_pos is not None:
                    arrow_info["start_pos"] = {"x": arrow.start_pos[0],
                                               "y": arrow.start_pos[1]}
                else:
                    arrow_info["start_pos"] = None

                if arrow.end_pos is not None:
                    arrow_info["end_pos"] = {"x": arrow.end_pos[0],
                                             "y": arrow.end_pos[1]}
                else:
                    arrow_info["end_pos"] = None

                arrows_data.append(arrow_info)

            # --- C) Combine into one JSON object
            ruleset_data = {
                "tiles": tiles_data,
                "arrows": arrows_data
            }

            # --- D) Save to disk
            with open(file_path, "w") as file:
                json.dump(ruleset_data, file, indent=4)
            print(f"Ruleset saved to {file_path}")

        except Exception as e:
            print(f"Error saving ruleset: {e}")


def loadRulesetFromFile():
    """Load the ruleset from a JSON file and reconstruct tiles & arrows."""

    file_path = filedialog.askopenfilename(
        title="Load Ruleset",
        defaultextension=".json",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
    )
    if not file_path:
        return  # User canceled or closed dialog

    try:
        with open(file_path, "r") as file:
            data = json.load(file)

        # Clear existing placed tiles and arrows
        placed_tiles.clear()
        arrows.clear()

        # Map from tile name -> base tile in all_tiles (for images).
        name_tile_map = {t.name: t for t in all_tiles}

        # --- A) Rebuild placed tiles
        id_to_newcell = {}
        for tile_info in data["tiles"]:
            base_tile = name_tile_map.get(tile_info["name"])
            if not base_tile:
                print(f"Warning: Tile '{tile_info['name']}' not found in all_tiles.")
                continue

            # Create a new Cell for each placed tile
            new_cell = Cell(
                name=base_tile.name,
                image_path=None,
                top=[], bottom=[], left=[], right=[]
            )
            new_cell.image = base_tile.image  # Reuse loaded image

            placed_tiles.append((new_cell,
                                 tile_info["x"],
                                 tile_info["y"],
                                 tile_info["id"]))
            id_to_newcell[tile_info["id"]] = new_cell

        # --- B) Rebuild arrow objects from "arrows"
        if "arrows" in data:
            for arrow_data in data["arrows"]:
                new_arrow = Arrow(
                    start_tile_id=arrow_data["start_tile_id"],
                    start_edge=arrow_data["start_edge"],
                    end_tile_id=arrow_data["end_tile_id"],
                    end_edge=arrow_data["end_edge"]
                )
                # If positions are given, set them
                sp = arrow_data.get("start_pos")
                if sp is not None:
                    new_arrow.start_pos = (sp["x"], sp["y"])

                ep = arrow_data.get("end_pos")
                if ep is not None:
                    new_arrow.end_pos = (ep["x"], ep["y"])

                arrows.append(new_arrow)

        print(f"Ruleset loaded from {file_path}.")

    except Exception as e:
        print(f"Error loading ruleset: {e}")


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
  if 0 <= neighbor_x < grid_x and 0 <= neighbor_y < grid_y:
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
     pygame.draw.rect(screen, (200, 200, 200),
                      (x * TILE_SIZE + offset_x, y * TILE_SIZE + offset_y, TILE_SIZE, TILE_SIZE), 1)
     text = font.render(str(len(cell.options)), True, (255, 255, 255))
     screen.blit(text, (x * TILE_SIZE + TILE_SIZE // 4 + offset_x, 
                        y * TILE_SIZE + TILE_SIZE // 4 + offset_y))

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
    if self.rect.collidepoint(position) and pygame.mouse.get_pressed()[0]:
        return True
    return False

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
exit_ruleset_screen_button = Button(button_surface,200,150,"EXIT")
save_ruleset_button = Button(button_surface, 1650, 500, "SAVE")
load_ruleset_button = Button(button_surface, 1650, 650, "LOAD")

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

        handle_scrolling(event)

    # Check button inputs
    if run_button.checkForInput():
        WFC_running += 1
    elif ruleset_button.checkForInput():
        ruleset_screen = True

    # Wave Function Collapse logic
    if WFC_running == 1:
        generateRulesetFromArrows()
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

    # Ruleset screen logic
    if ruleset_screen:
        exit_ruleset_screen = False
        while not exit_ruleset_screen:
            screen.fill((0, 0, 0))
            if exit_ruleset_screen_button.checkForInput():
                exit_ruleset_screen = True
                ruleset_screen = False

            for event in pygame.event.get():
                handle_scrolling(event)
                if event.type == pygame.QUIT:
                    exit_ruleset_screen = True
                    ruleset_screen = False
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        exit_ruleset_screen = True
                        ruleset_screen = False
                        running = False

            ruleset_Screen()
            draw_arrows()

            save_ruleset_button.update()
            if save_ruleset_button.checkForInput():
                saveRulesetToFile()
            
            load_ruleset_button.update()
            if load_ruleset_button.checkForInput():
                loadRulesetFromFile()

            if not pygame.mouse.get_pressed()[0]:
                is_saving = False

            exit_ruleset_screen_button.update()
            pygame.display.flip()

    # Update buttons in the main menu
    run_button.update()
    ruleset_button.update()
    pygame.display.flip()

pygame.quit()
sys.exit()