import pygame

class GameVariables:
  FPS = 60

  FONT_BIG: pygame.font.Font = None
  FONT_MIDDLE: pygame.font.Font = None
  FONT_SMALL: pygame.font.Font = None

  @staticmethod
  def init():
    pygame.init()
    GameVariables.FONT_BIG = pygame.font.SysFont("arial", 48, bold=True)
    GameVariables.FONT_MIDDLE = pygame.font.SysFont("arial", 30, bold=False)
    GameVariables.FONT_SMALL = pygame.font.SysFont("arial", 14, bold=False)

class GameScreens:
  MAIN = "mainscreen"
  PLAY = "play"
  EXIT = "exit"
  actual = MAIN