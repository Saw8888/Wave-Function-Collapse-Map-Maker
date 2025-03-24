import pygame
import random
import sys
import math
import json
from tkinter import filedialog, Tk
from PIL import Image
import os

pygame.init()

screen_x = 1480
screen_y = 900
screen = pygame.display.set_mode((screen_x, screen_y))
pygame.display.set_caption("Wave Function Collapse")

TILE_SIZE = int(0.03 * screen_x)
GRID_TILES_SIZE = int(0.04 * screen_x)

global grid_x, grid_y
grid_x = 15
grid_y = 10

RUN_BUTTON_POS = (int(0.85 * screen_x), int(0.15 * screen_y))
RULESET_BUTTON_POS = (int(0.85 * screen_x), int(0.30 * screen_y))
EXIT_BUTTON_POS = (int(0.15 * screen_x), int(0.15 * screen_y))
SAVE_BUTTON_POS = (int(0.85 * screen_x), int(0.50 * screen_y))
MAP_BUTTON_POS = (int(0.85 * screen_x), int(0.45 * screen_y))
LOAD_BUTTON_POS = (int(0.85 * screen_x), int(0.65 * screen_y))
TILES_BUTTON_POS = (int(0.85 * screen_x), int(0.57 * screen_y))

SELECTION_X = int(0.10 * screen_x)
SELECTION_WIDTH = int(((TILE_SIZE/screen_x)*2) * screen_x) + 15
SELECTION_HEIGHT = 400
SELECTION_Y = (screen_y - SELECTION_HEIGHT) // 2

MAIN_SELECTION_X = 10
MAIN_SELECTION_Y = 80
MAIN_SELECTION_WIDTH = int(0.12 * screen_x)
MAIN_SELECTION_HEIGHT = screen_y - 90

scroll_offset = 0
scroll_speed = 10
is_scrolling = False

main_scroll_offset = 0
main_is_scrolling = False

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
  self.removal_log = {}
  self.exclusion_mode = False
  self.probability = None
  self.seeded = False

 def __eq__(self, other):
  if not isinstance(other, Cell):
   return False
  return self.name == other.name

 def __hash__(self):
  return hash(self.name)

all_tiles = []

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
   angle = math.atan2(self.end_pos[1] - self.start_pos[1],
                      self.end_pos[0] - self.start_pos[0])
   arrow_tip = self.end_pos
   arrow_left = (arrow_tip[0] - arrow_length * math.cos(angle - math.pi / 6),
                 arrow_tip[1] - arrow_length * math.sin(angle - math.pi / 6))
   arrow_right = (arrow_tip[0] - arrow_length * math.cos(angle + math.pi / 6),
                  arrow_tip[1] - arrow_length * math.sin(angle + math.pi / 6))
   pygame.draw.polygon(screen, (0, 255, 0),
                       [arrow_tip, arrow_left, arrow_right])

arrows = []
creating_arrow = None
arrow_start_tile_id = None
arrow_start_edge = None
arrow_start_pos = None

dragging_tile = None
dragging_offset = (0, 0)
placed_tiles = []

def gcd(a, b):
 while b:
  a, b = b, a % b
 return a

def lcm(a, b):
 return (a * b) // gcd(a, b)

import random

def pickWeightedTile(options):
    valid = []
    total_defined_probability = 0.0
    undefined_count = 0

    for t in options:
        if t.probability is None:
            undefined_count += 1
        else:
            if t.probability > 0:
                total_defined_probability += (t.probability / 100.0)

    if total_defined_probability > 1.0:
        raise ValueError("Total defined probabilities exceed 100%.")

    remaining_probability = 1.0 - total_defined_probability
    if undefined_count > 0:
        share = remaining_probability / undefined_count
    else:
        share = 0

    weighted_tiles = []
    for t in options:
        if t.probability is None:
            if share > 0:
                weighted_tiles.append((t, share))
        else:
            if t.probability > 0:
                weighted_tiles.append((t, t.probability / 100.0))

    if not weighted_tiles:
        return None

    total_w = sum(w for (_, w) in weighted_tiles)
    r = random.random() * total_w
    cumulative = 0
    for (tile, w) in weighted_tiles:
        cumulative += w
        if r <= cumulative:
            return tile
    return weighted_tiles[-1][0]

def shorten_name(full_path: str) -> str:
 basename = os.path.basename(full_path)
 name_only = os.path.splitext(basename)[0]
 return name_only

