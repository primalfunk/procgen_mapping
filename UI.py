import pygame

class UI:
    def __init__(self, map):
        cell_size = 25
        self.text_scroll_offset = 0
        width = (map.width * 2 - 1) * cell_size
        height = (map.height * 2 - 1) * cell_size
        pygame.init()
        self.screen = pygame.display.set_mode((width * 2, height))
        pygame.font.init()
        self.font = pygame.font.SysFont("Helvetica", 24)
        self.clock = pygame.time.Clock()
        self.map = map
        self.show_UI()

    def render_text_box(self, text, x, y):
        font_size = 30
        font = pygame.font.SysFont("Helvetica", font_size)
        text_color = (255, 255, 255)
        box_width = self.screen.get_width() // 2 - 20
        box_height = self.screen.get_height() - 20
        padding = 5
        line_spacing = 4
        font_height = font.get_linesize()
        # Break the text into lines, considering newline characters
        paragraphs = text.split('\n')
        lines = []
        for paragraph in paragraphs:
            words = paragraph.split(' ')
            line = ''
            while words:
                if font.size(line + words[0])[0] <= box_width - padding * 2:
                    line += (words.pop(0) + ' ')
                else:
                    lines.append(line)
                    line = ''
            lines.append(line)
        # Draw the text box
        pygame.draw.rect(self.screen, (0, 0, 0), (x, y, box_width, box_height))
        pygame.draw.rect(self.screen, text_color, (x, y, box_width, box_height), 1)
        # Render the text with the scroll offset
        for i, line in enumerate(lines):
            text_surface = font.render(line, True, text_color)
            self.screen.blit(text_surface, (x + padding, y + padding + i * (font_height + line_spacing) - self.text_scroll_offset))

    def get_directions(self, current_cell, connected_cells):
        directions = []
        x_current, y_current = current_cell
        for cell in connected_cells:
            x, y = cell
            if x == x_current and y < y_current:
                directions.append("North")
            elif x == x_current and y > y_current:
                directions.append("South")
            elif y == y_current and x < x_current:
                directions.append("West")
            elif y == y_current and x > x_current:
                directions.append("East")
        return directions

    def show_UI(self):
        running = True
        action = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4: # scroll up
                        self.text_scroll_offset = max(self.text_scroll_offset -14, 0)
                    elif event.button == 5: # scroll down
                        self.text_scroll_offset += 14
                if event.type == pygame.KEYDOWN:
                    action = True
                    if event.key == pygame.K_UP:
                        self.map.move_player("N")
                    elif event.key == pygame.K_DOWN:
                        self.map.move_player("S")
                    elif event.key == pygame.K_LEFT:
                        self.map.move_player("W")
                    elif event.key == pygame.K_RIGHT:
                        self.map.move_player("E")
            # Calculate the required width for the map
            map_width = self.map.width * 25 * 2 - 25
            map_height = self.map.height * 25 * 2 - 25
            if action:
                self.screen.fill((0, 0, 0))
            if self.screen.get_width() < map_width * 2:
                # Resize the main window if needed
                new_width = map_width * 2
                new_height = max(map_height, self.screen.get_height())
                self.screen = pygame.display.set_mode((new_width, new_height))
            # Create the map surface
            map_surface = pygame.Surface((map_width, map_height))
            self.map.visualize_map(map_surface)
            self.screen.blit(map_surface, (self.screen.get_width() - map_width, 0))
            # Render the UI in the left half of the window
            if action:
                player_location = self.map.get_player_location()
                connections = player_location.get_connections()
                exits = self.get_directions((player_location.x, player_location.y), connections)
                text = f"Coordinates: ({player_location.x}, {player_location.y})\nRegion: {player_location.region}\nType: {player_location.room_type}\n\nName: {player_location.name}\n\nDescription: {player_location.desc}"
                text += f"\n\nYou can see exits: {exits}"
                self.render_text_box(text, 10, 10)
                action = False
            pygame.display.flip()
            self.clock.tick(30)
        pygame.quit()