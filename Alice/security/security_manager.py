"""Security management for Alice system."""
import hashlib
import hmac
import logging
import json
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum, auto

from events.event_system import EventManager, EventPriority

class SecurityLevel(Enum):
    """Security clearance levels."""
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()

@dataclass
class SecurityContext:
    """Security context for operations."""
    level: SecurityLevel
    source: str
    timestamp: datetime
    metadata: Dict[str, Any]

class SecurityViolation(Exception):
    """Raised when a security violation is detected."""
    pass

class SecurityManager:
    """Manages system security and access control."""
    
    def __init__(self, event_manager: EventManager):
        self.event_manager = event_manager
        self.logger = logging.getLogger(__name__)
        self._operation_rules: Dict[str, SecurityLevel] = {}
        self._blocked_sources: Set[str] = set()
        self._violation_counts: Dict[str, int] = {}
        
    def configure_operation(self, operation: str, level: SecurityLevel):
        """Configure security level for an operation."""
        self._operation_rules[operation] = level
        self.logger.info(f"Configured security level {level.name} for operation: {operation}")
        
    def block_source(self, source: str):
        """Block a source from performing operations."""
        self._blocked_sources.add(source)
        self.logger.warning(f"Blocked source: {source}")
        
    def unblock_source(self, source: str):
        """Unblock a previously blocked source."""
        self._blocked_sources.discard(source)
        self.logger.info(f"Unblocked source: {source}")
        
    async def validate_operation(
        self,
        operation: str,
        context: SecurityContext
    ) -> bool:
        """Validate if an operation is allowed."""
        try:
            # Check if source is blocked
            if context.source in self._blocked_sources:
                raise SecurityViolation(f"Source is blocked: {context.source}")
                
            # Check operation security level
            required_level = self._operation_rules.get(
                operation,
                SecurityLevel.MEDIUM  # Default level
            )
            
            if context.level.value < required_level.value:
                raise SecurityViolation(
                    f"Insufficient security level for operation {operation}"
                )
                
            # Validate operation specific rules
            await self._validate_operation_rules(operation, context)
            
            # Log successful validation
            self.audit_log(
                operation,
                context,
                "Operation validated successfully"
            )
            
            return True
            
        except SecurityViolation as e:
            # Handle security violation
            await self._handle_violation(operation, context, str(e))
            raise
            
        except Exception as e:
            self.logger.error(f"Error validating operation: {str(e)}")
            raise
            
    def audit_log(
        self,
        operation: str,
        context: SecurityContext,
        message: str
    ):
        """Log security-relevant operations."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'source': context.source,
            'security_level': context.level.name,
            'message': message,
            'metadata': context.metadata
        }
        
        # Log to file
        self.logger.info(f"Security audit: {json.dumps(log_entry)}")
        
        # Calculate entry hash for integrity
        entry_hash = self._calculate_hash(json.dumps(log_entry))
        self.logger.debug(f"Audit log entry hash: {entry_hash}")
        
    async def _validate_operation_rules(
        self,
        operation: str,
        context: SecurityContext
    ):
        """Validate operation-specific security rules."""
        # Add custom validation rules here
        if operation.startswith('system.'):
            await self._validate_system_operation(operation, context)
        elif operation.startswith('data.'):
            await self._validate_data_operation(operation, context)
            
    async def _validate_system_operation(
        self,
        operation: str,
        context: SecurityContext
    ):
        """Validate system-level operations."""
        if operation == 'system.shutdown':
            if context.level != SecurityLevel.CRITICAL:
                raise SecurityViolation("System shutdown requires CRITICAL security level")
                
    async def _validate_data_operation(
        self,
        operation: str,
        context: SecurityContext
    ):
        """Validate data operations."""
        if operation.startswith('data.delete'):
            if context.level.value < SecurityLevel.HIGH.value:
                raise SecurityViolation("Data deletion requires HIGH security level")
                
    async def _handle_violation(
        self,
        operation: str,
        context: SecurityContext,
        message: str
    ):
        """Handle security violations."""
        # Update violation count
        self._violation_counts[context.source] = (
            self._violation_counts.get(context.source, 0) + 1
        )
        
        # Check for repeated violations
        if self._violation_counts[context.source] >= 3:
            self.block_source(context.source)
            
        # Emit security alert
        await self.event_manager.emit(
            'security.violation',
            {
                'operation': operation,
                'source': context.source,
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'violation_count': self._violation_counts[context.source]
            },
            priority=EventPriority.HIGH
        )
        
        # Log violation
        self.audit_log(
            operation,
            context,
            f"Security violation: {message}"
        )
        
    def _calculate_hash(self, data: str) -> str:
        """Calculate hash for data integrity."""
        return hashlib.sha256(data.encode()).hexdigest()