def propagate(x, y):
    if not grid[y][x].collapsed:
        return
    tile = grid[y][x].options[0]

    neighbor_offsets = [
        (0, -1, tile.top,    "bottom"),
        (0,  1, tile.bottom, "top"),
        (-1, 0, tile.left,   "right"),
        ( 1, 0, tile.right,  "left"),
    ]
    directions = ["top", "bottom", "left", "right"]

    for i, (dx, dy, tile_edge_list, neighbor_opposite_edge) in enumerate(neighbor_offsets):
        nx = x + dx
        ny = y + dy
        if 0 <= nx < grid_x and 0 <= ny < grid_y:
            neighbor = grid[ny][nx]
            if neighbor.collapsed:
                continue

            allowed_tiles = []
            for candidate_tile in tile_edge_list:
                if tile in getattr(candidate_tile, neighbor_opposite_edge):
                    allowed_tiles.append(candidate_tile)

            allowed_names = {t.name for t in allowed_tiles}
            old_options = set(neighbor.options)
            new_options = [o for o in neighbor.options if o.name in allowed_names]

            removed_tiles = old_options - set(new_options)
            reason = (
              f"Cell({x},{y}) collapsed to '{shorten_name(tile.name)}', "
              f"restricting its {directions[i]} neighbor to "
              f"{[shorten_name(t.name) for t in allowed_tiles]}."
            )
            neighbor.removal_log.setdefault(
                str([shorten_name(t.name) for t in removed_tiles]), []
            ).append(reason)

            neighbor.options = new_options
            if not neighbor.options:
                print(f"*** Contradiction at cell ({nx},{ny}): No options left. ***")
                for removed_tile_name, reasons in neighbor.removal_log.items():
                    short_removed_name = shorten_name(removed_tile_name)
                    print(f"  Tiles '{short_removed_name}' removed because:")
                    for r in reasons:
                        print(f"    - {r}")
                return

def globalPropagate(grid):
    changed = True
    while changed:
        changed = False
        queue = []

        for yy in range(grid_y):
            for xx in range(grid_x):
                cell = grid[yy][xx]
                if cell.collapsed and cell.options:
                    queue.append((xx, yy))

        visited = set()
        while queue:
            x, y = queue.pop(0)
            if (x, y) in visited:
                continue
            visited.add((x, y))

            cell = grid[y][x]
            if cell.collapsed and cell.options:
                old_len = len(cell.options)
                propagate(x, y)
                new_len = len(cell.options)
                if new_len < old_len:
                    changed = True

            for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < grid_x and 0 <= ny < grid_y:
                    neighbor = grid[ny][nx]
                    old_collapsed = neighbor.collapsed
                    old_len = len(neighbor.options)
                    if not neighbor.seeded and len(neighbor.options) == 1:
                        neighbor.collapsed = True

                    new_len = len(neighbor.options)
                    if (new_len < old_len) or (neighbor.collapsed and not old_collapsed):
                        changed = True
                        queue.append((nx, ny))

def init_grid(grid_reference=None):
 new_grid = []
 for yy in range(grid_y):
  row = []
  for xx in range(grid_x):
   if grid_reference and grid_reference[yy][xx].seeded:
    row.append(grid_reference[yy][xx])
   else:
    new_cell = Cell("")
    new_cell.options = all_tiles.copy()
    row.append(new_cell)
  new_grid.append(row)
 return new_grid

def find_lowest_entropy(grid):
 lowest_entropy = float('inf')
 lowest_cell = None
 for yy in range(grid_y):
  for xx in range(grid_x):
   cell = grid[yy][xx]
   if not cell.collapsed and len(cell.options) < lowest_entropy:
    lowest_entropy = len(cell.options)
    lowest_cell = (xx, yy)
 return lowest_cell

