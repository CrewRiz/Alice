import os
import sys
import time
import json
import asyncio
import logging
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum, auto
import numpy as np

import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException

from TimePerception import QuantumTime
from PersonalityGene import PersonalitySystem
from AdvancedInteractions import AdvancedInteractionSystem, InteractionMode, InteractionParameters
from AutomationSystem import AutomationSystem, AutomationType, AutomationTask

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('computer_interaction.log'),
        logging.StreamHandler()
    ]
)

class InteractionType(Enum):
    MOUSE = auto()
    KEYBOARD = auto()
    SYSTEM = auto()
    WEB = auto()
    FILE = auto()

@dataclass
class InteractionMetrics:
    total_actions: int = 0
    successful_actions: int = 0
    failed_actions: int = 0
    last_action_time: datetime = datetime.fromisoformat("2024-12-23T03:39:17-06:00")
    action_durations: List[float] = None
    
    def __post_init__(self):
        if self.action_durations is None:
            self.action_durations = []

@dataclass
class SafetyConfig:
    max_actions_per_minute: Dict[InteractionType, int] = None
    unsafe_commands: List[str] = None
    unsafe_domains: List[str] = None
    unsafe_paths: List[str] = None
    unsafe_content: List[str] = None
    
    def __post_init__(self):
        if self.max_actions_per_minute is None:
            self.max_actions_per_minute = {
                InteractionType.MOUSE: 60,
                InteractionType.KEYBOARD: 120,
                InteractionType.SYSTEM: 10,
                InteractionType.WEB: 30,
                InteractionType.FILE: 20
            }
        if self.unsafe_commands is None:
            self.unsafe_commands = [
                'rm -rf', 'format', 'del', 'shutdown', 'reboot',
                'mkfs', 'dd', 'chmod -R', 'chown -R'
            ]
        if self.unsafe_domains is None:
            self.unsafe_domains = [
                'malware', 'phishing', 'hack', 'crack',
                'warez', 'torrent', 'proxy'
            ]
        if self.unsafe_paths is None:
            self.unsafe_paths = [
                '/system', 'C:\\Windows', '/boot', '/etc',
                'C:\\Program Files', 'C:\\Program Files (x86)'
            ]
        if self.unsafe_content is None:
            self.unsafe_content = [
                'password', 'credit card', 'social security',
                'private key', 'secret key', 'api key'
            ]

