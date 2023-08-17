class Room:
    def __init__(self, x, y, region, room_type):
        self.x = x
        self.y = y
        self.region = region
        self.room_type = room_type  # S, D, M, Q, E, or blank
        self.connections = set()
        self.name = ""
        self.desc = ""

    def add_connection(self, room):
        self.connections.add(room)

    def get_connections(self):
        return [(conn.x, conn.y) for conn in self.connections]
    
    def set_name_and_description(self, name, description):
        self.name = name.title()
        self.desc = description
