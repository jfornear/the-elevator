import logging
import os
from datetime import datetime
from typing import Dict, Any

class ElevatorLogger:
    def __init__(self):
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        # Set up file handler
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = f'logs/elevator_system_{timestamp}.log'
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()  # Also print to console
            ]
        )
        self.logger = logging.getLogger('ElevatorSystem')
        self.logger.info("=== Starting New Elevator System Session ===")
        
    def log_system_init(self, num_floors: int, num_elevators: int) -> None:
        """Log system initialization"""
        self.logger.info(f"Initializing system with {num_floors} floors and {num_elevators} elevators")
        
    def log_elevator_init(self, elevator_id: int, zone: str, floor_range: tuple) -> None:
        """Log elevator initialization"""
        self.logger.info(f"Initialized E{elevator_id} - Zone: {zone}, Floors: {floor_range}")
        
    def log_request_assignment(self, request_type: str, floor: int, direction: str, 
                             elevator_id: int, current_floor: int, targets: list) -> None:
        """Log request assignment"""
        self.logger.info(
            f"REQUEST: {request_type} request F{floor} {direction} assigned to E{elevator_id}\n"
            f"         Current floor: {current_floor}, Targets: {targets}"
        )
        
    def log_request_rejected(self, request_type: str, floor: int, reason: str) -> None:
        """Log rejected request"""
        self.logger.warning(
            f"REJECTED: {request_type} request F{floor} - {reason}"
        )
        
    def log_movement(self, elevator_id: int, from_floor: int, to_floor: int, 
                    direction: str, targets: list) -> None:
        """Log elevator movement"""
        self.logger.info(
            f"MOVE: E{elevator_id} {direction} F{from_floor}→F{to_floor}\n"
            f"      Targets: {targets}"
        )
        
    def log_stop(self, elevator_id: int, floor: int, direction: str, 
                 reason: str, targets: list) -> None:
        """Log elevator stop"""
        self.logger.info(
            f"STOP: E{elevator_id} at F{floor} ({direction})\n"
            f"      Reason: {reason}\n"
            f"      Targets: {targets}"
        )
        
    def log_door_operation(self, elevator_id: int, floor: int, 
                          operation: str, targets: list) -> None:
        """Log door operations"""
        self.logger.info(
            f"DOORS: E{elevator_id} F{floor} - {operation}\n"
            f"       Targets: {targets}"
        )
        
    def log_direction_change(self, elevator_id: int, floor: int, 
                           old_dir: str, new_dir: str, targets: list) -> None:
        """Log direction changes"""
        self.logger.info(
            f"DIRECTION: E{elevator_id} at F{floor} changed {old_dir}→{new_dir}\n"
            f"          Targets: {targets}"
        )
        
    def log_request_completed(self, elevator_id: int, floor: int, 
                            direction: str, remaining_targets: list) -> None:
        """Log completed requests"""
        self.logger.info(
            f"COMPLETED: E{elevator_id} F{floor} {direction} request\n"
            f"          Remaining targets: {remaining_targets}"
        )
        
    def log_state_change(self, elevator_id: int, floor: int,
                        old_state: str, new_state: str, direction: str) -> None:
        """Log state changes"""
        self.logger.info(
            f"STATE: E{elevator_id} at F{floor} changed {old_state}→{new_state}\n"
            f"       Direction: {direction}"
        )
        
    def log_error(self, elevator_id: int, error_type: str, details: str) -> None:
        """Log errors"""
        self.logger.error(
            f"ERROR: E{elevator_id} - {error_type}\n"
            f"       Details: {details}"
        )
        
    def log_system_status(self, status: Dict[str, Any]) -> None:
        """Log full system status"""
        self.logger.info("=== System Status ===")
        for elevator in status['elevators']:
            self.logger.info(
                f"E{elevator['id']} - Floor: {elevator['current_floor']}, "
                f"State: {elevator['state']}, Direction: {elevator['direction']}, "
                f"Targets: {elevator['target_floors']}, "
                f"Weight: {elevator['current_weight']}lbs"
            )
        self.logger.info("===================") 