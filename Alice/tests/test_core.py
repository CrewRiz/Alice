"""Core test suite for Alice system."""
import pytest
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any

from events.event_system import EventManager, Event, EventPriority
from security.security_manager import SecurityManager, SecurityContext, SecurityLevel
from monitoring.system_monitor import SystemMonitor
from validation.data_validation import ValidationManager, TaskType

# Fixtures
@pytest.fixture
async def event_manager():
    """Create and initialize event manager."""
    manager = EventManager()
    await manager.initialize()
    yield manager
    await manager.cleanup()

@pytest.fixture
def security_manager(event_manager):
    """Create security manager."""
    return SecurityManager(event_manager)

@pytest.fixture
def system_monitor(event_manager):
    """Create system monitor."""
    return SystemMonitor(event_manager)

@pytest.fixture
def validation_manager():
    """Create validation manager."""
    return ValidationManager()

# Event System Tests
class TestEventSystem:
    """Test event system functionality."""
    
    @pytest.mark.asyncio
    async def test_event_publishing(self, event_manager):
        """Test basic event publishing."""
        received_events = []
        
        async def event_handler(event: Event):
            received_events.append(event)
            
        # Subscribe to test events
        event_manager.event_bus.subscribe('test.event', event_handler)
        
        # Publish test event
        await event_manager.emit(
            'test.event',
            {'test': 'data'},
            EventPriority.MEDIUM
        )
        
        # Wait for event processing
        await asyncio.sleep(0.1)
        
        assert len(received_events) == 1
        assert received_events[0].type == 'test.event'
        assert received_events[0].data == {'test': 'data'}
        
    @pytest.mark.asyncio
    async def test_event_priority(self, event_manager):
        """Test event priority handling."""
        received_events = []
        
        async def event_handler(event: Event):
            received_events.append(event)
            
        # Subscribe to test events
        event_manager.event_bus.subscribe('test.priority', event_handler)
        
        # Publish events with different priorities
        await event_manager.emit(
            'test.priority',
            {'priority': 'low'},
            EventPriority.LOW
        )
        await event_manager.emit(
            'test.priority',
            {'priority': 'high'},
            EventPriority.HIGH
        )
        
        # Wait for event processing
        await asyncio.sleep(0.1)
        
        assert len(received_events) == 2
        assert received_events[0].data['priority'] == 'high'
        assert received_events[1].data['priority'] == 'low'

# Security Tests
class TestSecurity:
    """Test security system functionality."""
    
    def test_security_validation(self, security_manager):
        """Test security validation."""
        # Configure security rules
        security_manager.configure_operation(
            'test.operation',
            SecurityLevel.HIGH
        )
        
        # Test with insufficient security level
        context = SecurityContext(
            level=SecurityLevel.MEDIUM,
            source='test',
            timestamp=datetime.now(),
            metadata={}
        )
        
        with pytest.raises(Exception):
            asyncio.run(
                security_manager.validate_operation('test.operation', context)
            )
            
        # Test with sufficient security level
        context.level = SecurityLevel.HIGH
        assert asyncio.run(
            security_manager.validate_operation('test.operation', context)
        )
        
    def test_security_blocking(self, security_manager):
        """Test source blocking functionality."""
        security_manager.block_source('malicious')
        
        context = SecurityContext(
            level=SecurityLevel.HIGH,
            source='malicious',
            timestamp=datetime.now(),
            metadata={}
        )
        
        with pytest.raises(Exception):
            asyncio.run(
                security_manager.validate_operation('test.operation', context)
            )

# Monitoring Tests
class TestMonitoring:
    """Test monitoring system functionality."""
    
    @pytest.mark.asyncio
    async def test_performance_monitoring(self, system_monitor):
        """Test performance monitoring."""
        # Start monitoring
        monitor_task = asyncio.create_task(
            system_monitor.performance_monitor.start_monitoring()
        )
        
        # Wait for initial metrics
        await asyncio.sleep(2)
        
        # Get collected metrics
        cpu_metrics = system_monitor.performance_monitor.metrics.get_metrics(
            'cpu_usage'
        )
        memory_metrics = system_monitor.performance_monitor.metrics.get_metrics(
            'memory_usage'
        )
        
        assert len(cpu_metrics) > 0
        assert len(memory_metrics) > 0
        
        # Cancel monitoring
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass
            
    def test_error_tracking(self, system_monitor):
        """Test error tracking functionality."""
        try:
            raise ValueError("Test error")
        except Exception as e:
            system_monitor.track_error(e, {'context': 'test'})
            
        assert len(system_monitor.error_tracker.errors) == 1
        assert system_monitor.error_tracker.errors[0]['type'] == 'ValueError'

# Validation Tests
class TestValidation:
    """Test data validation functionality."""
    
    def test_task_validation(self, validation_manager):
        """Test task validation."""
        # Valid task data
        task_data = {
            'id': '123',
            'type': TaskType.AUTOMATION,
            'target_system': 'test',
            'actions': [{'type': 'test', 'parameters': {}}]
        }
        
        task = validation_manager.validate_task(task_data)
        assert task.id == '123'
        assert task.type == TaskType.AUTOMATION
        
        # Invalid task data
        invalid_data = {
            'id': '123',
            'type': TaskType.AUTOMATION,
            'target_system': 'test',
            'actions': []  # Empty actions list should fail
        }
        
        with pytest.raises(ValueError):
            validation_manager.validate_task(invalid_data)
            
    def test_system_command_validation(self, validation_manager):
        """Test system command validation."""
        # Valid command
        command, args, env = validation_manager.validate_system_command(
            'echo',
            ['hello'],
            {}
        )
        assert command == 'echo'
        assert args == ['hello']
        
        # Invalid command
        with pytest.raises(ValueError):
            validation_manager.validate_system_command('', [], {})
