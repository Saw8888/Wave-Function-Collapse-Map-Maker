import pygame

class Button:
  def __init__(self, image, x_pos, y_pos, text_input, font):
    self.image = image
    self.x_pos = x_pos
    self.y_pos = y_pos
    self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
    self.text_input = text_input
    self.font = font
    self.text = self.font.render(self.text_input, True, "white")
    self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

  def update(self, screen):
    screen.blit(self.image, self.rect)
    screen.blit(self.text, self.text_rect)
    self.changeColor()

  def checkForInput(self):
    position = pygame.mouse.get_pos()
    if self.rect.collidepoint(position) and pygame.mouse.get_pressed()[0]:
      return True
    return False

  def changeColor(self):
    position = pygame.mouse.get_pos()
    if (self.rect.left <= position[0] <= self.rect.right and
        self.rect.top <= position[1] <= self.rect.bottom):
      self.text = self.font.render(self.text_input, True, "green")
    else:
      self.text = self.font.render(self.text_input, True, "white")
