import pygame
import random
import sys
import math

pygame.init()

TILE_SIZE = 30
grid_x, grid_y = 30,30

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Wave Function Collapse")


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

horizontal.top = [grass, horizontal]
horizontal.bottom = [grass, horizontal]
horizontal.left = [tl, bl, horizontal]
horizontal.right = [tr, br, horizontal]

vertical.top = [tl, tr, vertical]
vertical.bottom = [bl, br, vertical]
vertical.left = [grass, vertical]
vertical.right = [grass, vertical]

tl.top = [grass, horizontal, br]
tl.bottom = [vertical, bl, br]
tl.left = [grass, vertical, br]
tl.right = [horizontal, tr, br]

tr.top = [grass, horizontal, bl]
tr.bottom = [vertical, bl, br]
tr.left = [tl, horizontal, br]
tr.right = [horizontal, tr, bl]

bl.top = [vertical, tl, tr]
bl.bottom = [grass, tl, tr, horizontal]
bl.left = [grass, vertical, br, tr]
bl.right = [horizontal, tr, br]

br.top = [vertical, tl, tr]
br.bottom = [grass, horizontal, tl, tr]
br.left = [horizontal, tl, bl]
br.right = [grass, vertical, tl, bl]

grass.top = [grass, horizontal, bl, br]
grass.bottom = [grass, horizontal, tl, tr]
grass.left = [grass, vertical, tr, br]
grass.right = [grass, vertical, tl, bl]

all_tiles = [grass, horizontal, vertical, tl, tr, bl, br]

scroll_offset = 0  # Used for scrolling
scroll_speed = 10  # Speed of scrolling when the user scrolls
is_scrolling = False  # To track if the cursor is inside the rectangle

# Track dragged tiles and placed tiles
dragging_tile = None  # Holds the tile currently being dragged
dragging_offset = (0, 0)  # Offset from mouse position to tile position
placed_tiles = []  # List to store placed tiles with their positions

