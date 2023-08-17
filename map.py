import json
from player import Player
import pygame
import random
from room import Room

class Map:
    def __init__(self, grid):
        self.player = None
        self.player_location = None
        self.height = grid.height
        self.width = grid.width
        self.room_type_mapping = {
            'E': 'entry',
            'S': 'single',
            'D': 'double',
            'Q': 'quad',
            'M': 'multi',
        }
        self.direction_mapping = {
        "N": (0, -1),
        "S": (0, 1),
        "E": (1, 0),
        "W": (-1, 0)
        }
        self.rooms = [[None for _ in range(grid.width)] for _ in range(grid.height)]
        for y in range(grid.height):
            for x in range(grid.width):
                region = grid.grid[y][x]
                room_type = grid.room_grid[y][x]
                self.rooms[y][x] = Room(x, y, region, room_type)
        # Connecting the rooms
        for cell1, connected_cells in grid.connections.items():
            room1 = self.rooms[cell1[0]][cell1[1]]
            for cell2 in connected_cells:
                room2 = self.rooms[cell2[0]][cell2[1]]
                room1.add_connection(room2)
                room2.add_connection(room1)
        self.used_major_types = {}
        self.used_names_and_descs = {}
        self.load_json()
        self.get_regions_mapping()
        self.major_types_mapping = {}
        for region in self.regions_mapping.values():
            self.major_types_mapping[region] = {}
            for room_type in self.room_type_mapping.values():
                self.major_types_mapping[region][room_type] = list(self.data['genres']["fantasy"]['regions'][region][room_type].keys())
                random.shuffle(self.major_types_mapping[region][room_type])
        self.set_room_descriptions()
        self.choose_player_start()
        self.generated_colors = self.generate_colors(5)
        
    def print_map_info(self):
        for row in self.rooms:
            for room in row:
                connections = room.get_connections()
                print(f"Region: {room.region}, Coordinates: ({room.x}, {room.y}), Room Type: {room.room_type}, Connections: {connections}")
                print(f"Room Name: {room.name}, Desc: {room.desc}")
    def load_json(self):
        with open('data.json', 'r') as file:
            self.data = json.load(file)

    def get_regions_mapping(self):
        regions_data = list(self.data['genres']["fantasy"]['regions'].keys())
        random.shuffle(regions_data)
        self.regions_mapping = {idx: region for idx, region in enumerate(regions_data)}

    def generate_room_name_and_description(self, region_index, room_type):
        region_name = self.regions_mapping[region_index]
        room_data_type = self.room_type_mapping[room_type]
        room_data = self.data['genres']["fantasy"]['regions'][region_name][room_data_type]
        major_types = self.major_types_mapping[region_name][room_data_type]
        major_type = major_types.pop()
        if not major_types:
            self.major_types_mapping[region_name][room_data_type] = list(room_data.keys())
            random.shuffle(self.major_types_mapping[region_name][room_data_type])
        # Get the major type's name and description data
        name_data = list(room_data[major_type]['name'])
        desc_data = list(room_data[major_type]['desc'])
        # Check if shuffled lists for name and description exist for this major_type, if not create them
        if major_type not in self.used_names_and_descs:
            random.shuffle(name_data)
            random.shuffle(desc_data)
            self.used_names_and_descs[major_type] = (name_data, desc_data)
        else:
            name_data, desc_data = self.used_names_and_descs[major_type]
        # If all names/descs are used, reshuffle and start from the beginning
        if not name_data:
            name_data = list(room_data[major_type]['name'])
            random.shuffle(name_data)
        if not desc_data:
            desc_data = list(room_data[major_type]['desc'])
            random.shuffle(desc_data)
        # Pick a non-repeating name and description
        name = name_data.pop()
        desc = desc_data.pop()
        # Store the updated lists back into used_names_and_descs
        self.used_names_and_descs[major_type] = (name_data, desc_data)
        return name, desc
    
    def set_room_descriptions(self):
        for row in self.rooms:
            for room in row:
                if room.region == -1:
                    continue
                name, desc = self.generate_room_name_and_description(room.region, room.room_type)
                room.set_name_and_description(name, desc)

    def choose_player_start(self):
        valid_rooms = [(y, x) for y in range(self.height) for x in range(self.width) if self.rooms[y][x].room_type != ' ']
        if valid_rooms:
            current_y, current_x = random.choice(valid_rooms)
            self.player_location = self.rooms[current_y][current_x]
            self.player = Player(self.player_location) # ***** create the Player at this point *****
            print(f"Player starting room randomly selected at ({self.player_location.x}, {self.player_location.y})")
            return True
        else:
            print("No valid rooms found!")
            return False
    
    def get_player_location(self):
        return self.player_location
    
    def generate_colors(self, number_of_colors):
        colors = []
        min_distance = 100
        for _ in range(number_of_colors):
            max_attempts = 100
            attempts = 0
            while attempts < max_attempts:
                color = (random.randint(100,255), random.randint(100,255), random.randint(100,255))
                if all(sum(abs(c1 - c2) for c1, c2 in zip(color, existing_color)) > min_distance for existing_color in colors):
                    break
                attempts += 1
            colors.append(color)
        return colors
    
    def visualize_map(self, screen):
        player_location = self.get_player_location()
        player_color = (255, 0, 0)
        player_border_color = (255, 255, 255)
        player_border_thickness = 3
        base_colors = [(255, 255, 255)] + self.generated_colors
        cell_size = 25
        font_size = 14
        font = pygame.font.SysFont("Helvetica", font_size)
        for row in range(len(self.rooms) * 2 - 1): # Draw the grid
            for col in range(len(self.rooms[0]) * 2 - 1):
                original_row = row // 2
                original_col = col // 2
                room = self.rooms[original_row][original_col]
                # If this is a non-room cell, fill it with black
                if (row % 2 == 0 and col % 2 == 0) and (room.region == -1 or room.room_type == ""):
                    pygame.draw.rect(screen, (0, 0, 0), (col * cell_size, row * cell_size, cell_size, cell_size))
                    continue
                if room is None:
                    continue
                base_color = base_colors[room.region + 1]
                color = base_color
                # draw cells (actual rooms)
                if row % 2 == 0 and col % 2 == 0:
                    if room.room_type in 'SDMQE':
                        color = base_color
                    pygame.draw.rect(screen, color, (col * cell_size, row * cell_size, cell_size, cell_size)) # Draw cells
                    pygame.draw.rect(screen, (192, 192, 192), (col * cell_size, row * cell_size, cell_size, cell_size), 1) # Draw borders
                    if room == player_location:
                        pygame.draw.rect(screen, player_color, (col * cell_size, row * cell_size, cell_size, cell_size)) # Draw player's cell
                        pygame.draw.rect(screen, player_border_color, (col * cell_size, row * cell_size, cell_size, cell_size), player_border_thickness) # Draw unique border for player's cell
                # draw connections, horizontal and vertical
                elif row % 2 == 0 and col % 2 == 1:
                    next_room = self.rooms[original_row][original_col + 1] if original_col + 1 < len(self.rooms[0]) else None
                    if next_room and next_room in room.connections:
                        color = tuple(min(c + 50, 255) for c in base_color)
                        pygame.draw.rect(screen, color, (col * cell_size, row * cell_size, cell_size, cell_size)) # Draw cells
                        pygame.draw.rect(screen, (192, 192, 192), (col * cell_size, row * cell_size, cell_size, cell_size), 1) # Draw borders
                elif row % 2 == 1 and col % 2 == 0:
                    next_room = self.rooms[original_row + 1][original_col] if original_row + 1 < len(self.rooms) else None
                    if next_room and next_room in room.connections:
                        color = tuple(min(c + 50, 255) for c in base_color)
                        pygame.draw.rect(screen, color, (col * cell_size, row * cell_size, cell_size, cell_size)) # Draw cells
                        pygame.draw.rect(screen, (192, 192, 192), (col * cell_size, row * cell_size, cell_size, cell_size), 1) # Draw borders
                # draw room labels
                if row % 2 == 0 and col % 2 == 0:
                    if room == player_location:
                        room_label = "P"
                    else:
                        room_label = room.room_type
                    text_surface = font.render(room_label, True, (0, 0, 0))
                    # Get the size of the text surface
                    text_width, text_height = text_surface.get_size()
                    # Calculate the centered position for the text
                    text_x = col * cell_size + (cell_size - text_width) // 2
                    text_y = row * cell_size + (cell_size - text_height) // 2
                    screen.blit(text_surface, (text_x, text_y))
        pygame.display.flip()

    def move_player(self, direction):
        # Get the current coordinates of the player
        current_x, current_y = self.player_location.x, self.player_location.y
        # Define the changes in coordinates for each direction
        direction_mapping = {
            "N": (0, -1),
            "S": (0, 1),
            "E": (1, 0),
            "W": (-1, 0)
        }
        # Get the change in coordinates for the specified direction
        dx, dy = direction_mapping[direction]
        # Compute the new coordinates
        new_x, new_y = current_x + dx, current_y + dy
        # Check if the new coordinates are within the bounds of the map
        if 0 <= new_x < self.width and 0 <= new_y < self.height:
            # Get the room object at the new coordinates
            new_room = self.rooms[new_y][new_x]
            # Check if there is a connection to the new room
            if new_room in self.player_location.connections:
                # Update the player's location
                self.player_location = new_room
                return f"You have moved {direction}."
            else:
                return "You can't go that way."
        else:
            return "You can't go that way."