class ComputerInteractionSystem:
    def __init__(self):
        self.reference_time = datetime.fromisoformat("2024-12-23T03:42:39-06:00")
        self.quantum_time = QuantumTime()
        self.personality = PersonalitySystem()
        
        # Initialize configurations
        self.safety_config = SafetyConfig()
        self.metrics = {
            interaction_type: InteractionMetrics()
            for interaction_type in InteractionType
        }
        
        # Initialize advanced interaction system
        self.advanced_interactions = AdvancedInteractionSystem(
            self.quantum_time,
            self.personality
        )
        
        # Initialize automation system
        self.automation_system = AutomationSystem(
            self.quantum_time,
            self.personality,
            self.advanced_interactions
        )
        
        # Configure PyAutoGUI
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
        
        # Initialize webdriver
        self.driver: Optional[webdriver.Chrome] = None
        self.driver_wait_time = 10
        
        # Action history with quantum timestamps
        self.action_history: List[Dict[str, Any]] = []
        
        logging.info("ComputerInteractionSystem initialized with advanced automation")

    async def execute_action(self, action: Dict[str, Any]) -> bool:
        """Execute an action with quantum-aware timing and safety checks."""
        try:
            # Check if this is an automation task
            if 'automation' in action:
                task = AutomationTask(
                    type=AutomationType[action['automation'].upper()],
                    parameters=action.get('parameters', {}),
                    conditions=action.get('conditions', {}),
                    callbacks=action.get('callbacks', {}),
                    timeout=action.get('timeout', 60.0),
                    retry_count=action.get('retry_count', 3),
                    quantum_sensitive=action.get('quantum_sensitive', True)
                )
                return await self.automation_system.execute_task(task)
            
            # Check if this is an advanced interaction sequence
            if 'sequence' in action:
                return await self.advanced_interactions.execute_complex_interaction(
                    action['sequence']
                )
            
            action_type = InteractionType[action.get('type', 'SYSTEM').upper()]
            
            # Check rate limits with quantum time
            if not self._check_rate_limit(action_type):
                logging.warning(f"Rate limit exceeded for {action_type}")
                return False
            
            # Get quantum phase for timing
            quantum_phase = self.quantum_time.get_current_phase()
            
            # Execute action based on type
            start_time = self.reference_time
            success = False
            
            if action_type == InteractionType.MOUSE:
                if action.get('advanced', False):
                    success = await self.advanced_interactions._execute_mouse_gesture(action)
                else:
                    success = await self._handle_mouse_action(action, quantum_phase)
            elif action_type == InteractionType.KEYBOARD:
                if action.get('advanced', False):
                    success = await self.advanced_interactions._execute_keyboard_sequence(action)
                else:
                    success = await self._handle_keyboard_action(action, quantum_phase)
            elif action_type == InteractionType.SYSTEM:
                if action.get('advanced', False):
                    success = await self.advanced_interactions._execute_system_sequence(action)
                else:
                    success = await self._handle_system_action(action, quantum_phase)
            elif action_type == InteractionType.WEB:
                if action.get('advanced', False):
                    success = await self.advanced_interactions._execute_web_interaction(action)
                else:
                    success = await self._handle_web_action(action, quantum_phase)
            elif action_type == InteractionType.FILE:
                success = await self._handle_file_action(action, quantum_phase)
            
            # Update metrics
            self._update_metrics(action_type, success, start_time)
            
            return success
            
        except Exception as e:
            logging.error(f"Action execution failed: {str(e)}", exc_info=True)
            return False

    def _check_rate_limit(self, action_type: InteractionType) -> bool:
        """Check if action is within rate limits using quantum time."""
        metrics = self.metrics[action_type]
        time_delta = (self.reference_time - metrics.last_action_time).total_seconds()
        
        # Apply quantum phase to rate limit
        quantum_phase = self.quantum_time.get_current_phase()
        rate_modifier = 0.8 + 0.4 * abs(np.cos(quantum_phase))  # Range: [0.8, 1.2]
        
        actions_per_minute = metrics.total_actions / (time_delta / 60)
        max_actions = self.safety_config.max_actions_per_minute[action_type] * rate_modifier
        
        return actions_per_minute <= max_actions

    async def _handle_mouse_action(self, action: Dict[str, Any], quantum_phase: float) -> bool:
        """Handle mouse actions with quantum-aware timing."""
        try:
            x = action.get('x', 0)
            y = action.get('y', 0)
            
            # Apply quantum phase to movement duration
            base_duration = 0.5
            duration = base_duration * (1 + 0.2 * np.cos(quantum_phase))
            
            # Get screen boundaries
            screen_width, screen_height = pyautogui.size()
            
            # Validate coordinates
            if not (0 <= x <= screen_width and 0 <= y <= screen_height):
                logging.warning(f"Invalid mouse coordinates: ({x}, {y})")
                return False
            
            # Execute movement
            pyautogui.moveTo(x, y, duration=duration)
            
            # Handle click if specified
            if action.get('click', False):
                await asyncio.sleep(0.1)  # Small delay before click
                pyautogui.click()
            
            return True
            
        except Exception as e:
            logging.error(f"Mouse action failed: {str(e)}")
            return False

    async def _handle_keyboard_action(self, action: Dict[str, Any], quantum_phase: float) -> bool:
        """Handle keyboard actions with quantum-aware timing."""
        try:
            text = action.get('text', '')
            
            # Check for unsafe content
            if not self._is_safe_content(text):
                logging.warning(f"Unsafe content detected in keyboard action")
                return False
            
            # Apply quantum phase to typing interval
            base_interval = 0.1
            interval = base_interval * (1 + 0.2 * np.cos(quantum_phase))
            
            # Execute typing
            pyautogui.typewrite(text, interval=interval)
            
            return True
            
        except Exception as e:
            logging.error(f"Keyboard action failed: {str(e)}")
            return False

    async def _handle_system_action(self, action: Dict[str, Any], quantum_phase: float) -> bool:
        """Handle system actions with quantum-aware timing."""
        try:
            command = action.get('command', '')
            
            # Check command safety
            if not self._is_safe_command(command):
                logging.warning(f"Unsafe command detected: {command}")
                return False
            
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            success = result.returncode == 0
            if not success:
                logging.error(f"Command failed: {result.stderr}")
            
            return success
            
        except subprocess.TimeoutExpired:
            logging.error("Command execution timed out")
            return False
        except Exception as e:
            logging.error(f"System action failed: {str(e)}")
            return False

    async def _handle_web_action(self, action: Dict[str, Any], quantum_phase: float) -> bool:
        """Handle web actions with quantum-aware timing."""
        try:
            url = action.get('url', '')
            
            # Check URL safety
            if not self._is_safe_url(url):
                logging.warning(f"Unsafe URL detected: {url}")
                return False
            
            # Initialize webdriver if needed
            if not self.driver:
                self.driver = webdriver.Chrome()
            
            # Apply quantum phase to wait time
            wait_time = self.driver_wait_time * (1 + 0.2 * np.cos(quantum_phase))
            
            # Execute web action
            self.driver.get(url)
            WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            return True
            
        except TimeoutException:
            logging.error("Web action timed out")
            return False
        except Exception as e:
            logging.error(f"Web action failed: {str(e)}")
            return False

    async def _handle_file_action(self, action: Dict[str, Any], quantum_phase: float) -> bool:
        """Handle file actions with quantum-aware timing."""
        try:
            path = action.get('path', '')
            operation = action.get('operation', '')
            
            # Check path safety
            if not self._is_safe_path(path):
                logging.warning(f"Unsafe path detected: {path}")
                return False
            
            # Execute file operation
            if operation == 'read':
                with open(path, 'r') as f:
                    _ = f.read()
            elif operation == 'write':
                content = action.get('content', '')
                if not self._is_safe_content(content):
                    logging.warning("Unsafe content detected in file operation")
                    return False
                with open(path, 'w') as f:
                    f.write(content)
            else:
                logging.warning(f"Unknown file operation: {operation}")
                return False
            
            return True
            
        except Exception as e:
            logging.error(f"File action failed: {str(e)}")
            return False

    def _update_metrics(self, action_type: InteractionType, success: bool, start_time: datetime) -> None:
        """Update interaction metrics with quantum time."""
        metrics = self.metrics[action_type]
        metrics.total_actions += 1
        if success:
            metrics.successful_actions += 1
        else:
            metrics.failed_actions += 1
            
        # Calculate action duration
        duration = (self.reference_time - start_time).total_seconds()
        metrics.action_durations.append(duration)
        
        # Keep only recent durations
        if len(metrics.action_durations) > 1000:
            metrics.action_durations = metrics.action_durations[-1000:]
            
        metrics.last_action_time = self.reference_time

    def _is_safe_command(self, command: str) -> bool:
        """Check if a command is safe to execute."""
        return not any(unsafe in command.lower() for unsafe in self.safety_config.unsafe_commands)

    def _is_safe_url(self, url: str) -> bool:
        """Check if a URL is safe to visit."""
        return not any(unsafe in url.lower() for unsafe in self.safety_config.unsafe_domains)

    def _is_safe_path(self, path: str) -> bool:
        """Check if a file path is safe to access."""
        return not any(unsafe in path for unsafe in self.safety_config.unsafe_paths)

    def _is_safe_content(self, content: str) -> bool:
        """Check if content is safe to handle."""
        return not any(unsafe in content.lower() for unsafe in self.safety_config.unsafe_content)

    async def cleanup(self) -> None:
        """Clean up resources with quantum-aware timing."""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
            
            # Save interaction history
            history_path = 'interaction_history.json'
            with open(history_path, 'w') as f:
                json.dump(self.action_history, f, indent=2, default=str)
            
            logging.info("ComputerInteractionSystem cleaned up successfully")
            
        except Exception as e:
            logging.error(f"Cleanup failed: {str(e)}")

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of interaction metrics."""
        return {
            interaction_type.name: {
                'total_actions': metrics.total_actions,
                'successful_actions': metrics.successful_actions,
                'failed_actions': metrics.failed_actions,
                'average_duration': np.mean(metrics.action_durations) if metrics.action_durations else 0,
                'last_action_time': metrics.last_action_time.isoformat()
            }
            for interaction_type, metrics in self.metrics.items()
        }
