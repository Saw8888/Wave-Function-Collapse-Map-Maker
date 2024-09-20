import pygame

pygame.init()

WIDTH, HEIGHT = 600, 600
grid_x = 30
grid_y = 30
tile_x = 16
tile_y = 16

screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("CS IA")

grid = [[tile() for x in range(tile_x)] for y in range(tile_y)]

class tile:
    def __init__(self, file):
        self.file = file
        self.right = []
        self.left = []
        self.bottom = []
        self.top = []

    def right(self, neibour):
        if(type(neibour) == list):
            self.right.extend(neibour)
        else:
            self.right.append(neibour)
    def left(self, neibour):
        if(type(neibour) == list):
            self.left.extend(neibour)
        else:
            self.left.append(neibour)
    def bottom(self, neibour):
        if(type(neibour) == list):
            self.bottom.extend(neibour)
        else:
            self.bottom.append(neibour)
    def top(self, neibour):
        if(type(neibour) == list):
            self.top.extend(neibour)
        else:
            self.top.append(neibour)

def draw_grid(grid):
    for col in range(grid_y):
        for row in range(grid_x):
            tile = grid[col][row]
            if tile:
                image = pygame.image.load(tile.file)
                image = pygame.transform.scale(image, (tile_x,tile_y))
                screen.blit(image, (col*tile_y, row*tile_y))

    for x in range(0, WIDTH, grid_x):
        pygame.draw.line(screen, (255,255,255), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, grid_y):
        pygame.draw.line(screen, (255,255,255), (0, y), (WIDTH, y))


grass = tile("Sprites/Grass")
horizontal = tile("Sprites/Horizontal_Fence")
vertical = tile("Sprites/Vertical_Fence")
tl = tile("Sprites/Top_Left_Fence")
tr = tile("Sprites/Top_Right_Fence")
bl = tile("Sprites/Bottom_Left_Fence")
br = tile("Sprites/Bottom_Right_Fence")

horizontal.left([tl,bl])
horizontal.right([tr,br])
horizontal.top([grass,horizontal])
horizontal.bottom([grass,horizontal])

vertical.left([grass,vertical])
vertical.right([grass,vertical])
vertical.top([tl,tr])
vertical.bottom([bl,br])

tl.left([grass,vertical])
tl.right([horizontal,tr,br])
tl.top([grass,horizontal])
tl.bottom([vertical, bl,br])

tr.left([tl,horizontal,br])
tr.right([horizontal,tr])
tr.top([grass,horizontal])
tr.bottom([vertical, bl,br])

bl.left([grass,vertical])
bl.right([horizontal,tl,tr])
bl.top([vertical,tl,bl])
bl.bottom([grass,vertical])

br.left([horizontal,tl,tr])
br.right([grass,vertical])
br.top([vertical,tr,br])
br.bottom([grass,vertical])

grass.left([grass,vertical,tl,bl])
grass.right([grass,vertical,tr,br])
grass.top([grass,horizontal,tl,tr])
grass.bottom([grass,horizontal,bl,br])
