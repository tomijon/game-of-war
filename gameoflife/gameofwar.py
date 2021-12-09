"""Game of War

Multiple teams.

Cells cannot die by isolation or cramming. Cells only die of old age (set by
death-age property).

Dead cells that are surrounded by 3 or more cells come to life. They are
controlled by the the dominant team (the team with the most cells surrounding
it). In the event of a tie, the team with the most cells takes control.

Alive cells can be killed by enemy cells when there are 3 or enemy cells
surrounding it. The alive cell is consumed by the team with the most
neighbours if their neighbours is at least 3.

The winning team is the team with the most cells after the round timer runs out
or the last team standing (e.g one team left)
"""
import time
import os
import multiprocessing
from sys import stdout
from gameoflife.cell import Cell
from gameoflife.team import Team

properties = dict()
bounds = dict()

class GameOfWar():
    """Class for defining attributes of a game of war."""
    def __init__(self):
        """Initialises the property dictionary and cells dictionary.
        """
        self.properties = dict()
        self.validations = dict()
        self.cells = dict()
        
        self.load_defaults()

    def load_defaults(self):
        """Sets all the properties to their default values.
        Called on initialisation of the module.

        Properties are:
            - width     the width of the grid
                            - max=100
                            - min=10
                            - default=30
            - height    the height of the grid
                            - max=50
                            - min=10
                            - default=30
            - refresh   how many times per second the grid will update
                            - max=60
                            - min=1
                            - default=4
            - death-age how many updates before the cells die
                            - max=32
                            - min=1
                            - default=4
            - win-round how many rounds there are before the game will end.
                            - max=65536
                            - min=128
                            - default=512
            - to-kill   how many neighbouring enemies are needed to kill a cell.
                            - max=8
                            - min=1
                            - default=3
        """
        properties["width"] = 30
        validations["width"] = (between, (10, 100))
        
        properties["height"] = 30
        validations["height"] = (between, (10, 50))
        
        properties["refresh"] = 4
        validations["refresh"] = (between, (1, 60))
        
        properties["death-age"] = 4
        validations["death-age"] = (between, (1, 32))
        
        properties["win-round"] = 512
        validations["win-round"] = (between, (128, 65536))
        
        properties["to-kill"] = 3
        validations["to-kill"] = (between, (1, 8))
            
    def set_property(self, prop, val):
        """Sets the given property to the given value.

        Parameters:
            - prop      The property to change
            - val       The value to change the property to

        Raises:
            - ValueError
        """
        # Check prop is valid.
        if prop not in self.properties:
            raise ValueError(f"'{prop}' is not a valid property.")
        # Convert val to int if possible.
        if val.isdigit():
            val = int(val)

        # Validate the value.
        if self.validate(prop, val):
            self.properties[prop] = val
        else:
            raise ValueError(f"'{val}' is not valid for property: '{prop}'")
              
    def _validate(self, prop, val):
        """Validates the input on a property.

        Parameters:
            - prop      The property the value is being added to
            - val       The value to be validated

        Returns:
            True if the value is valid.
        """
        func, args = self.validations["prop"]
        return func(val, *args)

    def load_config(self, config):
        """Loads properties from a config into the properties dictionary.

        Parameters:
            - File path for the config.
        """
        # Load configuration.
        with open(config) as config:
            for line in config:
                self.set_property(*line.strip().split(":"))

    def _generate_grid(self):
        """Generates a grid of dead cells of size width, height.

        The default 'view' of a dead cell is '.'
        
        Returns:
            - a 2D array of dead cells.
        """
        width = properties["width"]
        height = properties["height"]
        return [["." for x in range(width)] for y in range(height)]

    def load_game(self, directory):
        """Loads a game from a directory.

        Directory must include:
            - a .data file
            - a .config file
            - a .cells file

        Directory loading is relative and must start with a '/'.
        Directory must only contain 1 file of each type. Other files are allowed
        but must not end in .data, .config or .cells
        
        Parameters:
            - directory     A string path to a directory containing a game
                            to load

        Raises:
            - ValueError
            - FileNotFoundError
        """
        files_in_dir = os.listdir(os.curdir + directory)
        # Count number of files ending in .data, .config and .cells.
        reserved = {"data":0, "config":0, "cells":0}
        for file in files_in_dir:
            file_type = file.split(".")[-1]

            # Check if needed file.
            if file_type in reserved.keys():
                reserved[file_type] += 1
                # Check cound.
                if reserved[file_type] > 1:
                    break
        else:
            # Check all files are there.
            if sum(reserved.values()) == 3:
                return

        raise ValueError("Expected 1 of each unique file (.data, .config, .cells).")
        
        
def between(target, lower, higher):
    """Determines if the target number is between lower and higher (including
    both end points).

    Parameters:
        - lower     The lower bound of the range.
        - higher    The higher bound of the range.
        - target    The number to check.

    Returns:
        True if the target is between the lower and higher bounds (including both
            end points)
    """
    return lower <= target <= higher




























































































