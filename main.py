from collections import deque
import random
from random import shuffle
from scipy.spatial import Voronoi
import numpy as np
from itertools import chain
import pygame
import cProfile
from map import Map
from grid import Grid

class UI:
    def __init__(self, width, height):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.font.init()
        self.font = pygame.font.SysFont("Helvetica", 24)
        self.clock = pygame.time.Clock()

    def render_text_box(self, text, x, y):
        lines = text.split('\n')
        for i, line in enumerate(lines):
            text_surface = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(text_surface, (x, y + i * 20))

    def loop(self, grid):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        grid.move_player("N")
                    elif event.key == pygame.K_DOWN:
                        grid.move_player("S")
                    elif event.key == pygame.K_LEFT:
                        grid.move_player("W")
                    elif event.key == pygame.K_RIGHT:
                        grid.move_player("E")
            # Clear the screen
            self.screen.fill((0, 0, 0))
            # Assume current_cell has the information about the player's current cell
            current_cell = grid.get_current_cell()
            text = f"Coordinates: {current_cell.coordinates}\nExits: {', '.join(current_cell.exits)}\nType: {current_cell.type}"
            self.render_text_box(text, 10, 10)

            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

grid = Grid()
grid.print_map()
map = Map(grid)





