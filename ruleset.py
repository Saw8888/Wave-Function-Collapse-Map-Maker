import pygame
import math
import json
from tkinter import filedialog

# ----------- ARROW CLASS -----------
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
      pygame.draw.polygon(screen, (0, 255, 0), [arrow_tip, arrow_left, arrow_right])

# ----------- SCROLLING -----------
def handle_scrolling(event, all_tiles, tile_size):
  # We import the globals from main to mutate them
  from main import scroll_offset, is_scrolling, scroll_speed
  from main import SELECTION_HEIGHT

  tiles_per_row = 2
  spacing = 4
  total_content_height = ((len(all_tiles) + 1) // tiles_per_row) * (tile_size + spacing)
  max_scroll = total_content_height - SELECTION_HEIGHT

  if is_scrolling and total_content_height > SELECTION_HEIGHT:
    if event.type == pygame.MOUSEBUTTONDOWN:
      if event.button == 4:  # Scroll up
        scroll_offset += scroll_speed
      elif event.button == 5:  # Scroll down
        scroll_offset -= scroll_speed
    scroll_offset = max(min(scroll_offset, 0), -max_scroll)

# ----------- DRAW ARROWS -----------
def draw_arrows(screen, placed_tiles, arrows, tile_size):
  for arrow in arrows:
    start_found = [(t, x, y, tid) for (t, x, y, tid) in placed_tiles if tid == arrow.start_tile_id]
    end_found   = [(t, x, y, tid) for (t, x, y, tid) in placed_tiles if tid == arrow.end_tile_id]
    if len(start_found) == 1 and len(end_found) == 1:
      _, start_x, start_y, _ = start_found[0]
      _, end_x,   end_y,   _ = end_found[0]

      start_edge_pos = {
        "top":    (start_x + tile_size // 2, start_y),
        "bottom": (start_x + tile_size // 2, start_y + tile_size),
        "left":   (start_x, start_y + tile_size // 2),
        "right":  (start_x + tile_size, start_y + tile_size // 2),
      }[arrow.start_edge]

      end_edge_pos = {
        "top":    (end_x + tile_size // 2, end_y),
        "bottom": (end_x + tile_size // 2, end_y + tile_size),
        "left":   (end_x, end_y + tile_size // 2),
        "right":  (end_x + tile_size, end_y + tile_size // 2),
      }[arrow.end_edge]

      arrow.start_pos = start_edge_pos
      arrow.end_pos   = end_edge_pos
      arrow.draw(screen)

# ----------- DRAW TILE FEATURES -----------
def draw_tile_features(
  screen, tile, tile_x, tile_y, tile_id,
  placed_tiles, creating_arrow, arrow_start_tile_id,
  arrow_start_edge, arrow_start_pos, tile_size
):
  from main import dragging_tile, dragging_offset

  pygame.draw.rect(screen, (255, 255, 255), (tile_x, tile_y, tile_size, tile_size), 2)

  center_top    = (tile_x + tile_size // 2, tile_y)
  center_bottom = (tile_x + tile_size // 2, tile_y + tile_size)
  center_left   = (tile_x, tile_y + tile_size // 2)
  center_right  = (tile_x + tile_size, tile_y + tile_size // 2)

  edges = {
    "top":    center_top,
    "bottom": center_bottom,
    "left":   center_left,
    "right":  center_right,
  }

  circle_color  = (255, 0, 0)
  circle_radius = 6
  mouse_x, mouse_y = pygame.mouse.get_pos()

  # Check for arrow creation
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

  # If we have a partial arrow in creation, draw it
  if creating_arrow:
    snapping_pos = None
    for (p_tile, p_x, p_y, p_id) in placed_tiles:
      placed_edges = {
        "top":    (p_x + tile_size // 2, p_y),
        "bottom": (p_x + tile_size // 2, p_y + tile_size),
        "left":   (p_x, p_y + tile_size // 2),
        "right":  (p_x + tile_size, p_y + tile_size // 2),
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
    creating_arrow.end_pos   = snapping_pos if snapping_pos else (mouse_x, mouse_y)
    creating_arrow.draw(screen)

    if not pygame.mouse.get_pressed()[0]:
      if snapping_pos and creating_arrow.end_tile_id is not None:
        from main import arrows
        arrows.append(creating_arrow)
      creating_arrow = None

# ----------- RULESET SCREEN -----------
def ruleset_Screen(
  screen, all_tiles, placed_tiles, tile_id_counter,
  tile_size, scroll_offset, scroll_speed, is_scrolling,
  dragging_tile, dragging_offset, creating_arrow,
  arrow_start_tile_id, arrow_start_edge, arrow_start_pos
):
  from main import SELECTION_X, SELECTION_Y, SELECTION_WIDTH, SELECTION_HEIGHT
  from main import arrows

  inner_rect = pygame.Rect(SELECTION_X, SELECTION_Y, SELECTION_WIDTH, SELECTION_HEIGHT)
  pygame.draw.rect(screen, (0, 0, 0), inner_rect)

  spacing = 4
  tiles_per_row = 2
  pair_width = tiles_per_row * tile_size + (tiles_per_row - 1) * spacing
  horizontal_offset = (SELECTION_WIDTH - pair_width) // 2
  y_offset = SELECTION_Y + scroll_offset

  mouse_x, mouse_y = pygame.mouse.get_pos()

  # Border
  pygame.draw.rect(screen, (255, 255, 255), inner_rect, 3)

  # Draw the tile palette
  for idx, tile in enumerate(all_tiles):
    row = idx // tiles_per_row
    col = idx % tiles_per_row
    tile_x = SELECTION_X + horizontal_offset + col * (tile_size + spacing)
    tile_y = y_offset + row * (tile_size + spacing)

    scaled_img = pygame.transform.scale(tile.image, (tile_size, tile_size))
    screen.blit(scaled_img, (tile_x, tile_y))
    tile_rect = pygame.Rect(tile_x, tile_y, tile_size, tile_size)

    # Drag a new tile from the palette
    if tile_rect.collidepoint(mouse_x, mouse_y) and pygame.mouse.get_pressed()[0] \
       and not dragging_tile and not creating_arrow:
      tile_id_counter += 1
      import copy
      new_tile = copy.copy(tile)
      new_tile.top = []
      new_tile.bottom = []
      new_tile.left = []
      new_tile.right = []

      dragging_tile = (new_tile, tile_x, tile_y, tile_id_counter)
      dragging_offset = (mouse_x - tile_x, mouse_y - tile_y)

  # Draw already placed tiles
  for p_tile, p_x, p_y, p_id in placed_tiles:
    scaled_img = pygame.transform.scale(p_tile.image, (tile_size, tile_size))
    screen.blit(scaled_img, (p_x, p_y))
    # Only show arrow endpoints if we're not dragging
    if not dragging_tile:
      draw_tile_features(screen, p_tile, p_x, p_y, p_id,
                         placed_tiles, creating_arrow, arrow_start_tile_id,
                         arrow_start_edge, arrow_start_pos, tile_size)

  # Allow picking up existing tiles
  if not creating_arrow:
    for p_tile, p_x, p_y, p_id in placed_tiles:
      placed_rect = pygame.Rect(p_x, p_y, tile_size, tile_size)
      if placed_rect.collidepoint(mouse_x, mouse_y) and pygame.mouse.get_pressed()[0] and not dragging_tile:
        dragging_tile = (p_tile, p_x, p_y, p_id)
        dragging_offset = (mouse_x - p_x, mouse_y - p_y)
        placed_tiles.remove((p_tile, p_x, p_y, p_id))
        break

  # If dragging a tile
  if dragging_tile:
    tile_obj, old_x, old_y, t_id = dragging_tile
    tile_x_moving = mouse_x - dragging_offset[0]
    tile_y_moving = mouse_y - dragging_offset[1]

    scaled_img = pygame.transform.scale(tile_obj.image, (tile_size, tile_size))
    screen.blit(scaled_img, (tile_x_moving, tile_y_moving))
    draw_tile_features(screen, tile_obj, tile_x_moving, tile_y_moving, t_id,
                       placed_tiles, creating_arrow, arrow_start_tile_id,
                       arrow_start_edge, arrow_start_pos, tile_size)

    # On mouse release, place tile
    if not pygame.mouse.get_pressed()[0]:
      # If dropped outside the palette, it is placed
      if not (SELECTION_X <= mouse_x <= SELECTION_X + SELECTION_WIDTH and
              SELECTION_Y <= mouse_y <= SELECTION_Y + SELECTION_HEIGHT):
        placed_tiles.append((tile_obj, tile_x_moving, tile_y_moving, t_id))
      dragging_tile = None

  # Check if mouse is over selection panel for scrolling
  from main import is_scrolling
  if inner_rect.collidepoint(mouse_x, mouse_y):
    is_scrolling = True
  else:
    is_scrolling = False

  # If there's more content than the panel can show, show scrollbar
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

# ----------- GENERATE RULESET -----------
def generateRulesetFromArrows(placed_tiles, arrows):
  # Clear existing edges
  for (tile, _, _, _) in placed_tiles:
    tile.top = []
    tile.bottom = []
    tile.left = []
    tile.right = []

  # Create dict for quick tile lookup
  placed_dict = {}
  for (tile, _, _, tid) in placed_tiles:
    placed_dict[tid] = tile

  # Now apply all arrows
  for arrow in arrows:
    if arrow.start_tile_id in placed_dict and arrow.end_tile_id in placed_dict:
      start_tile = placed_dict[arrow.start_tile_id]
      end_tile   = placed_dict[arrow.end_tile_id]

      # Forward connection
      if arrow.start_edge == "top":
        start_tile.top.append(end_tile)
      elif arrow.start_edge == "bottom":
        start_tile.bottom.append(end_tile)
      elif arrow.start_edge == "left":
        start_tile.left.append(end_tile)
      elif arrow.start_edge == "right":
        start_tile.right.append(end_tile)

      # Reverse connection
      if arrow.end_edge == "top":
        end_tile.top.append(start_tile)
      elif arrow.end_edge == "bottom":
        end_tile.bottom.append(start_tile)
      elif arrow.end_edge == "left":
        end_tile.left.append(start_tile)
      elif arrow.end_edge == "right":
        end_tile.right.append(start_tile)

# ----------- SAVE RULESET -----------
def saveRulesetToFile(placed_tiles, arrows):
  generateRulesetFromArrows(placed_tiles, arrows)  # ensure edges are up to date

  from main import tk_root
  file_path = filedialog.asksaveasfilename(
    title="Save Ruleset",
    defaultextension=".json",
    filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
  )
  if file_path:
    try:
      tiles_data = []
      for tile, x, y, tid in placed_tiles:
        tile_info = {
          "id": tid,
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

      arrows_data = []
      for arrow in arrows:
        arrow_info = {
          "start_tile_id": arrow.start_tile_id,
          "start_edge":    arrow.start_edge,
          "end_tile_id":   arrow.end_tile_id,
          "end_edge":      arrow.end_edge
        }
        if arrow.start_pos is not None:
          arrow_info["start_pos"] = {"x": arrow.start_pos[0], "y": arrow.start_pos[1]}
        else:
          arrow_info["start_pos"] = None
        if arrow.end_pos is not None:
          arrow_info["end_pos"]   = {"x": arrow.end_pos[0], "y": arrow.end_pos[1]}
        else:
          arrow_info["end_pos"]   = None
        arrows_data.append(arrow_info)

      ruleset_data = {
        "tiles":  tiles_data,
        "arrows": arrows_data
      }

      with open(file_path, "w") as f:
        json.dump(ruleset_data, f, indent=4)
      print(f"Ruleset saved to {file_path}")
    except Exception as e:
      print(f"Error saving ruleset: {e}")

# ----------- LOAD RULESET -----------
def loadRulesetFromFile(all_tiles, placed_tiles, arrows):
  from main import tk_root
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

    placed_tiles.clear()
    arrows.clear()

    # Map tile name -> base tile
    name_tile_map = {t.name: t for t in all_tiles}

    # Rebuild placed tiles
    id_to_newcell = {}
    for tile_info in data["tiles"]:
      base_tile = name_tile_map.get(tile_info["name"])
      if not base_tile:
        print(f"Warning: Tile '{tile_info['name']}' not found in all_tiles.")
        continue

      import copy
      new_cell = copy.copy(base_tile)
      new_cell.top = []
      new_cell.bottom = []
      new_cell.left = []
      new_cell.right = []

      placed_tiles.append((new_cell, tile_info["x"], tile_info["y"], tile_info["id"]))
      id_to_newcell[tile_info["id"]] = new_cell

    # Rebuild arrows
    if "arrows" in data:
      for arrow_data in data["arrows"]:
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