def generate(file):
    """Initialise a dictionary of cells from a file.

    For each new cell (that isn't a dead cell) that doesn't exist, a new team
    is created for that cell group.

    The width and height properties are changed accordingly.
    
    Parameters:
        file    - The file to read from.

    Returns:
        A tuple containing:
            - dict object of cells
            - a dict object of teams (maps a team to itself)
        in  the formate (cells, teams).
    """
    global cells
    global teams
    cells = dict()
    teams = dict()
    
    with open(file) as readable:
        for y, row in enumerate(readable):
            row = row.strip()
            for x, cell in enumerate(row):
                if cell == ".":
                    continue
                # Create a new team.
                if cell not in teams:
                    new_team = Team(cell)
                    teams[new_team.view] = new_team
                
                team = teams[cell]
                team.score += 1
                cells[(x, y)] = Cell(x, y, team, properties["death-age"])
        # Update properties.
        properties["width"] = x + 1
        properties["height"] = y + 1
        
    return cells, teams

def update_grid(grid, cells):
    """Places all the cells in the given grid.
    Parameters:
        - grid      The grid to place the cells in
        - cells     The cells to place in the grid
    """
    for position, cell in cells.items():
        grid[position[1]][position[0]] = cell.team.view
        
    return grid
    
def reload(properties):
    """Removes all values from the cells set and clears the grid.
    Returns:
        - a tuple in the form of
        (new 2D of empty strings, empty set of cells)
    """
    return generate_grid(properties), dict()

def get_neighbours(cells, x, y):
    """Finds all neighbours (the 8 surrounding squares) of a cell.

    Parameters:
        - cells     The set of cells to search in.
        - x         The x position of the cell to search around.
        - y         The y position fo the cell to search around.

    Returns:
        A list object of neighbouring cells.
    """
    neighbours = []
    for neighbour_y in range(-1, 2):
        for neighbour_x in range(-1, 2):
            if ((neighbour_x != 0 and neighbour_y != 0) and
                    0 <= x+neighbour_x < properties["width"] and 0 <= y+neighbour_y < properties["height"]):
                if (x + neighbour_x, y + neighbour_y) in cells:
                    neighbours.append(cells[(x+neighbour_x, y+neighbour_y)])
                else:
                    neighbours.append(("DEAD", (x+neighbour_x, y+neighbour_y)))
    return neighbours

def update(cells):
    """Updates the state of all of the cells.
    Returns:
        - a new set of cells"""
    new_cells = dict()
    dead_cells = []

    # Kill alive cells.
    for cell in cells.values():
        #if not cell.update():
        if True:
            neighbours = get_neighbours(cells, *cell.position)
            
            # Count number of enemy cells.
            enemies = 0
            for neighbour in neighbours:
                # Add dead cells to the list of dead cells.
                if isinstance(neighbour, tuple):
                    dead_cells.append(neighbour[1])
                # Check if cell is an enemy.
                elif neighbour.team != cell.team:
                    enemies += 1

            # Add new cell if it is to not be killed.    
            if enemies < properties["to-kill"]:
                new_cells[cell.position] = cell

    # Revive dead cells.
    for dead in dead_cells:
        neighbours = get_neighbours(cells, *dead)
        total_neighbours = 0
        team_control = dict()
        # Handle neighbours.
        for neighbour in neighbours:
            if not isinstance(neighbour, tuple):
                total_neighbours += 1
                # Add team.
                if neighbour.team not in team_control:
                    team_control[neighbour.team] = 1
                else:
                    team_control[neighbour.team] += 1
        # Revive the cell.
        if total_neighbours >= 0:
            max_control = max(team_control.values())
            if total_neighbours - max_control < total_neighbours / 2:
                # get team.
                for team, value in team_control.items():
                    if value == max_control:
                        break
                new_cells[dead] = Cell(dead[0], dead[1], team, properties["death-age"])
            else:
                # FIXME change to while loop subtracting from total_neighbours
                #       break when remainder < max_control.
                # get all teams with the highest control.
                controlling_teams = []
                for team, value in team_control.items():
                    if value == max_control:
                        controlling_teams.append(team)

                controlling_teams = sorted(controlling_teams, key = lambda x:x.score, reverse=True)
                # Check if top two teams have the same score.
                # Only revive if not the same.
                if controlling_teams[0].score != controlling_teams[1].score:
                    new_cells[dead] = Cell(dead[0], dead[1], controlling_teams[0], properties["death-age"])
                    
    return new_cells

def output(grid, stream):
    """Displays the grid.
    Parameters:
        - grid      the grid to output
        - stream    where to output the grid
    """
    #print("\n" * 50, file=stream) # Clearing the screen.
    output = ""
    for row in grid:
        output += "".join(row) + "\n"
    output.rstrip("\n")
    print(output, file=stream)
    

def loop():
    """The main loop of the game of life war.

    Runs a constant loop (updating x times per second based on refresh property)
    The loop ends when a winner is determined.
    """
    global cells
    global properties
    
    round_number = 0
    last = 0
    delta = 1 / properties["refresh"]
    
    while round_number < properties["win-round"]:
        current = time.time()
        if current - last > delta:
            round_number += 1
            cells = update(cells)
            grid = update_grid(generate_grid(properties), cells)
            output(grid, stdout)
            last = current


# -- On import -----------------------------------------------------------------
# Add validation for certain properties.
bounds["width"] = (between, (10, 100,))
bounds["height"] = (between, (10, 50,))
bounds["refresh"] = (between, (1, 60,))
bounds["death-age"] = (between, (1, 32,))
bounds["win-round"] = (between, (128, 65536,))
bounds["to-kill"] = (between, (1, 8,))

load_defaults()
cells = dict()
teams = dict()
grid = generate_grid(properties)