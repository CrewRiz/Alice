import pyautogui
import subprocess
import os
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
import pyautogui
import subprocess
import time
import logging
import os
import asyncio
from datetime import datetime, timedelta

class ComputerInteractionSystem:
    def __init__(self, config=None):
        # Initialize safety settings
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 1.0

        # Set up logging
        logging.basicConfig(filename='system_actions.log', level=logging.INFO)
        
        # Configuration for safety and rate-limiting settings
        self.config = config or {
            'action_limits': {
                'file_operations_per_minute': 10,
                'mouse_moves_per_minute': 60,
                'web_requests_per_minute': 30
            },
            'unsafe_commands': ['rm -rf', 'format', 'del', 'shutdown'],
            'unsafe_domains': ['malware', 'phishing'],
            'unsafe_paths': ['/system', 'C:\\Windows'],
            'unsafe_content': ['password', 'credit card']
        }
        
        # Track actions
        self.action_history = []
        self.driver = None
        
    def log_action(self, message, level="INFO"):
        """Log system actions with additional context"""
        timestamp = time.time()
        log_message = f"{datetime.fromtimestamp(timestamp)} - {message}"
        self.action_history.append({'timestamp': timestamp, 'action': message, 'level': level})
        
        if level == "INFO":
            logging.info(log_message)
        elif level == "ERROR":
            logging.error(log_message)

    def rate_limit(self, action_type):
        """Enforce rate limits on actions to prevent abuse"""
        action_limit = self.config['action_limits'].get(action_type, 10)
        one_minute_ago = time.time() - 60
        recent_actions = [a for a in self.action_history if a['timestamp'] > one_minute_ago and action_type in a['action']]
        return len(recent_actions) < action_limit

    def safe_mouse_move(self, x, y):
        """Move mouse with safety checks and rate limiting"""
        try:
            if not self.rate_limit("mouse_moves"):
                raise ValueError("Mouse move rate limit exceeded")
                
            screen_width, screen_height = pyautogui.size()
            if 0 <= x <= screen_width and 0 <= y <= screen_height:
                pyautogui.moveTo(x, y, duration=0.5)
                self.log_action(f"Mouse moved to {x}, {y}")
            else:
                raise ValueError("Coordinates out of screen bounds")
                
        except Exception as e:
            self.log_action(f"Mouse move failed: {str(e)}", level="ERROR")

    def click_element(self, image_path=None, coordinates=None):
        """Click element with image recognition or coordinates with error handling"""
        try:
            if not self.rate_limit("mouse_moves"):
                raise ValueError("Click rate limit exceeded")
                
            if image_path:
                location = pyautogui.locateOnScreen(image_path)
                if location:
                    pyautogui.click(location)
                    self.log_action(f"Clicked element at {location}")
                else:
                    raise ValueError(f"Element not found: {image_path}")
            elif coordinates:
                self.safe_mouse_move(*coordinates)
                pyautogui.click()
                
        except Exception as e:
            self.log_action(f"Click failed: {str(e)}", level="ERROR")

    def type_text(self, text, interval=0.1):
        """Type text with rate limiting"""
        try:
            if not self.rate_limit("keyboard_inputs"):
                raise ValueError("Typing rate limit exceeded")
                
            pyautogui.typewrite(text, interval=interval)
            self.log_action(f"Typed text: {text[:20]}...")
        except Exception as e:
            self.log_action(f"Type failed: {str(e)}", level="ERROR")

    def execute_command(self, command):
        """Execute command line command with safety validation and rate limiting"""
        try:
            if not self.rate_limit("commands"):
                raise ValueError("Command execution rate limit exceeded")

            if self.is_safe_command(command):
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                self.log_action(f"Executed command: {command}")
                return result.stdout
            else:
                raise ValueError(f"Unsafe command: {command}")
                
        except Exception as e:
            self.log_action(f"Command execution failed: {str(e)}", level="ERROR")

    def browse_web(self, url):
        """Browse web with safety checks and rate limiting"""
        try:
            if not self.rate_limit("web_requests"):
                raise ValueError("Web request rate limit exceeded")

            if self.is_safe_url(url):
                if not self.driver:
                    self.driver = webdriver.Chrome()
                self.driver.get(url)
                self.log_action(f"Browsed to: {url}")
            else:
                raise ValueError(f"Unsafe URL: {url}")
                
        except (TimeoutException, ValueError, Exception) as e:
            self.log_action(f"Web browsing failed: {str(e)}", level="ERROR")

    def file_operation(self, operation, path, content=None):
        """Handle file operations with safety validation and rate limiting"""
        try:
            if not self.rate_limit("file_operations"):
                raise ValueError("File operation rate limit exceeded")

            if self.is_safe_path(path):
                if operation == "create":
                    with open(path, 'w') as f:
                        if content:
                            f.write(content)
                elif operation == "read":
                    with open(path, 'r') as f:
                        return f.read()
                elif operation == "delete":
                    os.remove(path)
                self.log_action(f"File operation {operation}: {path}")
            else:
                raise ValueError(f"Unsafe path: {path}")
                
        except (FileNotFoundError, ValueError, Exception) as e:
            self.log_action(f"File operation failed: {str(e)}", level="ERROR")

    def is_safe_command(self, command):
        """Check if command is safe to execute"""
        return not any(cmd in command.lower() for cmd in self.config['unsafe_commands'])

    def is_safe_url(self, url):
        """Check if URL is safe to visit with simple checks"""
        return not any(domain in url.lower() for domain in self.config['unsafe_domains'])

    def is_safe_path(self, path):
        """Check if file path is safe"""
        return not any(p in path for p in self.config['unsafe_paths'])

    def cleanup(self):
        """Clean up resources using context management for safety"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def __del__(self):
        self.cleanup()

