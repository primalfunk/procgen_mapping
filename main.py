from collections import deque
import random
from random import shuffle
from scipy.spatial import Voronoi
import numpy as np
from itertools import chain
import pygame
import cProfile

class Grid:
    def __init__(self):
        self.height = random.randint(22, 25)
        self.width = random.randint(22, 25)
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.room_grid = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        unique_regions = set(chain.from_iterable(self.grid))
        self.room_counts = {region: {'S': 0, 'D': 0, 'M': 0, 'Q': 0} for region in range(5)}
        self.regions = [None for _ in range(5)]
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.connections = {}
        self.generate_voronoi_grid()
        self.make_uneven_edges()
        self.fit_rooms()
        self.mark_unique_edge_rooms()
        self.make_connections()
        self.print_map()
        self.visualize_map()

    def make_uneven_edges(self):
        for row in range(len(self.grid)):
            for col in range(len(self.grid[0])):
                if row == 0 or row == len(self.grid) - 1 or col == 0 or col == len(self.grid[0]) - 1:
                    if random.random() < 0.2:
                        self.grid[row][col] = -1

    def divide_grid(self):
        total_cells = sum([row.count(0) for row in self.grid])
        region_sizes = [random.randint(total_cells // 10, total_cells // 6) for _ in range(5)]
        random.shuffle(region_sizes)
        start_row, start_col = random.randint(1, self.height - 2), random.randint(1, self.width - 2)
        self.grid[start_row][start_col] = 1
        region_index = 0
        queue = deque([(start_row, start_col, region_index)])
        while queue and region_index < 5:
            row, col, region_index = queue.popleft()
            for dr, dc in self.directions:
                new_row, new_col = row + dr, col + dc
                if (0 < new_row < self.height - 1) and (0 < new_col < self.width - 1) and self.grid[new_row][new_col] == 0:
                    self.grid[new_row][new_col] = region_index + 1
                    region_sizes[region_index] -= 1
                    if region_sizes[region_index] <= 0:
                        region_index += 1
                        if region_index >= 5:
                            break
                    queue.append((new_row, new_col, region_index))

    def fit_s(self, row, col, region):
        if self.grid[row][col] == region and not self.is_cell_occupied(row, col):
            self.room_grid[row][col] = 'S'
            self.room_counts[region]['S'] += 1
            return True
        return False

    def fit_d(self, row, col, region):
        if (col + 1 < self.width and
            self.grid[row][col] == region and self.grid[row][col + 1] == region and
            not self.is_cell_occupied(row, col) and not self.is_cell_occupied(row, col + 1)):
            self.room_grid[row][col] = 'D'
            self.room_grid[row][col + 1] = 'D'
            self.room_counts[region]['D'] += 1
            return True
        elif (row + 1 < self.height and
            self.grid[row][col] == region and self.grid[row + 1][col] == region and
            not self.is_cell_occupied(row, col) and not self.is_cell_occupied(row + 1, col)):
            self.room_grid[row][col] = 'D'
            self.room_grid[row + 1][col] = 'D'
            self.room_counts[region]['D'] += 1
            return True
        return False

    def fit_q(self, row, col, region):
        if (row + 1 < self.height and col + 1 < self.width and
            self.grid[row][col] == region and self.grid[row + 1][col] == region and
            self.grid[row][col + 1] == region and self.grid[row + 1][col + 1] == region and
            not self.is_cell_occupied(row, col) and not self.is_cell_occupied(row + 1, col) and
            not self.is_cell_occupied(row, col + 1) and not self.is_cell_occupied(row + 1, col + 1)):
            self.room_grid[row][col] = 'Q'
            self.room_grid[row + 1][col] = 'Q'
            self.room_grid[row][col + 1] = 'Q'
            self.room_grid[row + 1][col + 1] = 'Q'
            self.room_counts[region]['Q'] += 1
            return True
        return False

    def fit_m(self, row, col, region):
        shapes = [[(0, 0), (0, 1), (0, 2)], [(0, 0), (1, 0), (2, 0)], [(0, 0), (1, 0), (1, 1)], [(0,0), (0,1), (1,1)]]
        for shape in shapes:
            if all(0 <= row + dr < self.height and 0 <= col + dc < self.width and 
                self.grid[row + dr][col + dc] == region and 
                not self.is_cell_occupied(row + dr, col + dc) for dr, dc in shape):
                for dr, dc in shape:
                    self.room_grid[row + dr][col + dc] = 'M'
                    self.room_counts[region]['M'] += 1
                return True
        return False

    def fit_rooms(self):
        self.room_grid = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        room_type_counts = {region: {'Q': 0, 'S': 0, 'D': 0, 'M': 0} for region in range(5)}
        for region in range(0, 5):
            for row in range(self.height):
                for col in range(self.width):
                    if self.grid[row][col] != region:
                        continue
                    room_type = self.choose_room_type()
                    while room_type == 'Q' and room_type_counts[region]['Q'] >= 2:
                        chances_without_q = {'S': 0.35, 'D': 0.3, 'M': 0.25}
                        room_type = random.choices(list(chances_without_q.keys()), weights=list(chances_without_q.values()))[0]
                    fitting_method = getattr(self, f'fit_{room_type.lower()}')
                    if fitting_method(row, col, region):
                        room_type_counts[region][room_type] += 1
                        continue
        for row in range(self.height):
            for col in range(self.width):
                if self.room_grid[row][col] == ' ':
                    region = self.grid[row][col]
                    if not region == -1:
                        self.fit_s(row, col, region)

    def is_cell_occupied(self, row, col):
        return self.room_grid[row][col] != ' '

    def print_map(self):
        for row in range(self.height):
            row_line = ""
            for col in range(self.width):
                room = self.room_grid[row][col]
                row_line += room
                # Add horizontal connection if there's a connection to the right
                if self.is_connected((row, col), (row, col + 1)):
                    row_line += "-"
                else:
                    row_line += " "
            print(row_line)
            # Print vertical connections
            if row < self.height - 1:
                for col in range(self.width):
                    if self.is_connected((row, col), (row + 1, col)):
                        print("|", end=" ")
                    else:
                        print(" ", end=" ")
                print()

    def choose_room_type(self):
        chances = {'Q': 0.1, 'S': 0.35, 'D': 0.3, 'M': 0.25}
        return random.choices(list(chances.keys()), weights=list(chances.values()))[0]

    def generate_voronoi_grid(self):
        points = np.random.rand(5, 2)
        points[:, 0] *= self.width
        points[:, 1] *= self.height
        vor = Voronoi(points)
        for y in range(self.height):
            for x in range(self.width):
                min_dist = float('inf')
                region = -1
                for i, point in enumerate(vor.points):
                    dist = (x - point[0]) ** 2 + (y - point[1]) ** 2
                    if dist < min_dist:
                        min_dist = dist
                        region = i
                self.grid[y][x] = region

    def mark_unique_edge_rooms(self):
        borders = {}
        for row in range(self.height - 1):
            for col in range(self.width - 1):
                if 0 <= self.grid[row][col] <= 4 and 0 <= self.grid[row][col + 1] <= 4 and self.grid[row][col] != self.grid[row][col + 1]:
                    regions = tuple(sorted([self.grid[row][col], self.grid[row][col + 1]]))
                    borders.setdefault(regions, []).append((row, col, 'H'))
                if 0 <= self.grid[row][col] <= 4 and 0 <= self.grid[row + 1][col] <= 4 and self.grid[row][col] != self.grid[row + 1][col]:
                    regions = tuple(sorted([self.grid[row][col], self.grid[row + 1][col]]))
                    borders.setdefault(regions, []).append((row, col, 'V'))
        for border_points in borders.values():
            border_points.sort(key=lambda x: (x[0], x[1]))
            midpoint_index = len(border_points) // 2
            row, col, orientation = border_points[midpoint_index]
            if orientation == 'H':
                self.room_grid[row][col] = 'E'
                self.room_grid[row][col + 1] = 'E'
            elif orientation == 'V':
                self.room_grid[row][col] = 'E'
                self.room_grid[row + 1][col] = 'E'

    def connect_within_room_types(self, region):
        for row in range(len(region)):
            for col in range(len(region[0])):
                cell_type = region[row][col]
                if cell_type in ['D', 'Q', 'M']:
                    for d_row, d_col in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                        next_row, next_col = row + d_row, col + d_col
                        if 0 <= next_row < len(region) and 0 <= next_col < len(region[0]) and region[next_row][next_col] == cell_type:
                            self.connect_cells((row, col), (next_row, next_col))

    def make_connections(self):
        # Loop through the entire grid
        for row in range(self.height):
            for col in range(self.width):
                # Identify the room type at the current cell
                cell_type = self.room_grid[row][col]
                # Skip if the cell is not of a type that can connect
                if cell_type not in ['D', 'Q', 'M']:
                    continue
                # Check neighboring cells in all four directions
                for d_row, d_col in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                    next_row, next_col = row + d_row, col + d_col
                    # If the neighboring cell is within bounds, of the same type, and in the same region, connect the cells
                    if (0 <= next_row < self.height and 0 <= next_col < self.width
                        and self.room_grid[next_row][next_col] == cell_type
                        and self.is_same_region((row, col), (next_row, next_col))):
                        self.connect_cells((row, col), (next_row, next_col))
        self.connect_S_rooms()
        self.connect_E_rooms()
        self.connect_isolated_islands()
    
    def connect_cells(self, cell1, cell2):
        if cell1 not in self.connections:
            self.connections[cell1] = []
        self.connections[cell1].append(cell2)
        if cell2 not in self.connections:
            self.connections[cell2] = []
        self.connections[cell2].append(cell1)

    def is_connected(self, cell1, cell2):
        return cell2 in self.connections.get(cell1, []) or cell1 in self.connections.get(cell2, [])

    def is_same_region(self, cell1, cell2):
        row1, col1 = cell1
        row2, col2 = cell2
        return self.grid[row1][col1] == self.grid[row2][col2]

    def connect_E_rooms(self):
        for row in range(self.height):
            for col in range(self.width):
                if self.room_grid[row][col] == 'E':
                    for d_row, d_col in self.directions:
                        next_row, next_col = row + d_row, col + d_col
                        if (0 <= next_row < self.height and 0 <= next_col < self.width
                            and self.room_grid[next_row][next_col] == 'E'
                            and not self.is_same_region((row, col), (next_row, next_col))):
                            # Connect "E" rooms to each other
                            self.connect_cells((row, col), (next_row, next_col))
                            
                            # Make up to 3 additional random connections within the region for both "E" rooms
                            for _ in range(3):
                                random.shuffle(self.directions)
                                for dr, dc in self.directions:
                                    r1, c1 = row + dr, col + dc
                                    r2, c2 = next_row + dr, next_col + dc
                                    if (0 <= r1 < self.height and 0 <= c1 < self.width
                                        and self.is_same_region((row, col), (r1, c1))):
                                        self.connect_cells((row, col), (r1, c1))
                                    if (0 <= r2 < self.height and 0 <= c2 < self.width
                                        and self.is_same_region((next_row, next_col), (r2, c2))):
                                        self.connect_cells((next_row, next_col), (r2, c2))

    def connect_S_rooms(self):
        for row in range(self.height):
            for col in range(self.width):
                if self.room_grid[row][col] == 'S':
                    random.shuffle(self.directions)  # Shuffle directions to add randomness
                    connections_count = random.choices([2, 3, 4], weights=[0.2, 0.5, 0.3])[0]
                    connected = 0
                    for d_row, d_col in self.directions:
                        next_row, next_col = row + d_row, col + d_col
                        if (0 <= next_row < self.height and 0 <= next_col < self.width
                            and self.is_same_region((row, col), (next_row, next_col))):
                            self.connect_cells((row, col), (next_row, next_col))
                            connected += 1
                            if connected == connections_count:
                                break

    def connect_isolated_islands(self):
        for row in range(self.height):
            for col in range(self.width):
                # Find a connected room to start BFS
                start_cell = (row, col)
                start_region = self.grid[row][col]
                visited = set(start_cell)
                queue = deque([start_cell])
                while queue:
                    current_cell = queue.popleft()
                    for dr, dc in self.directions:
                        next_row, next_col = current_cell[0] + dr, current_cell[1] + dc
                        next_cell = (next_row, next_col)
                        if (0 <= next_row < self.height and 0 <= next_col < self.width
                            and next_cell not in visited
                            and self.is_same_region(current_cell, next_cell)
                            and self.is_connected(current_cell, next_cell)):
                            visited.add(next_cell)
                            queue.append(next_cell)
                region_cells = {(r, c) for r in range(self.height) for c in range(self.width) if self.grid[r][c] == start_region}
                isolated_cells = region_cells - visited
                for cell in isolated_cells:
                    for dr, dc in self.directions:
                        next_row, next_col = cell[0] + dr, cell[1] + dc
                        next_cell = (next_row, next_col)
                        if (0 <= next_row < self.height and 0 <= next_col < self.width
                            and self.grid[next_row][next_col] == start_region
                            and next_cell in visited):
                            self.connect_cells(cell, next_cell)
                            break

    def visualize_map(self):
        base_colors = [(255, 255, 255), (0, 0, 255), (0, 255, 0), (255, 255, 0), (0, 255, 255), (255, 0, 255)]
        cell_size = 25
        pygame.init()
        pygame.font.init()
        font_size = 14
        font = pygame.font.SysFont("Helvetica", font_size)
        screen = pygame.display.set_mode((self.width * 2 * cell_size - cell_size, self.height * 2 * cell_size - cell_size))
        for row in range(self.height * 2 - 1): # Draw the grid
            for col in range(self.width * 2 - 1):
                original_row = row // 2
                original_col = col // 2
                base_color = base_colors[self.grid[original_row][original_col] + 1]
                color = base_color  # Default color
                if row % 2 == 0 and col % 2 == 0: # Modify color based on room type
                    room_type = self.room_grid[original_row][original_col]
                    if room_type in 'SDMQE':
                        color = base_color
                    pygame.draw.rect(screen, color, (col * cell_size, row * cell_size, cell_size, cell_size)) # Draw cells
                    pygame.draw.rect(screen, (192, 192, 192), (col * cell_size, row * cell_size, cell_size, cell_size), 1) # Draw borders
                    if room_type != ' ': # Draw room label
                        font_size = 30  # Increase font size for debugging
                        text_color = (0, 0, 0) # should be black
                        font = pygame.font.Font(None, font_size) # Update font size
                        text_surface = font.render(room_type, True, text_color)
                        text_x = col * cell_size + 5  # Fixed position within cell for debugging
                        text_y = row * cell_size + 5
                        screen.blit(text_surface, (text_x, text_y))
                elif row % 2 == 0 and col % 2 == 1 and self.is_connected((original_row, original_col), (original_row, original_col + 1)):
                    color = tuple(min(c + 50, 255) for c in base_color)
                    pygame.draw.rect(screen, color, (col * cell_size, row * cell_size, cell_size, cell_size)) # Draw cells
                    pygame.draw.rect(screen, (192, 192, 192), (col * cell_size, row * cell_size, cell_size, cell_size), 1) # Draw borders
                elif row % 2 == 1 and col % 2 == 0 and self.is_connected((original_row, original_col), (original_row + 1, original_col)):
                    color = tuple(min(c + 50, 255) for c in base_color)
                    pygame.draw.rect(screen, color, (col * cell_size, row * cell_size, cell_size, cell_size)) # Draw cells
                    pygame.draw.rect(screen, (192, 192, 192), (col * cell_size, row * cell_size, cell_size, cell_size), 1) # Draw borders
        pygame.display.flip()
        running = True  # Keep the window open until it's manually closed
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
        pygame.quit()


cProfile.run("grid_obj = Grid()")


