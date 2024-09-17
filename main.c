#include "GGD.h"
#include <math.h>
#include <time.h>
#include <stdio.h>
#include <stdlib.h>

#define pixelScale 1
#define GLW 1000
#define GLH 500

#define GRID_WIDTH 10
#define GRID_HEIGHT 10
#define SQUARE_SIZE 20

typedef enum {
 BLUE,
 YELLOW,
 GREEN,
 GRAY,
 UNDETERMINED
} Color;

typedef struct {
 Color color;
 int colors[4];  // BLUE, YELLOW, GREEN, GRAY
 int numcolors;
 int collapsed;
} Cube;

Cube grid[GRID_WIDTH][GRID_HEIGHT];

void drawSquare(int x, int y, int width, int height, int color);

int isValid(int x, int y, int color) {
  if (color == BLUE) {
    if ((x + 1 < GRID_WIDTH && grid[x + 1][y].collapsed && grid[x + 1][y].color != YELLOW) ||
        (y + 1 < GRID_HEIGHT && grid[x][y + 1].collapsed && grid[x][y + 1].color != YELLOW) ||
        (y - 1 >= 0 && grid[x][y - 1].collapsed && grid[x][y - 1].color != YELLOW)) {
      return 0;
    }
  } else if (color == YELLOW) {
    // Yellow can only have green to the right
    if (x + 1 < GRID_WIDTH && grid[x + 1][y].collapsed && grid[x + 1][y].color != GREEN) {
      return 0;
    }
  }
  // Green and gray can be placed anywhere
  return 1;
}

void collapse(int x, int y) {
  pixelData colors[] = {(pixelData){0,0,255},(pixelData){255,255,0},(pixelData){0,255,0},(pixelData){100,100,100}};
  for (int i = 0; i < grid[x][y].numcolors; i++) {
    int j = rand() % grid[x][y].numcolors;
    int temp = grid[x][y].colors[i];
    grid[x][y].colors[i] = grid[x][y].colors[j];
    grid[x][y].colors[j] = temp;
  }

  for (int i = 0; i < grid[x][y].numcolors; i++) {
    int color = grid[x][y].colors[i];
    if (isValid(x, y, color)) {
      grid[x][y].color = color;
      grid[x][y].collapsed = 1;
      DS(x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE, colors[color]);
      return;
    }
  }

  // Gay default
  grid[x][y].color = GRAY;
  grid[x][y].collapsed = 1;
  DS(x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE, colors[3]);
}

// Initializes superpositioned cubes
void initializeGrid() {
  for (int i = 0; i < GRID_WIDTH; i++) {
    for (int j = 0; j < GRID_HEIGHT; j++) {
      grid[i][j].color = UNDETERMINED;
      grid[i][j].collapsed = 0;
      grid[i][j].colors[0] = BLUE;
      grid[i][j].colors[1] = YELLOW;
      grid[i][j].colors[2] = GREEN;
      grid[i][j].colors[3] = GRAY;
      grid[i][j].numcolors = 4;
    }
  }
}


int main(int argc, char** argv) {
 matrix specs;
 screen dimensions;
 dimensions.name = "Main";
 dimensions.width = GLW;
 dimensions.height = GLH;

 setupScreen(&dimensions);

 specs.posX = 0;
 specs.posY = 0;
 specs.height = GLH;
 specs.width = GLW;
 specs.pointSize = pixelScale;
 specs.matrix = createMatrix(specs);

 setActiveMatrix(&specs);

 srand((unsigned int)time(NULL));
 initializeGrid();

 for (int x = 0; x < GRID_WIDTH; x++) {
    for (int y = 0; y < GRID_HEIGHT; y++) {
      collapse(x, y);
    }
  }

 while (!windowClosed(&dimensions)) {
  updateScreen(&dimensions, &specs);
 }

 terminateScreen(&dimensions, &specs);
 return 0;
}
