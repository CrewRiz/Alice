import asyncio
import psutil
import logging
import json
import subprocess
import os
import signal
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

from TimePerception import QuantumTime
from PersonalityGene import PersonalitySystem

class ProcessPriority(Enum):
    LOW = auto()
    BELOW_NORMAL = auto()
    NORMAL = auto()
    ABOVE_NORMAL = auto()
    HIGH = auto()
    REALTIME = auto()

@dataclass
class ProcessConfig:
    name: str
    command: str
    args: List[str]
    working_dir: Optional[str] = None
    env: Optional[Dict[str, str]] = None
    priority: ProcessPriority = ProcessPriority.NORMAL
    cpu_limit: Optional[float] = None
    memory_limit: Optional[int] = None
    timeout: Optional[float] = None
    restart_policy: Optional[Dict[str, Any]] = None

class ProcessManager:
    def __init__(self, quantum_time: QuantumTime):
        self.reference_time = datetime.fromisoformat("2024-12-23T03:53:51-06:00")
        self.quantum_time = quantum_time
        self.running_processes: Dict[str, psutil.Process] = {}
        self.process_configs: Dict[str, ProcessConfig] = {}
        self.process_stats: Dict[str, List[Dict[str, Any]]] = {}
        
        # Initialize process monitoring
        self.monitoring_enabled = True
        self.monitor_task = None
        
    async def start_process(self, config: ProcessConfig) -> bool:
        """Start a process with advanced configuration."""
        try:
            # Check if process already running
            if config.name in self.running_processes:
                if self.running_processes[config.name].is_running():
                    logging.warning(f"Process {config.name} already running")
                    return False
                    
            # Prepare environment
            env = os.environ.copy()
            if config.env:
                env.update(config.env)
                
            # Start process
            process = await asyncio.create_subprocess_exec(
                config.command,
                *config.args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=config.working_dir,
                env=env
            )
            
            # Get psutil process for monitoring
            psutil_process = psutil.Process(process.pid)
            
            # Set priority
            self._set_process_priority(psutil_process, config.priority)
            
            # Store process information
            self.running_processes[config.name] = psutil_process
            self.process_configs[config.name] = config
            self.process_stats[config.name] = []
            
            # Start monitoring if enabled
            if self.monitoring_enabled:
                await self._ensure_monitor_running()
                
            return True
            
        except Exception as e:
            logging.error(f"Failed to start process {config.name}: {str(e)}")
            return False
            
    def _set_process_priority(self, process: psutil.Process, priority: ProcessPriority):
        """Set process priority."""
        try:
            if os.name == 'nt':  # Windows
                priority_map = {
                    ProcessPriority.LOW: psutil.IDLE_PRIORITY_CLASS,
                    ProcessPriority.BELOW_NORMAL: psutil.BELOW_NORMAL_PRIORITY_CLASS,
                    ProcessPriority.NORMAL: psutil.NORMAL_PRIORITY_CLASS,
                    ProcessPriority.ABOVE_NORMAL: psutil.ABOVE_NORMAL_PRIORITY_CLASS,
                    ProcessPriority.HIGH: psutil.HIGH_PRIORITY_CLASS,
                    ProcessPriority.REALTIME: psutil.REALTIME_PRIORITY_CLASS
                }
            else:  # Unix-like
                priority_map = {
                    ProcessPriority.LOW: 19,
                    ProcessPriority.BELOW_NORMAL: 10,
                    ProcessPriority.NORMAL: 0,
                    ProcessPriority.ABOVE_NORMAL: -10,
                    ProcessPriority.HIGH: -15,
                    ProcessPriority.REALTIME: -20
                }
                
            process.nice(priority_map[priority])
            
        except Exception as e:
            logging.error(f"Failed to set process priority: {str(e)}")
            
    async def stop_process(self, name: str, force: bool = False) -> bool:
        """Stop a running process."""
        try:
            if name not in self.running_processes:
                logging.warning(f"Process {name} not found")
                return False
                
            process = self.running_processes[name]
            
            if force:
                process.kill()
            else:
                process.terminate()
                
            try:
                await asyncio.wait_for(
                    self._wait_for_process_exit(process),
                    timeout=5.0
                )
            except asyncio.TimeoutError:
                process.kill()
                
            del self.running_processes[name]
            return True
            
        except Exception as e:
            logging.error(f"Failed to stop process {name}: {str(e)}")
            return False
            
    async def _wait_for_process_exit(self, process: psutil.Process):
        """Wait for process to exit."""
        while process.is_running():
            await asyncio.sleep(0.1)
            
    async def restart_process(self, name: str) -> bool:
        """Restart a process."""
        try:
            if name not in self.process_configs:
                logging.warning(f"No configuration found for process {name}")
                return False
                
            await self.stop_process(name)
            return await self.start_process(self.process_configs[name])
            
        except Exception as e:
            logging.error(f"Failed to restart process {name}: {str(e)}")
            return False
            
    async def _monitor_processes(self):
        """Monitor running processes."""
        try:
            while self.monitoring_enabled:
                quantum_phase = self.quantum_time.get_current_phase()
                
                for name, process in list(self.running_processes.items()):
                    try:
                        if not process.is_running():
                            await self._handle_process_exit(name)
                            continue
                            
                        # Get process stats
                        stats = {
                            'timestamp': self.reference_time.isoformat(),
                            'cpu_percent': process.cpu_percent(),
                            'memory_percent': process.memory_percent(),
                            'num_threads': process.num_threads(),
                            'io_counters': process.io_counters()._asdict(),
                            'quantum_phase': quantum_phase
                        }
                        
                        # Store stats
                        self.process_stats[name].append(stats)
                        
                        # Trim old stats
                        if len(self.process_stats[name]) > 1000:
                            self.process_stats[name] = self.process_stats[name][-1000:]
                            
                        # Check resource limits
                        await self._check_resource_limits(name, process, stats)
                        
                    except psutil.NoSuchProcess:
                        await self._handle_process_exit(name)
                        
                await asyncio.sleep(1.0)
                
        except Exception as e:
            logging.error(f"Process monitoring failed: {str(e)}")
            
    async def _check_resource_limits(self, name: str, process: psutil.Process, 
                                   stats: Dict[str, Any]):
        """Check if process exceeds resource limits."""
        config = self.process_configs[name]
        
        if config.cpu_limit and stats['cpu_percent'] > config.cpu_limit:
            logging.warning(f"Process {name} exceeded CPU limit")
            await self._handle_resource_violation(name, 'cpu')
            
        if config.memory_limit and stats['memory_percent'] > config.memory_limit:
            logging.warning(f"Process {name} exceeded memory limit")
            await self._handle_resource_violation(name, 'memory')
            
    async def _handle_resource_violation(self, name: str, resource_type: str):
        """Handle process resource violation."""
        config = self.process_configs[name]
        
        if config.restart_policy:
            policy = config.restart_policy.get(resource_type)
            if policy == 'restart':
                await self.restart_process(name)
            elif policy == 'stop':
                await self.stop_process(name)
                
    async def _handle_process_exit(self, name: str):
        """Handle process exit."""
        config = self.process_configs[name]
        
        if config.restart_policy and config.restart_policy.get('on_exit') == 'restart':
            await self.restart_process(name)
        else:
            if name in self.running_processes:
                del self.running_processes[name]
                
    async def _ensure_monitor_running(self):
        """Ensure process monitor is running."""
        if self.monitor_task is None or self.monitor_task.done():
            self.monitor_task = asyncio.create_task(self._monitor_processes())
            
    def get_process_stats(self, name: str, 
                         num_samples: int = 100) -> List[Dict[str, Any]]:
        """Get process statistics."""
        if name not in self.process_stats:
            return []
            
        return self.process_stats[name][-num_samples:]
        
    def get_all_processes(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all managed processes."""
        result = {}
        for name, process in self.running_processes.items():
            try:
                if process.is_running():
                    result[name] = {
                        'pid': process.pid,
                        'status': process.status(),
                        'cpu_percent': process.cpu_percent(),
                        'memory_percent': process.memory_percent(),
                        'create_time': datetime.fromtimestamp(
                            process.create_time()
                        ).isoformat()
                    }
            except psutil.NoSuchProcess:
                continue
                
        return result
        
    async def cleanup(self):
        """Clean up all managed processes."""
        self.monitoring_enabled = False
        
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
                
        for name in list(self.running_processes.keys()):
            await self.stop_process(name, force=True)
            
    def export_stats(self, filepath: str):
        """Export process statistics to file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.process_stats, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to export stats: {str(e)}")
            
    def import_stats(self, filepath: str):
        """Import process statistics from file."""
        try:
            with open(filepath, 'r') as f:
                self.process_stats = json.load(f)
        except Exception as e:
            logging.error(f"Failed to import stats: {str(e)}")
