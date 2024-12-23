"""Event system for Alice."""
from typing import Dict, Any, List, Callable, Set
import asyncio
import logging
from datetime import datetime
from dataclasses import dataclass
from enum import Enum, auto

class EventPriority(Enum):
    """Event priority levels."""
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()

@dataclass
class Event:
    """Base event class."""
    type: str
    data: Dict[str, Any]
    timestamp: datetime
    priority: EventPriority = EventPriority.MEDIUM
    source: str = "system"

class EventBus:
    """Central event management system."""
    
    def __init__(self):
        self._subscribers: Dict[str, Set[Callable]] = {}
        self._priority_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self._is_running = False
        self.logger = logging.getLogger(__name__)
        
    async def start(self):
        """Start event processing."""
        self._is_running = True
        asyncio.create_task(self._process_events())
        self.logger.info("Event bus started")
        
    async def stop(self):
        """Stop event processing."""
        self._is_running = False
        self.logger.info("Event bus stopped")
        
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to events of specified type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = set()
        self._subscribers[event_type].add(handler)
        self.logger.debug(f"Handler subscribed to {event_type}")
        
    def unsubscribe(self, event_type: str, handler: Callable):
        """Unsubscribe from events of specified type."""
        if event_type in self._subscribers:
            self._subscribers[event_type].discard(handler)
            self.logger.debug(f"Handler unsubscribed from {event_type}")
            
    async def publish(self, event: Event):
        """Publish an event to subscribers."""
        try:
            # Add to priority queue
            await self._priority_queue.put((event.priority.value, event))
            self.logger.debug(f"Event published: {event.type}")
        except Exception as e:
            self.logger.error(f"Error publishing event: {str(e)}")
            
    async def _process_events(self):
        """Process events from the priority queue."""
        while self._is_running:
            try:
                # Get next event from queue
                _, event = await self._priority_queue.get()
                
                # Get subscribers for this event type
                handlers = self._subscribers.get(event.type, set())
                
                # Process event with all subscribers
                await asyncio.gather(
                    *[self._safe_handle(handler, event) for handler in handlers],
                    return_exceptions=True
                )
                
                self._priority_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error processing event: {str(e)}")
                await asyncio.sleep(1)  # Prevent tight loop on error
                
    async def _safe_handle(self, handler: Callable, event: Event):
        """Safely execute event handler."""
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)
        except Exception as e:
            self.logger.error(f"Error in event handler: {str(e)}")
            
class EventManager:
    """High-level event management interface."""
    
    def __init__(self):
        self.event_bus = EventBus()
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self):
        """Initialize event system."""
        await self.event_bus.start()
        self.logger.info("Event manager initialized")
        
    async def cleanup(self):
        """Cleanup event system."""
        await self.event_bus.stop()
        self.logger.info("Event manager cleaned up")
        
    def create_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        priority: EventPriority = EventPriority.MEDIUM,
        source: str = "system"
    ) -> Event:
        """Create a new event."""
        return Event(
            type=event_type,
            data=data,
            timestamp=datetime.now(),
            priority=priority,
            source=source
        )
        
    async def emit(
        self,
        event_type: str,
        data: Dict[str, Any],
        priority: EventPriority = EventPriority.MEDIUM,
        source: str = "system"
    ):
        """Emit a new event."""
        event = self.create_event(event_type, data, priority, source)
        await self.event_bus.publish(event)