def draw_tile_features(tile, x, y):
    """Draw the circles and white outline for a tile, and detect edge clicks for arrows."""
    global creating_arrow, arrow_start_tile, arrow_start_edge, arrow_start_pos

    # Draw a white outline around the tile
    pygame.draw.rect(screen, (255, 255, 255), (x, y, TILE_SIZE, TILE_SIZE), 2)

    # Calculate the center points of each edge of the tile
    center_top = (x + TILE_SIZE // 2, y)
    center_bottom = (x + TILE_SIZE // 2, y + TILE_SIZE)
    center_left = (x, y + TILE_SIZE // 2)
    center_right = (x + TILE_SIZE, y + TILE_SIZE // 2)

    # Edge mappings
    edges = {
        "top": center_top,
        "bottom": center_bottom,
        "left": center_left,
        "right": center_right,
    }

    # Draw circles at the center of each edge and detect clicks
    circle_color = (255, 0, 0)  # Red color for circles
    circle_radius = 6

    for edge, center in edges.items():
        pygame.draw.circle(screen, circle_color, center, circle_radius)

        # Detect clicks for arrow creation
        mouse_x, mouse_y = pygame.mouse.get_pos()
        circle_rect = pygame.Rect(center[0] - circle_radius, center[1] - circle_radius, circle_radius * 2, circle_radius * 2)
        if circle_rect.collidepoint(mouse_x, mouse_y) and pygame.mouse.get_pressed()[0]:
            if not creating_arrow:
                # Start creating an arrow
                creating_arrow = Arrow(tile, edge)
                arrow_start_tile = tile
                arrow_start_edge = edge
                arrow_start_pos = center

    # Draw the arrow currently being created
    if creating_arrow:
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # If the mouse is over a valid end circle, snap to it
        snapping_pos = None
        for placed_tile, placed_x, placed_y in placed_tiles:
            placed_center_top = (placed_x + TILE_SIZE // 2, placed_y)
            placed_center_bottom = (placed_x + TILE_SIZE // 2, placed_y + TILE_SIZE)
            placed_center_left = (placed_x, placed_y + TILE_SIZE // 2)
            placed_center_right = (placed_x + TILE_SIZE, placed_y + TILE_SIZE // 2)

            placed_edges = {
                "top": placed_center_top,
                "bottom": placed_center_bottom,
                "left": placed_center_left,
                "right": placed_center_right,
            }

            for end_edge, end_center in placed_edges.items():
                end_circle_rect = pygame.Rect(end_center[0] - circle_radius, end_center[1] - circle_radius,
                                              circle_radius * 2, circle_radius * 2)
                if end_circle_rect.collidepoint(mouse_x, mouse_y):
                    snapping_pos = end_center

        # Update the arrow end position
        creating_arrow.start_pos = arrow_start_pos
        creating_arrow.end_pos = snapping_pos if snapping_pos else (mouse_x, mouse_y)
        creating_arrow.draw(screen)

        # Finish arrow creation when the mouse is released
        if not pygame.mouse.get_pressed()[0]:
            if snapping_pos:
                # Snap to the edge and complete the arrow
                for placed_tile, placed_x, placed_y in placed_tiles:
                    placed_center_top = (placed_x + TILE_SIZE // 2, placed_y)
                    placed_center_bottom = (placed_x + TILE_SIZE // 2, placed_y + TILE_SIZE)
                    placed_center_left = (placed_x, placed_y + TILE_SIZE // 2)
                    placed_center_right = (placed_x + TILE_SIZE, placed_y + TILE_SIZE // 2)

                    placed_edges = {
                        "top": placed_center_top,
                        "bottom": placed_center_bottom,
                        "left": placed_center_left,
                        "right": placed_center_right,
                    }

                    for end_edge, end_center in placed_edges.items():
                        if snapping_pos == end_center:
                            creating_arrow.end_tile = placed_tile
                            creating_arrow.end_edge = end_edge
                            creating_arrow.end_pos = end_center
                            arrows.append(creating_arrow)  # Add the completed arrow to the list
                            creating_arrow = None  # Reset arrow creation
                            return

            # If no valid end circle is detected, cancel the arrow creation
            creating_arrow = None


def ruleset_Screen():
    global scroll_offset, is_scrolling, dragging_tile, dragging_offset, placed_tiles, creating_arrow

    # Rectangle for the menu
    selection_x = 100
    selection_height = 400
    selection_width = 100
    selection_y = (screen.get_height() - selection_height) / 2
    
    # Inner area for clipping images
    inner_rect = pygame.Rect(selection_x, selection_y, selection_width, selection_height)
    pygame.draw.rect(screen, (0, 0, 0), inner_rect)  # Background for the inner rect

    # Calculate and draw tile pairs inside the rectangle
    tile_size = TILE_SIZE  # Using global TILE_SIZE for tiles
    spacing = 4  # Space between tiles and rows
    tiles_per_row = 2  # Number of tiles per row
    pair_width = tiles_per_row * tile_size + (tiles_per_row - 1) * spacing  # Total width of a pair

    # Calculate horizontal offset to center the pairs
    horizontal_offset = (selection_width - pair_width) // 2
    
    # Calculate vertical placement of pairs
    y_offset = selection_y + scroll_offset
    for idx, tile in enumerate(all_tiles):
        row = idx // tiles_per_row  # Determine the row index
        col = idx % tiles_per_row  # Determine the column index

        # Calculate position of the tile
        tile_x = selection_x + horizontal_offset + col * (tile_size + spacing)
        tile_y = y_offset + row * (tile_size + spacing)
        
        # Only draw the tile if it's not being dragged
        if not (dragging_tile and dragging_tile[0] == tile):
            screen.blit(tile.image, (tile_x, tile_y))

        # Detect drag start only if no arrow is being created
        mouse_x, mouse_y = pygame.mouse.get_pos()
        tile_rect = pygame.Rect(tile_x, tile_y, tile_size, tile_size)
        if tile_rect.collidepoint(mouse_x, mouse_y) and pygame.mouse.get_pressed()[0] and not dragging_tile and not creating_arrow:
            # Start dragging the tile from the menu
            dragging_tile = (tile, tile_x, tile_y)  # Store tile and original position
            dragging_offset = (mouse_x - tile_x, mouse_y - tile_y)
    
    # Draw the outline of the menu
    pygame.draw.rect(screen, (255, 255, 255), (selection_x, selection_y, selection_width, selection_height), 3)

    # Handle dragging logic
    if dragging_tile:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        tile_x = mouse_x - dragging_offset[0]
        tile_y = mouse_y - dragging_offset[1]
        screen.blit(dragging_tile[0].image, (tile_x, tile_y))  # Draw dragged tile at new position

        # Draw circles and outlines for the dragged tile
        draw_tile_features(dragging_tile[0], tile_x, tile_y)

        # Check if the mouse button is released to place the tile
        if not pygame.mouse.get_pressed()[0]:
            # Check if dragging from menu or repositioning a placed tile
            if dragging_tile in placed_tiles:
                # Update the position of the tile being moved
                placed_tiles.remove(dragging_tile)
            placed_tiles.append((dragging_tile[0], tile_x, tile_y))  # Add tile to placed tiles
            dragging_tile = None  # Stop dragging

    # Draw all placed tiles
    for tile, x, y in placed_tiles:
        screen.blit(tile.image, (x, y))
        draw_tile_features(tile, x, y)  # Draw circles and outlines

    # Handle scrolling when the mouse is inside the rectangle
    mouse_x, mouse_y = pygame.mouse.get_pos()
    is_scrolling = inner_rect.collidepoint(mouse_x, mouse_y)  # Check if the mouse is inside the box
    
    # Scrollbar Logic
    total_content_height = ((len(all_tiles) + 1) // tiles_per_row) * (tile_size + spacing)  # Total height of all rows
    if total_content_height > selection_height:
        # Scrollbar dimensions
        scrollbar_width = 10
        scrollbar_x = selection_x + selection_width - scrollbar_width
        scrollbar_height = selection_height * (selection_height / total_content_height)
        scrollbar_y = selection_y + (-scroll_offset / total_content_height) * selection_height

        # Draw the scrollbar
        pygame.draw.rect(screen, (200, 200, 200), (scrollbar_x, selection_y, scrollbar_width, selection_height))
        pygame.draw.rect(screen, (100, 100, 100), (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height))



class Arrow:
    def __init__(self, start_tile, start_edge, end_tile=None, end_edge=None):
        """
        Arrow class to represent an arrow connecting two tile edges.
        """
        self.start_tile = start_tile  # The tile where the arrow starts
        self.start_edge = start_edge  # The edge of the starting tile
        self.end_tile = end_tile  # The tile where the arrow ends
        self.end_edge = end_edge  # The edge of the ending tile
        self.start_pos = None  # Start position (center of the edge) in screen coordinates
        self.end_pos = None  # End position (center of the edge) in screen coordinates

    def draw(self, screen):
        """
        Draw the arrow on the screen.
        """
        if self.start_pos and self.end_pos:
            # Draw the arrow line
            pygame.draw.line(screen, (0, 255, 0), self.start_pos, self.end_pos, 2)

            # Draw the arrowhead
            arrow_length = 10
            angle = math.atan2(self.end_pos[1] - self.start_pos[1], self.end_pos[0] - self.start_pos[0])
            arrow_tip = self.end_pos
            arrow_left = (arrow_tip[0] - arrow_length * math.cos(angle - math.pi / 6),
                          arrow_tip[1] - arrow_length * math.sin(angle - math.pi / 6))
            arrow_right = (arrow_tip[0] - arrow_length * math.cos(angle + math.pi / 6),
                           arrow_tip[1] - arrow_length * math.sin(angle + math.pi / 6))
            pygame.draw.polygon(screen, (0, 255, 0), [arrow_tip, arrow_left, arrow_right])

# Store arrows
arrows = []

# Variables for arrow creation
creating_arrow = None  # Current arrow being created (instance of Arrow)
arrow_start_tile = None  # Tile where the arrow starts
arrow_start_edge = None  # Edge of the starting tile
arrow_start_pos = None  # Position of the starting circle

def draw_tile_features(tile, x, y):
    """Draw the circles and white outline for a tile, and detect edge clicks for arrows."""
    global creating_arrow, arrow_start_tile, arrow_start_edge, arrow_start_pos

    # Draw a white outline around the tile
    pygame.draw.rect(screen, (255, 255, 255), (x, y, TILE_SIZE, TILE_SIZE), 2)

    # Calculate the center points of each edge of the tile
    center_top = (x + TILE_SIZE // 2, y)
    center_bottom = (x + TILE_SIZE // 2, y + TILE_SIZE)
    center_left = (x, y + TILE_SIZE // 2)
    center_right = (x + TILE_SIZE, y + TILE_SIZE // 2)

    # Edge mappings
    edges = {
        "top": center_top,
        "bottom": center_bottom,
        "left": center_left,
        "right": center_right,
    }

    # Draw circles at the center of each edge and detect clicks
    circle_color = (255, 0, 0)  # Red color for circles
    circle_radius = 6

    for edge, center in edges.items():
        pygame.draw.circle(screen, circle_color, center, circle_radius)

        # Detect clicks for arrow creation
        mouse_x, mouse_y = pygame.mouse.get_pos()
        circle_rect = pygame.Rect(center[0] - circle_radius, center[1] - circle_radius, circle_radius * 2, circle_radius * 2)
        if circle_rect.collidepoint(mouse_x, mouse_y) and pygame.mouse.get_pressed()[0]:
            if not creating_arrow:
                # Start creating an arrow
                creating_arrow = Arrow(tile, edge)
                arrow_start_tile = tile
                arrow_start_edge = edge
                arrow_start_pos = center

    # Draw the arrow currently being created
    if creating_arrow:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        creating_arrow.start_pos = arrow_start_pos
        creating_arrow.end_pos = (mouse_x, mouse_y)
        creating_arrow.draw(screen)

        # Finish arrow creation when the mouse is released
        if not pygame.mouse.get_pressed()[0]:
            # Detect the ending circle if the mouse is released over another edge
            for placed_tile, placed_x, placed_y in placed_tiles:
                placed_center_top = (placed_x + TILE_SIZE // 2, placed_y)
                placed_center_bottom = (placed_x + TILE_SIZE // 2, placed_y + TILE_SIZE)
                placed_center_left = (placed_x, placed_y + TILE_SIZE // 2)
                placed_center_right = (placed_x + TILE_SIZE, placed_y + TILE_SIZE // 2)

                placed_edges = {
                    "top": placed_center_top,
                    "bottom": placed_center_bottom,
                    "left": placed_center_left,
                    "right": placed_center_right,
                }

                for end_edge, end_center in placed_edges.items():
                    end_circle_rect = pygame.Rect(end_center[0] - circle_radius, end_center[1] - circle_radius,
                                                  circle_radius * 2, circle_radius * 2)
                    if end_circle_rect.collidepoint(mouse_x, mouse_y):
                        # Complete the arrow
                        creating_arrow.end_tile = placed_tile
                        creating_arrow.end_edge = end_edge
                        creating_arrow.end_pos = end_center
                        arrows.append(creating_arrow)  # Add the completed arrow to the list
                        creating_arrow = None  # Reset arrow creation
                        return

            # If no valid end circle is detected, cancel the arrow creation
            creating_arrow = None

def draw_arrows():
    """Draw all completed arrows."""
    for arrow in arrows:
        if arrow.start_tile and arrow.start_edge and arrow.end_tile and arrow.end_edge:
            # Calculate positions dynamically from the tile and edge
            start_tile_x, start_tile_y = [
                placed_tile for placed_tile in placed_tiles if placed_tile[0] == arrow.start_tile
            ][0][1:3]
            end_tile_x, end_tile_y = [
                placed_tile for placed_tile in placed_tiles if placed_tile[0] == arrow.end_tile
            ][0][1:3]

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



def handle_scrolling(event):
    global scroll_offset
    tile_size = 16
    spacing = 4
    tiles_per_row = 2
    total_content_height = ((len(all_tiles) + 1) // tiles_per_row) * (tile_size + spacing)
    max_scroll = total_content_height - 400  # Max scroll based on selection_height

    # Check for scrolling only when the cursor is inside the rectangle
    if is_scrolling and total_content_height > 400:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                scroll_offset += scroll_speed
            elif event.button == 5:  # Scroll down
                scroll_offset -= scroll_speed

        # Clamp the scrolling to within bounds
        scroll_offset = max(min(scroll_offset, 0), -max_scroll)

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

        if 0 <= neighbor_x < grid_x and 0 <= neighbor_y < grid_y: #nOt out of bounds
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
                pygame.draw.rect(screen, (200, 200, 200), (x * TILE_SIZE + offset_x, y * TILE_SIZE + offset_y, TILE_SIZE, TILE_SIZE), 1)
                text = font.render(str(len(cell.options)), True, (255, 255, 255))
                screen.blit(text, (x * TILE_SIZE + TILE_SIZE // 4 + offset_x, y * TILE_SIZE + TILE_SIZE // 4 + offset_y))


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
       if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom) and pygame.mouse.get_pressed()[0]:
        return True

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
    
    if run_button.checkForInput() == True:
        WFC_running += 1
    elif ruleset_button.checkForInput() == True:
        ruleset_screen = True

    if WFC_running == 1:
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

    if ruleset_screen == True:
        exit_ruleset_screen = False

        while not exit_ruleset_screen:
            screen.fill((0, 0, 0))
            if exit_ruleset_screen_button.checkForInput() == True:
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
            exit_ruleset_screen_button.update()
            pygame.display.flip()
                


    run_button.update()
    ruleset_button.update()
    pygame.display.flip()
pygame.quit()
sys.exit()
