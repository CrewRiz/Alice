"""Base service layer for Alice system."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

class BaseService(ABC):
    """Abstract base class for all services."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize service resources."""
        pass
        
    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup service resources."""
        pass
        
    async def health_check(self) -> Dict[str, Any]:
        """Check service health status."""
        try:
            return {
                'service': self.__class__.__name__,
                'status': 'healthy',
                'details': await self._get_health_details()
            }
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return {
                'service': self.__class__.__name__,
                'status': 'unhealthy',
                'error': str(e)
            }
            
    @abstractmethod
    async def _get_health_details(self) -> Dict[str, Any]:
        """Get detailed health information."""
        pass
