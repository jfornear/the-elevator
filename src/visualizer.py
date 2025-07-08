from typing import List, Dict
import os
import platform
from time import strftime


class ElevatorVisualizer:
    def __init__(self, num_floors: int):
        self.num_floors = num_floors
        self.floor_width = 80  # Width for multiple elevators
        self.is_windows = platform.system() == "Windows"
        self.shaft_width = 6
        self.previous_status = None

    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if self.is_windows else 'clear')

    def draw_system(self, status: Dict) -> None:
        """Draw the elevator system state with ASCII visualization."""
        self.clear_screen()
        
        # Create the building visualization
        building: List[str] = []
        
        # Header with current time
        current_time = strftime("%H:%M:%S")
        building.append("=" * self.floor_width)
        title = f"Elevator System - {current_time}"
        padding = (self.floor_width - len(title)) // 2
        building.append(" " * padding + title)
        building.append("=" * self.floor_width)

        # Elevator status panel
        building.append("Elevator Status:")
        for elevator in status['elevators']:
            status_line = (
                f"#{elevator['id']}: Floor {elevator['current_floor']}, "
                f"Direction: {elevator['direction']}, State: {elevator['state']}, "
                f"Weight: {elevator['current_weight']}lbs, Targets: {elevator['target_floors']}"
            )
            building.append(status_line)
        
        building.append("-" * self.floor_width)

        # Draw each floor (from top to bottom)
        for floor in range(self.num_floors, 0, -1):
            floor_str = self._create_floor_visualization(floor, status['elevators'])
            building.append(floor_str)

        # Ground
        building.append("=" * self.floor_width)
        
        # Add legend
        building.append("Legend:")
        building.append("[ || ] - Open doors   [||||] - Closed doors   * - Target floor   [!!!!] - Emergency")
        building.append("↑/↓ - Moving up/down   E# - Elevator number")
        
        # Print the building
        print("\n".join(building))
        
        # Store current status for change detection
        self.previous_status = status.copy()

    def _create_floor_visualization(self, floor: int, elevators: List[Dict]) -> str:
        """Create the visualization for a single floor with multiple elevators."""
        # Floor number
        floor_num = f"{floor:2d} |"
        
        # Create elevator representations for this floor
        elevator_displays = []
        for elevator in elevators:
            if elevator['current_floor'] == floor:
                # Elevator is on this floor
                if elevator['state'] == 'door_open':
                    display = f"[E{elevator['id']} ||]"
                elif elevator['state'] == 'door_opening':
                    display = f"[E{elevator['id']} |>]"
                elif elevator['state'] == 'door_closing':
                    display = f"[E{elevator['id']}<| ]"
                elif elevator['state'] == 'emergency':
                    display = f"[E{elevator['id']}!!!!]"
                elif elevator['state'] == 'moving':
                    display = f"[E{elevator['id']}||||]"
                else:  # idle
                    display = f"[E{elevator['id']}||||]"
            else:
                # Show shaft or target indicator
                if floor in elevator['target_floors']:
                    display = "   *   "
                else:
                    display = "       "
            elevator_displays.append(display)
        
        # Combine all elevator displays with proper spacing
        elevator_section = " ".join(elevator_displays)
        
        # Add direction indicators
        indicators = []
        elevators_here = [e for e in elevators if e['current_floor'] == floor]
        for elevator in elevators_here:
            if elevator['direction'] == 'up':
                indicators.append("↑")
            elif elevator['direction'] == 'down':
                indicators.append("↓")
        
        # Create the complete floor string with proper spacing
        left_space = " " * 2
        right_space = " " * (self.floor_width - len(floor_num) - len(left_space) - 
                           len(elevator_section) - len("".join(indicators)) - 2)
        
        floor_str = f"{floor_num}{left_space}{elevator_section}{right_space}{''.join(indicators)}"
        
        return floor_str 