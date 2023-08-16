from collections import deque
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
import random
from random import shuffle
from scipy.spatial import Voronoi
import numpy as np
from itertools import chain

class Map:
    def __init__(self):
        self.height = random.randint(22, 25)
        self.width = random.randint(22, 25)
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.room_grid = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        unique_regions = set(chain.from_iterable(self.grid))
        self.room_counts = {region: {'S': 0, 'D': 0, 'M': 0, 'Q': 0} for region in range(5)}

    def make_uneven_edges(self):
        for row in range(len(self.grid)):
            for col in range(len(self.grid[0])):
                if row == 0 or row == len(self.grid) - 1 or col == 0 or col == len(self.grid[0]) - 1:
                    if random.random() < 0.2:  # chance of removing an edge cell
                        self.grid[row][col] = -1

    def divide_grid(self):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        total_cells = sum([row.count(0) for row in self.grid])
        region_sizes = [random.randint(total_cells // 10, total_cells // 6) for _ in range(5)]
        random.shuffle(region_sizes)
        start_row, start_col = random.randint(1, self.height - 2), random.randint(1, self.width - 2)
        self.grid[start_row][start_col] = 1
        region_index = 0
        queue = deque([(start_row, start_col, region_index)])
        while queue and region_index < 5:
            row, col, region_index = queue.popleft()
            for dr, dc in directions:
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
        # Try horizontal placement
        if (col + 1 < self.width and
            self.grid[row][col] == region and self.grid[row][col + 1] == region and
            not self.is_cell_occupied(row, col) and not self.is_cell_occupied(row, col + 1)):
            
            self.room_grid[row][col] = 'D'
            self.room_grid[row][col + 1] = 'D'
            self.room_counts[region]['D'] += 1
            return True
        # Try vertical placement
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
        for row in self.room_grid:
            print(''.join(row))

    def visualize_grid(self):
        region_counts = {-1: 0, 0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
        total_cells = 0
        for row in self.grid:
            for cell in row:
                region_counts[cell] += 1
                total_cells += 1
        print("Total Cells:", total_cells)
        for region, count in region_counts.items():
            if region == -1:
                print(f"Removed Cells: {count}")
            else:
                print(f"Region {region} Cells: {count}")
        colors = ['white', 'blue', 'green', 'red', 'purple', 'orange']
        cmap = LinearSegmentedColormap.from_list("custom", colors, N=len(colors))
        norm = Normalize(vmin=-1, vmax=4)
        plt.imshow(self.grid, cmap=cmap, norm=norm)
        plt.axis('off')
         # Add room labels
        for row in range(self.height):
            for col in range(self.width):
                label = self.room_grid[row][col]
                if label != ' ':
                    plt.text(col, row, label, ha='center', va='center', color='black')
        plt.show()

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


map_obj = Map()
map_obj.generate_voronoi_grid()
map_obj.make_uneven_edges()
map_obj.fit_rooms()
map_obj.visualize_grid()
map_obj.print_map()