def draw_grid():
 font = pygame.font.Font(None, 24)
 offset_x = (screen.get_width() - (grid_x * GRID_TILES_SIZE)) / 2
 offset_y = (screen.get_height() - (grid_y * GRID_TILES_SIZE)) / 2
 for yy in range(grid_y):
  for xx in range(grid_x):
   cell = grid[yy][xx]
   rect_x = xx * GRID_TILES_SIZE + offset_x
   rect_y = yy * GRID_TILES_SIZE + offset_y
   if cell.collapsed and cell.options:
    tile = cell.options[0]
    if tile.image:
     scaled_img = pygame.transform.scale(tile.image, (GRID_TILES_SIZE, GRID_TILES_SIZE))
     screen.blit(scaled_img, (rect_x, rect_y))
    else:
     pygame.draw.rect(screen, (0, 255, 0),
                      (rect_x, rect_y, GRID_TILES_SIZE, GRID_TILES_SIZE), 0)
   else:
    pygame.draw.rect(screen, (200, 200, 200),
                     (rect_x, rect_y, GRID_TILES_SIZE, GRID_TILES_SIZE), 1)
    text = font.render(str(len(cell.options)), True, (255, 255, 255))
    screen.blit(text, (rect_x + GRID_TILES_SIZE // 4, rect_y + GRID_TILES_SIZE // 4))

def setOrUnsetProbability(tile):
 if tile.probability is None:
  tile.probability = 100
  print(f"Tile '{tile.name}' => probability set to 100")
 else:
  tile.probability = None
  print(f"Tile '{tile.name}' => probability unset (default 100)")

def adjustProbability(tile, delta):
 if tile.probability is not None:
  new_val = tile.probability + delta
  new_val = max(0, min(100, new_val))
  tile.probability = int(new_val)
  print(f"Tile '{tile.name}' => probability adjusted to {tile.probability}")

def generateRulesetFromArrows():
 rulesets = {}
 for (tile, _, _, _) in placed_tiles:
  if tile.name not in rulesets:
   rulesets[tile.name] = {
       "exclusion_mode": tile.exclusion_mode,
       "top": set(),
       "bottom": set(),
       "left": set(),
       "right": set(),
       "removals": {"top": set(), "bottom": set(), "left": set(), "right": set()}
   }
  else:
   if tile.exclusion_mode:
    rulesets[tile.name]["exclusion_mode"] = True

 placed_tile_dict = {tile_id: tile for (tile, _, _, tile_id) in placed_tiles}
 for arrow in arrows:
  if arrow.start_tile_id not in placed_tile_dict or arrow.end_tile_id not in placed_tile_dict:
   continue
  start_tile = placed_tile_dict[arrow.start_tile_id]
  end_tile   = placed_tile_dict[arrow.end_tile_id]
  s_name = start_tile.name
  e_name = end_tile.name
  s_rules = rulesets[s_name]
  e_rules = rulesets[e_name]
  if not s_rules["exclusion_mode"]:
   if arrow.start_edge == "top":
    s_rules["top"].add(e_name)
   elif arrow.start_edge == "bottom":
    s_rules["bottom"].add(e_name)
   elif arrow.start_edge == "left":
    s_rules["left"].add(e_name)
   elif arrow.start_edge == "right":
    s_rules["right"].add(e_name)
  else:
   s_rules["removals"][arrow.start_edge].add(e_name)
  if not e_rules["exclusion_mode"]:
   if arrow.end_edge == "top":
    e_rules["top"].add(s_name)
   elif arrow.end_edge == "bottom":
    e_rules["bottom"].add(s_name)
   elif arrow.end_edge == "left":
    e_rules["left"].add(s_name)
   elif arrow.end_edge == "right":
    e_rules["right"].add(s_name)
  else:
   e_rules["removals"][arrow.end_edge].add(s_name)

 for e_name, e_data in rulesets.items():
  if not e_data["exclusion_mode"]:
   continue
  for n_name, n_data in rulesets.items():
   if n_name == e_name or n_data["exclusion_mode"]:
    continue
   for edge in ["top", "bottom", "left", "right"]:
    if e_name not in n_data[edge]:
     opposite = {"top": "bottom", "bottom": "top", "left": "right", "right": "left"}
     e_edge = opposite[edge]
     if n_name not in e_data["removals"][e_edge]:
      n_data[edge].add(e_name)

 for e_name, e_data in rulesets.items():
  if not e_data["exclusion_mode"]:
   continue
  for n_name, n_data in rulesets.items():
   if n_name == e_name or n_data["exclusion_mode"]:
    continue
   for edge in ["top", "bottom", "left", "right"]:
    if n_name not in e_data["removals"][edge]:
     e_data[edge].add(n_name)

 def lookup_tiles(name_set):
  return [t for t in all_tiles if t.name in name_set]

 for (tile, _, _, _) in placed_tiles:
  d = rulesets[tile.name]
  tile.top    = lookup_tiles(d["top"])
  tile.bottom = lookup_tiles(d["bottom"])
  tile.left   = lookup_tiles(d["left"])
  tile.right  = lookup_tiles(d["right"])

 for tile in all_tiles:
  if tile.name in rulesets:
   d = rulesets[tile.name]
   tile.top    = lookup_tiles(d["top"])
   tile.bottom = lookup_tiles(d["bottom"])
   tile.left   = lookup_tiles(d["left"])
   tile.right  = lookup_tiles(d["right"])

 print("\n----- FINAL RULESETS -----")
 for name, data in rulesets.items():
  print(f"{shorten_name(name)} [excluded={data['exclusion_mode']}]")
  for edge in ["top", "bottom", "left", "right"]:
   print(f"  {edge} => {[shorten_name(t) for t in data[edge]]}")
 print("--------------------------\n")
 if not placed_tiles or not arrows:
        raise ValueError("No ruleset is present (no placed tiles or no arrows).")

tk_root = Tk()
tk_root.withdraw()
tk_root.attributes("-topmost", True)

def saveRulesetToFile():
 generateRulesetFromArrows()
 file_path = filedialog.asksaveasfilename(
     title="Save Ruleset",
     defaultextension=".json",
     filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
 )
 if file_path:
  try:
   ruleset_dict = {}
   for tile, x, y, tile_id in placed_tiles:
    sprite_name = tile.name
    if sprite_name not in ruleset_dict:
     ruleset_dict[sprite_name] = {
         "exclusion_mode": tile.exclusion_mode,
         "connections": {
             "top": set(t.name for t in tile.top),
             "bottom": set(t.name for t in tile.bottom),
             "left": set(t.name for t in tile.left),
             "right": set(t.name for t in tile.right)
         }
     }
    else:
     ruleset_dict[sprite_name]["connections"]["top"].update(t.name for t in tile.top)
     ruleset_dict[sprite_name]["connections"]["bottom"].update(t.name for t in tile.bottom)
     ruleset_dict[sprite_name]["connections"]["left"].update(t.name for t in tile.left)
     ruleset_dict[sprite_name]["connections"]["right"].update(t.name for t in tile.right)

   master_rulesets = []
   for sprite_name, data in ruleset_dict.items():
    master_rulesets.append({
        "name": sprite_name,
        "exclusion_mode": data["exclusion_mode"],
        "connections": {
            "top": list(data["connections"]["top"]),
            "bottom": list(data["connections"]["bottom"]),
            "left": list(data["connections"]["left"]),
            "right": list(data["connections"]["right"])
        }
    })

   diagram_placed_tiles = []
   for tile, x, y, tile_id in placed_tiles:
    diagram_placed_tiles.append({
        "id": tile_id,
        "name": tile.name,
        "x": x,
        "y": y,
        "exclusion_mode": tile.exclusion_mode,
        "probability": tile.probability
    })

   arrows_data = []
   for arrow in arrows:
    arrow_info = {
        "start_tile_id": arrow.start_tile_id,
        "start_edge": arrow.start_edge,
        "end_tile_id": arrow.end_tile_id,
        "end_edge": arrow.end_edge,
        "start_pos": {"x": arrow.start_pos[0], "y": arrow.start_pos[1]} if arrow.start_pos else None,
        "end_pos": {"x": arrow.end_pos[0], "y": arrow.end_pos[1]} if arrow.end_pos else None
    }
    arrows_data.append(arrow_info)

   ruleset_data = {
       "rulesets": master_rulesets,
       "diagram": {
           "placed_tiles": diagram_placed_tiles,
           "arrows": arrows_data
       }
   }
   with open(file_path, "w") as file:
    json.dump(ruleset_data, file, indent=4)
   print(f"Ruleset saved to {file_path}")
  except Exception as e:
   print(f"Error saving ruleset: {e}")

def loadRulesetFromFile():
 file_path = filedialog.askopenfilename(
     title="Load Ruleset",
     defaultextension=".json",
     filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
 )
 if not file_path:
  return
 try:
  with open(file_path, "r") as file:
   data = json.load(file)
  loadMasterRuleset(file_path)

  placed_tiles.clear()
  arrows.clear()
  diagram = data.get("diagram", {})
  placed_tiles_data = diagram.get("placed_tiles", [])
  for tile_info in placed_tiles_data:
   try:
    loaded_image = pygame.image.load(tile_info["name"])
    loaded_image = pygame.transform.scale(loaded_image, (TILE_SIZE, TILE_SIZE))
   except Exception as e:
    print(f"Error loading image '{tile_info['name']}': {e}")
    continue

   new_cell = Cell(name=tile_info["name"], image_path=None)
   new_cell.image = loaded_image
   new_cell.exclusion_mode = tile_info.get("exclusion_mode", False)
   new_cell.probability = tile_info.get("probability", None)
   placed_tiles.append((new_cell, tile_info["x"], tile_info["y"], tile_info["id"]))

   if tile_info["name"] not in [t.name for t in all_tiles]:
    all_tiles.append(new_cell)

  arrows_data = diagram.get("arrows", [])
  for arrow_data in arrows_data:
   new_arrow = Arrow(
       start_tile_id=arrow_data["start_tile_id"],
       start_edge=arrow_data["start_edge"],
       end_tile_id=arrow_data["end_tile_id"],
       end_edge=arrow_data["end_edge"]
   )
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

def loadMasterRuleset(json_path):
 try:
  with open(json_path, "r") as f:
   data = json.load(f)
  if "rulesets" not in data:
   print("No 'rulesets' key found in JSON.")
   return
  rulesets = data["rulesets"]
  for ruleset_entry in rulesets:
   sprite_name = ruleset_entry["name"]
   connections = ruleset_entry["connections"]
   matching_tiles = [t for t in all_tiles if t.name == sprite_name]
   if not matching_tiles:
    print(f"No matching tile found in all_tiles for {sprite_name}.")
    continue
   tile_obj = matching_tiles[0]
   top_names = connections["top"]
   bottom_names = connections["bottom"]
   left_names = connections["left"]
   right_names = connections["right"]

   def lookup_tiles(name_list):
    return [t for t in all_tiles if t.name in name_list]

   tile_obj.top = lookup_tiles(top_names)
   tile_obj.bottom = lookup_tiles(bottom_names)
   tile_obj.left = lookup_tiles(left_names)
   tile_obj.right = lookup_tiles(right_names)
   tile_obj.exclusion_mode = ruleset_entry.get("exclusion_mode", False)
   tile_obj.probability = ruleset_entry.get("probability", None)

  print("Master ruleset loaded and applied to all_tiles.")
 except Exception as e:
  print(f"Error loading master ruleset from {json_path}: {e}")

def loadTiles():
 files_path = filedialog.askopenfilenames(title="Load Files")
 if not files_path:
  return
 for tile in files_path:
  all_tiles.append(Cell(tile, tile))

def saveMap():
 file_path = filedialog.asksaveasfilename(
     defaultextension=".png",
     filetypes=[("PNG Files", "*.png"), ("JPEG Files", "*.jpg"), ("All Files", "*.*")]
 )
 if file_path:
  base = Image.new('RGB', (grid_x * GRID_TILES_SIZE, grid_y * GRID_TILES_SIZE))
  offset_x = 0
  offset_y = 0
  for yy in range(grid_y):
   for xx in range(grid_x):
    cell = grid[yy][xx]
    if cell.options and cell.options[0].image:
     scaled_img = pygame.transform.scale(cell.options[0].image, (GRID_TILES_SIZE, GRID_TILES_SIZE))
     mode = 'RGBA'
     data_str = pygame.image.tostring(scaled_img, mode)
     tile_img = Image.frombytes(mode, scaled_img.get_size(), data_str)
     base.paste(tile_img, (xx * GRID_TILES_SIZE, yy * GRID_TILES_SIZE))
    else:
     for py in range(GRID_TILES_SIZE):
      for px in range(GRID_TILES_SIZE):
       base.putpixel((xx*GRID_TILES_SIZE+px, yy*GRID_TILES_SIZE+py), (0,255,0))
  base.save(file_path)

main_font = pygame.font.SysFont("cambria", int(screen_x * 0.03))

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

 def checkForInput(self, event):
  if event.type == pygame.MOUSEBUTTONUP:  # Only triggers on mouse button release
   position = pygame.mouse.get_pos()
   if self.rect.collidepoint(position):
    return True
  return False

 def changeColor(self):
  position = pygame.mouse.get_pos()
  if self.rect.collidepoint(position):
   self.text = main_font.render(self.text_input, True, "green")
  else:
   self.text = main_font.render(self.text_input, True, "white")

button_surface = pygame.image.load("Sprites/Base/button.png")
button_surface = pygame.transform.scale(button_surface, (int(0.1 * screen_x), int(0.05 * screen_y)))

run_button = Button(button_surface, RUN_BUTTON_POS[0], RUN_BUTTON_POS[1], "RUN")
ruleset_button = Button(button_surface, RULESET_BUTTON_POS[0], RULESET_BUTTON_POS[1], "RULESET")
exit_ruleset_screen_button = Button(button_surface, EXIT_BUTTON_POS[0], EXIT_BUTTON_POS[1], "EXIT")
save_ruleset_button = Button(button_surface, SAVE_BUTTON_POS[0], SAVE_BUTTON_POS[1], "SAVE")
save_map_button = Button(button_surface, MAP_BUTTON_POS[0], MAP_BUTTON_POS[1], "SAVE MAP")
load_ruleset_button = Button(button_surface, LOAD_BUTTON_POS[0], LOAD_BUTTON_POS[1], "LOAD")
load_tiles_button = Button(button_surface, TILES_BUTTON_POS[0], TILES_BUTTON_POS[1], "ADD TILES")

class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val=0, label=""):
        self.rect = pygame.Rect(x, y, width, height)  
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.handle_width = 15  
        self.dragging = False
        self.font = pygame.font.SysFont(None, 24)

    def handle_event(self, event):
        mx, my = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(mx, my):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:

                ratio = (mx - self.rect.x) / float(self.rect.width)

                ratio = max(0, min(1, ratio))
                new_val = int(self.min_val + ratio * (self.max_val - self.min_val))
                self.value = new_val

    def draw(self, surface):

        pygame.draw.rect(surface, (180,180,180), self.rect, border_radius=3)

        fill_ratio = (self.value - self.min_val) / float(self.max_val - self.min_val)
        fill_width = int(self.rect.width * fill_ratio)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
        pygame.draw.rect(surface, (100,200,100), fill_rect, border_radius=3)

        handle_x = self.rect.x + fill_width - (self.handle_width//2)
        handle_rect = pygame.Rect(handle_x, self.rect.y, self.handle_width, self.rect.height)
        pygame.draw.rect(surface, (220,80,80), handle_rect)

        text_surf = self.font.render(f"{self.label}: {self.value}", True, (255,255,255))
        surface.blit(text_surf, (self.rect.x, self.rect.y+2))

    def get_value(self):
        return self.value

width_slider = Slider(MAIN_SELECTION_X, 10,
                      200, 20, 0, 50, initial_val=grid_x, label="Width")
height_slider = Slider(MAIN_SELECTION_X, 40,
                       200, 20, 0, 50, initial_val=grid_y, label="Height")

old_grid_x = grid_x
old_grid_y = grid_y

running = True
WFC_running = 0
ruleset_screen = False
lowest_entropy_cell = True

main_screen_selected_tile = None
last_painted_cell = None

def handle_scrolling(event):
 global scroll_offset
 tiles_per_row = 2
 tile_size = TILE_SIZE
 spacing = 4
 total_content_height = ((len(all_tiles) + 1) // tiles_per_row) * (tile_size + spacing)
 max_scroll = total_content_height - SELECTION_HEIGHT
 if is_scrolling and total_content_height > SELECTION_HEIGHT:
  if event.type == pygame.MOUSEBUTTONDOWN:
   if event.button == 4:  
    scroll_offset += scroll_speed
   elif event.button == 5:  
    scroll_offset -= scroll_speed
  scroll_offset = max(min(scroll_offset, 0), -max_scroll)

def handle_main_scrolling(event):
 global main_scroll_offset
 tiles_per_row = 1
 tile_size = TILE_SIZE
 spacing = 4
 total_content_height = (len(all_tiles)) * (tile_size + spacing)
 max_scroll = total_content_height - MAIN_SELECTION_HEIGHT
 if main_is_scrolling and total_content_height > MAIN_SELECTION_HEIGHT:
  if event.type == pygame.MOUSEBUTTONDOWN:
   if event.button == 4:
    main_scroll_offset += scroll_speed
   elif event.button == 5:
    main_scroll_offset -= scroll_speed
  main_scroll_offset = max(min(main_scroll_offset, 0), -max_scroll)

def get_grid_cell_from_mouse(mx, my):
 offset_x = (screen.get_width() - (grid_x * GRID_TILES_SIZE)) / 2
 offset_y = (screen.get_height() - (grid_y * GRID_TILES_SIZE)) / 2
 gx = int((mx - offset_x) // GRID_TILES_SIZE)
 gy = int((my - offset_y) // GRID_TILES_SIZE)
 if 0 <= gx < grid_x and 0 <= gy < grid_y:
  return (gx, gy)
 return None

def placeTileInGrid(x, y, tile):
 cell = grid[y][x]
 cell.options = [tile]
 cell.collapsed = True
 cell.seeded = True

def removeTileFromGrid(x, y):
 cell = grid[y][x]
 cell.seeded = False
 cell.collapsed = False
 cell.options = all_tiles.copy()

def draw_arrows():
 for arrow in arrows:
  start_found = [(t, xx, yy, tid) for (t, xx, yy, tid) in placed_tiles if tid == arrow.start_tile_id]
  end_found = [(t, xx, yy, tid) for (t, xx, yy, tid) in placed_tiles if tid == arrow.end_tile_id]
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
 border_color = (255, 0, 0) if tile.exclusion_mode else (255, 255, 255)
 pygame.draw.rect(screen, border_color, (tile_x, tile_y, TILE_SIZE, TILE_SIZE), 2)

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

 if creating_arrow:
  snapping_pos = None
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
   if snapping_pos:
    break
  creating_arrow.start_pos = arrow_start_pos
  creating_arrow.end_pos = snapping_pos if snapping_pos else (mouse_x, mouse_y)
  creating_arrow.draw(screen)
  if not pygame.mouse.get_pressed()[0]:
   if snapping_pos and creating_arrow.end_tile_id is not None:
    dist = math.hypot(creating_arrow.end_pos[0] - creating_arrow.start_pos[0],
                      creating_arrow.end_pos[1] - creating_arrow.start_pos[1])
    if dist > circle_radius + 5:
     arrows.append(creating_arrow)
   creating_arrow = None

def ruleset_Screen():
 global scroll_offset, is_scrolling, dragging_tile, dragging_offset, placed_tiles, creating_arrow
 tile_size = TILE_SIZE
 spacing = 4
 tiles_per_row = 2
 pair_width = tiles_per_row * tile_size + (tiles_per_row - 1) * spacing
 horizontal_offset = (SELECTION_WIDTH - pair_width) // 2

 inner_rect = pygame.Rect(SELECTION_X, SELECTION_Y, SELECTION_WIDTH, SELECTION_HEIGHT)
 pygame.draw.rect(screen, (0, 0, 0), inner_rect)
 pygame.draw.rect(screen, (255, 255, 255), inner_rect, 3)

 y_offset = SELECTION_Y + scroll_offset
 mouse_x, mouse_y = pygame.mouse.get_pos()
 prob_font = pygame.font.SysFont(None, 22)

 for idx, tile in enumerate(all_tiles):
  row = idx // tiles_per_row
  col = idx % tiles_per_row
  tile_x = SELECTION_X + horizontal_offset + col * (tile_size + spacing)
  tile_y = y_offset + row * (tile_size + spacing)
  screen.blit(tile.image, (tile_x, tile_y))
  if tile.probability is not None:
   txt = f"{tile.probability}"
   surf = prob_font.render(txt, True, (255, 255, 0))
   screen.blit(surf, (tile_x + 4, tile_y + 4))
  tile_rect = pygame.Rect(tile_x, tile_y, tile_size, tile_size)
  if tile_rect.collidepoint(mouse_x, mouse_y) and pygame.mouse.get_pressed()[0] and not dragging_tile and not creating_arrow:
   global tile_id_counter
   tile_id_counter += 1
   dragging_tile = (tile, tile_x, tile_y, tile_id_counter)
   dragging_offset = (mouse_x - tile_x, mouse_y - tile_y)

 for p_tile, p_x, p_y, p_id in placed_tiles:
  screen.blit(p_tile.image, (p_x, p_y))
  if p_tile.probability is not None:
   txt = f"{p_tile.probability}"
   surf = prob_font.render(txt, True, (255, 255, 0))
   screen.blit(surf, (p_x + 4, p_y + 4))
  if not dragging_tile:
   draw_tile_features(p_tile, p_x, p_y, p_id)

 if pygame.mouse.get_pressed()[2]:
  for p_tile, p_x, p_y, p_id in placed_tiles:
   placed_rect = pygame.Rect(p_x, p_y, tile_size, tile_size)
   if placed_rect.collidepoint(mouse_x, mouse_y):
    p_tile.exclusion_mode = not p_tile.exclusion_mode
    break

 if not creating_arrow:
  for p_tile, p_x, p_y, p_id in placed_tiles:
   placed_rect = pygame.Rect(p_x, p_y, tile_size, tile_size)
   if placed_rect.collidepoint(mouse_x, mouse_y) and pygame.mouse.get_pressed()[0] and not dragging_tile:
    dragging_tile = (p_tile, p_x, p_y, p_id)
    dragging_offset = (mouse_x - p_x, mouse_y - p_y)
    placed_tiles.remove((p_tile, p_x, p_y, p_id))
    break

 if dragging_tile:
  mx, my = pygame.mouse.get_pos()
  tile_x_moving = mx - dragging_offset[0]
  tile_y_moving = my - dragging_offset[1]
  drag_tile = dragging_tile[0]
  screen.blit(drag_tile.image, (tile_x_moving, tile_y_moving))
  if drag_tile.probability is not None:
   txt = f"{drag_tile.probability}"
   surf = prob_font.render(txt, True, (255, 255, 0))
   screen.blit(surf, (tile_x_moving + 4, tile_y_moving + 4))
  draw_tile_features(drag_tile, tile_x_moving, tile_y_moving, dragging_tile[3])
  if not pygame.mouse.get_pressed()[0]:
   if not (SELECTION_X <= mx <= SELECTION_X + SELECTION_WIDTH and
           SELECTION_Y <= my <= SELECTION_HEIGHT + SELECTION_Y):
    placed_tiles.append((drag_tile, tile_x_moving, tile_y_moving, dragging_tile[3]))
   dragging_tile = None

 global is_scrolling
 is_scrolling = inner_rect.collidepoint(mouse_x, mouse_y)
 total_content_height = ((len(all_tiles) + 1) // tiles_per_row) * (tile_size + spacing)
 if total_content_height > SELECTION_HEIGHT:
  scrollbar_width = 10
  scrollbar_x = SELECTION_X + SELECTION_WIDTH - scrollbar_width
  scrollbar_height = SELECTION_HEIGHT * (SELECTION_HEIGHT / total_content_height)
  scrollbar_y = SELECTION_Y + (-scroll_offset / total_content_height) * SELECTION_HEIGHT
  pygame.draw.rect(screen, (200, 200, 200),
                   (scrollbar_x, SELECTION_Y, scrollbar_width, SELECTION_HEIGHT))
  pygame.draw.rect(screen, (100, 100, 100),
                   (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height))

def draw_main_tile_selection():
 global main_screen_selected_tile
 global main_scroll_offset
 global main_is_scrolling

 tile_size = TILE_SIZE
 spacing = 4
 tiles_per_row = 1

 selection_rect = pygame.Rect(MAIN_SELECTION_X, MAIN_SELECTION_Y,
                              MAIN_SELECTION_WIDTH, MAIN_SELECTION_HEIGHT)
 pygame.draw.rect(screen, (30, 30, 30), selection_rect)
 pygame.draw.rect(screen, (255, 255, 255), selection_rect, 2)

 mx, my = pygame.mouse.get_pos()

 main_is_scrolling = selection_rect.collidepoint(mx, my)

 y_offset = MAIN_SELECTION_Y + main_scroll_offset
 for idx, tile in enumerate(all_tiles):
  tile_y = y_offset + idx * (tile_size + spacing)
  tile_x = MAIN_SELECTION_X + 5
  screen.blit(tile.image, (tile_x, tile_y))

  tile_rect = pygame.Rect(tile_x, tile_y, tile_size, tile_size)

  if tile == main_screen_selected_tile:
   pygame.draw.rect(screen, (255, 255, 0), tile_rect, 3)

  if tile_rect.collidepoint(mx, my) and pygame.mouse.get_pressed()[0]:
   main_screen_selected_tile = tile

run_button_pressed = False
grid = init_grid()  

while running:
 screen.fill((0, 0, 0))

 # --- Outer loop: handle events for the main screen ---
 for event in pygame.event.get():

  width_slider.handle_event(event)
  height_slider.handle_event(event)

  if event.type == pygame.QUIT:
   running = False
  if event.type == pygame.KEYDOWN:
   if event.key == pygame.K_q:
    running = False

  handle_main_scrolling(event)

  # Main screen buttons
  if run_button.checkForInput(event):
   run_button_pressed = True
   pygame.event.clear(pygame.MOUSEBUTTONUP)  # flush old mouse-ups
  elif ruleset_button.checkForInput(event):
   ruleset_screen = True
   pygame.event.clear(pygame.MOUSEBUTTONUP)  # flush old mouse-ups
  elif save_map_button.checkForInput(event):
   saveMap()

  # Placing tiles with left-click
  if event.type == pygame.MOUSEBUTTONDOWN:
   if event.button == 1:
    if main_screen_selected_tile:
     cell_pos = get_grid_cell_from_mouse(*pygame.mouse.get_pos())
     if cell_pos:
      x, y = cell_pos
      placeTileInGrid(x, y, main_screen_selected_tile)
      globalPropagate(grid)
      last_painted_cell = cell_pos

   # Removing seeded tiles with right-click
   if event.button == 3:
    cell_pos = get_grid_cell_from_mouse(*pygame.mouse.get_pos())
    if cell_pos:
     cx, cy = cell_pos
     c = grid[cy][cx]
     if c.seeded:
      removeTileFromGrid(cx, cy)
      globalPropagate(grid)

  # Drag-to-paint multiple cells
  if event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0]:
   if main_screen_selected_tile:
    cell_pos = get_grid_cell_from_mouse(*pygame.mouse.get_pos())
    if cell_pos and cell_pos != last_painted_cell:
     x, y = cell_pos
     placeTileInGrid(x, y, main_screen_selected_tile)
     globalPropagate(grid)
     last_painted_cell = cell_pos

  if event.type == pygame.MOUSEBUTTONUP:
   if event.button == 1:
    last_painted_cell = None

 # If user changes width/height, re-init the grid
 current_w = width_slider.get_value()
 current_h = height_slider.get_value()
 if current_w != old_grid_x or current_h != old_grid_y:
  grid_x = current_w
  grid_y = current_h
  old_grid_x = current_w
  old_grid_y = current_h
  grid = init_grid()

 # Draw main screen items
 draw_main_tile_selection()
 draw_grid()
 width_slider.draw(screen)
 height_slider.draw(screen)
 save_map_button.update()
 run_button.update()
 ruleset_button.update()

 # If RUN was pressed, attempt the wave-function collapse
 if run_button_pressed:
  try:
    generateRulesetFromArrows()
  except ValueError as e:
    print(e)
    print("Please load or create a ruleset before running WFC.")
  else:
    # Collapse the grid with the current rules
    grid = init_grid(grid)
    globalPropagate(grid)

    while True:
      cell_loc = find_lowest_entropy(grid)
      if not cell_loc:
        break
      x, y = cell_loc
      cell = grid[y][x]
      chosen = pickWeightedTile(cell.options)
      if chosen is None:
        chosen = pickWeightedTile(all_tiles)
      cell.collapsed = True
      cell.options = [chosen]
      globalPropagate(grid)

  run_button_pressed = False

 # --- Inner loop: ruleset screen ---
 if ruleset_screen:
  exit_ruleset_screen = False
  while not exit_ruleset_screen:
   screen.fill((60, 60, 60))

   # Process events specific to the ruleset screen
   for ev in pygame.event.get():
    handle_scrolling(ev)

    if ev.type == pygame.QUIT:
     exit_ruleset_screen = True
     ruleset_screen = False
     running = False

    if ev.type == pygame.KEYDOWN:
     if ev.key == pygame.K_q:
      exit_ruleset_screen = True
      ruleset_screen = False
      running = False

    # Check for MOUSEBUTTONUP (middle-click) to toggle probabilities
    if ev.type == pygame.MOUSEBUTTONUP and ev.button == 2:
     mx, my = pygame.mouse.get_pos()
     tile_size = TILE_SIZE
     spacing = 4
     tpr = 2
     pair_width = tpr * tile_size + (tpr - 1) * spacing
     hor_off = (SELECTION_WIDTH - pair_width) // 2
     y_off = SELECTION_Y + scroll_offset
     for idx, tile in enumerate(all_tiles):
      row = idx // tpr
      col = idx % tpr
      tx = SELECTION_X + hor_off + col * (tile_size + spacing)
      ty = y_off + row * (tile_size + spacing)
      rct = pygame.Rect(tx, ty, tile_size, tile_size)
      if rct.collidepoint(mx, my):
       setOrUnsetProbability(tile)
       break

    # Use mouse wheel inside the ruleset screen to adjust probabilities
    if ev.type == pygame.MOUSEWHEEL:
     tpr = 2
     tile_size = TILE_SIZE
     spacing = 4
     pair_width = tpr * tile_size + (tpr - 1) * spacing
     hor_off = (SELECTION_WIDTH - pair_width) // 2
     mx, my = pygame.mouse.get_pos()
     found_tile = None
     for idx, tile in enumerate(all_tiles):
      row = idx // tpr
      col = idx % tpr
      tile_x = SELECTION_X + hor_off + col * (tile_size + spacing)
      tile_y = SELECTION_Y + scroll_offset + row * (tile_size + spacing)
      tile_rect = pygame.Rect(tile_x, tile_y, tile_size, tile_size)
      if tile_rect.collidepoint(mx, my):
       found_tile = tile
       break
     if found_tile and found_tile.probability is not None:
      adjustProbability(found_tile, ev.y)

    # Ruleset screen buttons must be checked with 'ev', not 'event'
    if exit_ruleset_screen_button.checkForInput(ev):
     exit_ruleset_screen = True
     ruleset_screen = False
    if save_ruleset_button.checkForInput(ev):
     saveRulesetToFile()
     pygame.event.clear(pygame.MOUSEBUTTONUP)  # optional flush
    if load_ruleset_button.checkForInput(ev):
     loadRulesetFromFile()
     pygame.event.clear(pygame.MOUSEBUTTONUP)
    if load_tiles_button.checkForInput(ev):
     loadTiles()
     pygame.event.clear(pygame.MOUSEBUTTONUP)

   # Draw the ruleset screen UI
   ruleset_Screen()
   draw_arrows()

   # Update and draw these buttons after handling events
   save_ruleset_button.update()
   load_ruleset_button.update()
   load_tiles_button.update()
   exit_ruleset_screen_button.update()

   pygame.display.flip()

 pygame.display.flip()

pygame.quit()
sys.exit()
