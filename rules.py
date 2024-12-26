def generateRulesetFromArrows():
  global all_tiles, placed_tiles, arrows
  for tile in all_tiles:
    tile.top, tile.bottom, tile.left, tile.right = [], [], [], []

  placed_tile_dict = {tile_id: tile for tile, _, _, tile_id in placed_tiles}
  for arrow in arrows:
    if arrow.start_tile_id in placed_tile_dict and arrow.end_tile_id in placed_tile_dict:
      start_tile = placed_tile_dict[arrow.start_tile_id]
      end_tile = placed_tile_dict[arrow.end_tile_id]
      if arrow.start_edge == "top":
        start_tile.top.append(end_tile)
      elif arrow.start_edge == "bottom":
        start_tile.bottom.append(end_tile)
      elif arrow.start_edge == "left":
        start_tile.left.append(end_tile)
      elif arrow.start_edge == "right":
        start_tile.right.append(end_tile)
