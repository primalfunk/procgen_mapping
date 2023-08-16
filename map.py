import json
import random
from room import Room

class Map:
    def __init__(self, grid):
        self.room_type_mapping = {
            'E': 'entry',
            'S': 'single',
            'D': 'double',
            'Q': 'quad',
            'M': 'multi',
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
        self.print_map_info()
        
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
        print(self.regions_mapping)

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