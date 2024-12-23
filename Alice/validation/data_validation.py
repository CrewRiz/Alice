"""Data validation system for Alice."""
from typing import Dict, Any, List, Optional, Type, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
import logging

# Base Models
class TaskType(str, Enum):
    """Types of tasks that can be processed."""
    AUTOMATION = "automation"
    INTERACTION = "interaction"
    LEARNING = "learning"
    SYSTEM = "system"
    GENERIC = "generic"

class TaskPriority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class BaseTask(BaseModel):
    """Base model for all tasks."""
    id: str
    type: TaskType
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('updated_at')
    def updated_at_must_be_after_created(cls, v, values):
        """Validate that updated_at is after created_at."""
        if 'created_at' in values and v < values['created_at']:
            raise ValueError("updated_at must be after created_at")
        return v

class AutomationTask(BaseTask):
    """Model for automation tasks."""
    type: TaskType = TaskType.AUTOMATION
    target_system: str
    actions: List[Dict[str, Any]]
    timeout_seconds: Optional[int] = 300
    
    @validator('actions')
    def validate_actions(cls, v):
        """Validate automation actions."""
        if not v:
            raise ValueError("actions list cannot be empty")
        return v

class InteractionTask(BaseTask):
    """Model for interaction tasks."""
    type: TaskType = TaskType.INTERACTION
    interaction_type: str
    parameters: Dict[str, Any]
    require_confirmation: bool = False

class LearningTask(BaseTask):
    """Model for learning tasks."""
    type: TaskType = TaskType.LEARNING
    learning_type: str
    training_data: Optional[Dict[str, Any]]
    validation_data: Optional[Dict[str, Any]]

class SystemTask(BaseTask):
    """Model for system tasks."""
    type: TaskType = TaskType.SYSTEM
    command: str
    args: List[str] = Field(default_factory=list)
    environment: Dict[str, str] = Field(default_factory=dict)

# Validation Manager
class ValidationManager:
    """Manages data validation across the system."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._task_models = {
            TaskType.AUTOMATION: AutomationTask,
            TaskType.INTERACTION: InteractionTask,
            TaskType.LEARNING: LearningTask,
            TaskType.SYSTEM: SystemTask
        }
        
    def validate_task(self, task_data: Dict[str, Any]) -> BaseTask:
        """Validate task data and return appropriate model."""
        try:
            # Determine task type
            task_type = task_data.get('type', TaskType.GENERIC)
            
            # Get appropriate model
            model_class = self._task_models.get(task_type, BaseTask)
            
            # Validate and return model instance
            return model_class(**task_data)
            
        except Exception as e:
            self.logger.error(f"Task validation failed: {str(e)}")
            raise ValueError(f"Invalid task data: {str(e)}")
            
    def validate_automation_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Validate automation action data."""
        required_fields = {'type', 'parameters'}
        if not all(field in action for field in required_fields):
            raise ValueError(f"Missing required fields: {required_fields - action.keys()}")
        return action
        
    def validate_interaction_parameters(
        self,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate interaction parameters."""
        # Add specific validation rules here
        return parameters
        
    def validate_learning_data(
        self,
        training_data: Optional[Dict[str, Any]],
        validation_data: Optional[Dict[str, Any]]
    ) -> tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """Validate learning data."""
        # Add specific validation rules here
        return training_data, validation_data
        
    def validate_system_command(
        self,
        command: str,
        args: List[str],
        environment: Dict[str, str]
    ) -> tuple[str, List[str], Dict[str, str]]:
        """Validate system command and arguments."""
        if not command:
            raise ValueError("Command cannot be empty")
            
        # Add security checks here
        
        return command, args, environment

# Response Models
class TaskResponse(BaseModel):
    """Model for task execution response."""
    task_id: str
    success: bool
    result: Optional[Dict[str, Any]]
    error: Optional[str]
    execution_time: float
    timestamp: datetime = Field(default_factory=datetime.now)

class ValidationResponse(BaseModel):
    """Model for validation response."""
    valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)
