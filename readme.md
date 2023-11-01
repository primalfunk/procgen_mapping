# Procedurally Generated Text Adventure game

## Introduction

This project serves as a comprehensive exercise in procedural map generation using Python and Pygame. It creates a rich, multi-regional, text-based adventure world that allows for player navigation through a set of interconnected rooms. The application is designed with extensibility in mind, making it possible to easily add new genres and themes by extending the included `data.json` file.

## Features

- **Procedural Map Generation**: Creates a complex and multi-regional map dynamically.
- **Real-Time Map Visualization**: Displays the map and the player's location in real time.
- **Text-Based UI**: Provides room descriptions, attributes, and available exits in a scrolling text box.
- **Player Navigation**: Use arrow keys to move between connected rooms.
- **Dynamic Window Resizing**: Adapts the window dimensions based on the map's size.
- **Extensible Genres**: The `data.json` file includes stubs for various genres including fantasy, sci-fi alien, western, post-apocalypse, sci-fi future, noir, cyberpunk, and steampunk.

## Core Components

The project consists of five Python files, each responsible for specific functionalities:

1. **Map.py**: Responsible for the map generation, player movement, and room-to-room connections.
2. **Room.py**: Defines the `Room` class containing various attributes like coordinates, type, and description.
3. **UI.py**: Manages the Pygame-based graphical user interface for map visualization and text rendering.
4. **Grid.py**: Constructs the grid, and provides utility functions to identify adjacent cells and generate the map.
5. **Data.json**: Contains the default fantasy genre descriptions of rooms from which the maps are generated.
6. **Player.py**: Contains the player object

## Requirements

- Python 3.x
- Pygame

## Setup

```bash
# Clone the repository
git clone https://github.com/YourUsername/YourRepoName.git

# Navigate into the directory
cd YourRepoName

# Install Pygame
pip install pygame

# Run the application
python main.py

# You can control the character's position (the room displayed) using the arrow keys and the visual map displayed.
