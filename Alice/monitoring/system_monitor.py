"""System monitoring for Alice."""
import asyncio
import logging
import psutil
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum, auto

from events.event_system import EventManager, EventPriority, Event

class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()

@dataclass
class MetricPoint:
    """Single metric measurement."""
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str]

class MetricsCollector:
    """Collects and stores system metrics."""
    
    def __init__(self, retention_hours: int = 24):
        self.metrics: List[MetricPoint] = []
        self.retention_hours = retention_hours
        self.logger = logging.getLogger(__name__)
        
    def add_metric(self, name: str, value: float, labels: Dict[str, str]):
        """Add a new metric measurement."""
        self.metrics.append(
            MetricPoint(
                name=name,
                value=value,
                timestamp=datetime.now(),
                labels=labels
            )
        )
        self._cleanup_old_metrics()
        
    def get_metrics(
        self,
        name: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        hours: Optional[int] = None
    ) -> List[MetricPoint]:
        """Get metrics matching criteria."""
        cutoff = datetime.now() - timedelta(hours=hours if hours else self.retention_hours)
        
        return [
            m for m in self.metrics
            if (not name or m.name == name) and
               (not labels or all(m.labels.get(k) == v for k, v in labels.items())) and
               m.timestamp >= cutoff
        ]
        
    def _cleanup_old_metrics(self):
        """Remove metrics older than retention period."""
        cutoff = datetime.now() - timedelta(hours=self.retention_hours)
        self.metrics = [m for m in self.metrics if m.timestamp >= cutoff]

class PerformanceMonitor:
    """Monitors system performance metrics."""
    
    def __init__(self, event_manager: EventManager):
        self.event_manager = event_manager
        self.metrics = MetricsCollector()
        self.logger = logging.getLogger(__name__)
        
    async def start_monitoring(self):
        """Start performance monitoring."""
        while True:
            try:
                # Collect system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                # Store metrics
                self.metrics.add_metric('cpu_usage', cpu_percent, {'type': 'system'})
                self.metrics.add_metric('memory_usage', memory.percent, {'type': 'system'})
                self.metrics.add_metric('disk_usage', disk.percent, {'type': 'system'})
                
                # Check thresholds and emit events if needed
                await self._check_thresholds({
                    'cpu_usage': cpu_percent,
                    'memory_usage': memory.percent,
                    'disk_usage': disk.percent
                })
                
                await asyncio.sleep(60)  # Collect metrics every minute
                
            except Exception as e:
                self.logger.error(f"Error collecting metrics: {str(e)}")
                await asyncio.sleep(60)  # Wait before retrying
                
    async def _check_thresholds(self, metrics: Dict[str, float]):
        """Check metrics against thresholds and emit alerts."""
        thresholds = {
            'cpu_usage': {'warning': 70, 'critical': 90},
            'memory_usage': {'warning': 80, 'critical': 95},
            'disk_usage': {'warning': 85, 'critical': 95}
        }
        
        for metric, value in metrics.items():
            if metric in thresholds:
                if value >= thresholds[metric]['critical']:
                    await self._emit_alert(
                        f"{metric} is critical: {value}%",
                        AlertLevel.CRITICAL
                    )
                elif value >= thresholds[metric]['warning']:
                    await self._emit_alert(
                        f"{metric} is high: {value}%",
                        AlertLevel.WARNING
                    )
                    
    async def _emit_alert(self, message: str, level: AlertLevel):
        """Emit alert event."""
        await self.event_manager.emit(
            'system.alert',
            {
                'message': message,
                'level': level.name,
                'timestamp': datetime.now().isoformat()
            },
            priority=EventPriority.HIGH
        )

class ErrorTracker:
    """Tracks and analyzes system errors."""
    
    def __init__(self, event_manager: EventManager):
        self.event_manager = event_manager
        self.errors: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)
        
    def track_error(self, error: Exception, context: Dict[str, Any]):
        """Track a new error."""
        error_data = {
            'type': type(error).__name__,
            'message': str(error),
            'timestamp': datetime.now().isoformat(),
            'context': context
        }
        
        self.errors.append(error_data)
        self._analyze_error(error_data)
        
    def _analyze_error(self, error_data: Dict[str, Any]):
        """Analyze error patterns and emit alerts if needed."""
        try:
            # Count recent errors of same type
            recent_similar_errors = [
                e for e in self.errors
                if e['type'] == error_data['type'] and
                datetime.fromisoformat(e['timestamp']) > datetime.now() - timedelta(minutes=5)
            ]
            
            if len(recent_similar_errors) >= 3:
                asyncio.create_task(
                    self._emit_error_alert(
                        f"Multiple {error_data['type']} errors detected",
                        AlertLevel.ERROR,
                        error_data
                    )
                )
                
        except Exception as e:
            self.logger.error(f"Error analyzing error pattern: {str(e)}")
            
    async def _emit_error_alert(
        self,
        message: str,
        level: AlertLevel,
        error_data: Dict[str, Any]
    ):
        """Emit error alert event."""
        await self.event_manager.emit(
            'system.error_alert',
            {
                'message': message,
                'level': level.name,
                'error_data': error_data,
                'timestamp': datetime.now().isoformat()
            },
            priority=EventPriority.HIGH
        )

class SystemMonitor:
    """Coordinates all monitoring activities."""
    
    def __init__(self, event_manager: EventManager):
        self.event_manager = event_manager
        self.performance_monitor = PerformanceMonitor(event_manager)
        self.error_tracker = ErrorTracker(event_manager)
        self.logger = logging.getLogger(__name__)
        
    async def start(self):
        """Start all monitoring systems."""
        try:
            # Start performance monitoring
            monitoring_task = asyncio.create_task(
                self.performance_monitor.start_monitoring()
            )
            
            self.logger.info("System monitoring started")
            
            # Keep monitoring running
            await monitoring_task
            
        except Exception as e:
            self.logger.error(f"Error in system monitoring: {str(e)}")
            
    def track_error(self, error: Exception, context: Dict[str, Any]):
        """Track a system error."""
        self.error_tracker.track_error(error, context)
