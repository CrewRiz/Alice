import asyncio
import logging
import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
import aiofiles
import aiohttp
import sqlite3
import yaml
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class DataFormat(Enum):
    JSON = auto()
    CSV = auto()
    EXCEL = auto()
    SQL = auto()
    YAML = auto()
    XML = auto()
    PARQUET = auto()
    AVRO = auto()

class DataTransformation(Enum):
    FILTER = auto()
    MAP = auto()
    REDUCE = auto()
    GROUP = auto()
    SORT = auto()
    JOIN = auto()
    PIVOT = auto()
    UNPIVOT = auto()

@dataclass
class DataConfig:
    format: DataFormat
    schema: Optional[Dict[str, Any]] = None
    validation_rules: Optional[List[Dict[str, Any]]] = None
    transformation_rules: Optional[List[Dict[str, Any]]] = None
    storage_options: Optional[Dict[str, Any]] = None
    cache_options: Optional[Dict[str, Any]] = None

class DataManager:
    def __init__(self):
        self.reference_time = datetime.fromisoformat("2024-12-23T03:53:51-06:00")
        self.data_cache: Dict[str, Any] = {}
        self.data_configs: Dict[str, DataConfig] = {}
        self.file_observers: Dict[str, Observer] = {}
        self.transformation_functions: Dict[str, Callable] = {}
        self.db_connections: Dict[str, sqlite3.Connection] = {}
        
        # Register default transformations
        self._register_default_transformations()
        
    def _register_default_transformations(self):
        """Register default data transformation functions."""
        self.transformation_functions.update({
            'filter': lambda data, condition: data[data.apply(condition, axis=1)],
            'map': lambda data, func: data.apply(func),
            'reduce': lambda data, func: data.agg(func),
            'group': lambda data, keys: data.groupby(keys),
            'sort': lambda data, by, **kwargs: data.sort_values(by, **kwargs),
            'join': lambda left, right, **kwargs: pd.merge(left, right, **kwargs),
            'pivot': lambda data, **kwargs: pd.pivot_table(data, **kwargs),
            'unpivot': lambda data, **kwargs: pd.melt(data, **kwargs)
        })
        
    async def read_data(self, source: str, config: DataConfig) -> Any:
        """Read data from various sources with caching."""
        try:
            # Check cache first
            if source in self.data_cache and config.cache_options:
                cache_time = self.data_cache[source]['timestamp']
                if (self.reference_time - cache_time).total_seconds() < config.cache_options.get('ttl', 300):
                    return self.data_cache[source]['data']
                    
            # Read data based on format
            data = await self._read_by_format(source, config.format)
            
            # Validate if schema provided
            if config.schema:
                self._validate_schema(data, config.schema)
                
            # Apply validation rules
            if config.validation_rules:
                data = self._apply_validation_rules(data, config.validation_rules)
                
            # Apply transformations
            if config.transformation_rules:
                data = await self._apply_transformations(data, config.transformation_rules)
                
            # Update cache
            if config.cache_options:
                self.data_cache[source] = {
                    'data': data,
                    'timestamp': self.reference_time
                }
                
            return data
            
        except Exception as e:
            logging.error(f"Failed to read data from {source}: {str(e)}")
            raise
            
    async def write_data(self, data: Any, target: str, config: DataConfig) -> bool:
        """Write data to various targets."""
        try:
            # Validate before writing
            if config.schema:
                self._validate_schema(data, config.schema)
                
            # Apply transformations before writing
            if config.transformation_rules:
                data = await self._apply_transformations(data, config.transformation_rules)
                
            # Write data based on format
            await self._write_by_format(data, target, config.format)
            
            # Update cache if enabled
            if config.cache_options:
                self.data_cache[target] = {
                    'data': data,
                    'timestamp': self.reference_time
                }
                
            return True
            
        except Exception as e:
            logging.error(f"Failed to write data to {target}: {str(e)}")
            return False
            
    async def _read_by_format(self, source: str, format: DataFormat) -> Any:
        """Read data based on format."""
        if format == DataFormat.JSON:
            async with aiofiles.open(source, 'r') as f:
                content = await f.read()
                return pd.read_json(content)
        elif format == DataFormat.CSV:
            return pd.read_csv(source)
        elif format == DataFormat.EXCEL:
            return pd.read_excel(source)
        elif format == DataFormat.SQL:
            conn = self._get_db_connection(source)
            return pd.read_sql(source, conn)
        elif format == DataFormat.YAML:
            async with aiofiles.open(source, 'r') as f:
                content = await f.read()
                return pd.DataFrame(yaml.safe_load(content))
        elif format == DataFormat.PARQUET:
            return pd.read_parquet(source)
        else:
            raise ValueError(f"Unsupported format: {format}")
            
    async def _write_by_format(self, data: Any, target: str, format: DataFormat):
        """Write data based on format."""
        if format == DataFormat.JSON:
            async with aiofiles.open(target, 'w') as f:
                await f.write(data.to_json(orient='records', indent=2))
        elif format == DataFormat.CSV:
            data.to_csv(target, index=False)
        elif format == DataFormat.EXCEL:
            data.to_excel(target, index=False)
        elif format == DataFormat.SQL:
            conn = self._get_db_connection(target)
            data.to_sql(target, conn, if_exists='replace')
        elif format == DataFormat.YAML:
            async with aiofiles.open(target, 'w') as f:
                await f.write(yaml.dump(data.to_dict(orient='records')))
        elif format == DataFormat.PARQUET:
            data.to_parquet(target)
        else:
            raise ValueError(f"Unsupported format: {format}")
            
    def _validate_schema(self, data: pd.DataFrame, schema: Dict[str, Any]):
        """Validate data against schema."""
        for column, requirements in schema.items():
            if column not in data.columns:
                raise ValueError(f"Required column {column} not found in data")
                
            dtype = requirements.get('type')
            if dtype:
                if str(data[column].dtype) != dtype:
                    try:
                        data[column] = data[column].astype(dtype)
                    except:
                        raise ValueError(f"Column {column} cannot be converted to {dtype}")
                        
            if 'unique' in requirements and requirements['unique']:
                if not data[column].is_unique:
                    raise ValueError(f"Column {column} must contain unique values")
                    
            if 'range' in requirements:
                range_req = requirements['range']
                if not data[column].between(range_req[0], range_req[1]).all():
                    raise ValueError(f"Values in {column} must be between {range_req[0]} and {range_req[1]}")
                    
    def _apply_validation_rules(self, data: pd.DataFrame, 
                              rules: List[Dict[str, Any]]) -> pd.DataFrame:
        """Apply validation rules to data."""
        for rule in rules:
            rule_type = rule['type']
            if rule_type == 'missing':
                columns = rule.get('columns', data.columns)
                if rule.get('action') == 'drop':
                    data = data.dropna(subset=columns)
                else:
                    fill_value = rule.get('fill_value', 0)
                    data = data.fillna(fill_value)
            elif rule_type == 'duplicate':
                columns = rule.get('columns', None)
                if rule.get('action') == 'drop':
                    data = data.drop_duplicates(subset=columns)
            elif rule_type == 'outlier':
                column = rule['column']
                threshold = rule['threshold']
                if rule.get('action') == 'drop':
                    data = data[abs(data[column] - data[column].mean()) <= threshold * data[column].std()]
                else:
                    data.loc[abs(data[column] - data[column].mean()) > threshold * data[column].std(), column] = rule.get('fill_value', data[column].mean())
                    
        return data
        
    async def _apply_transformations(self, data: pd.DataFrame, 
                                   transformations: List[Dict[str, Any]]) -> pd.DataFrame:
        """Apply transformation rules to data."""
        for transform in transformations:
            transform_type = DataTransformation[transform['type'].upper()]
            params = transform.get('params', {})
            
            if transform_type == DataTransformation.FILTER:
                data = self.transformation_functions['filter'](data, params['condition'])
            elif transform_type == DataTransformation.MAP:
                data = self.transformation_functions['map'](data, params['function'])
            elif transform_type == DataTransformation.REDUCE:
                data = self.transformation_functions['reduce'](data, params['function'])
            elif transform_type == DataTransformation.GROUP:
                data = self.transformation_functions['group'](data, params['keys'])
            elif transform_type == DataTransformation.SORT:
                data = self.transformation_functions['sort'](data, **params)
            elif transform_type == DataTransformation.JOIN:
                other_data = await self.read_data(params['right_source'], self.data_configs[params['right_source']])
                data = self.transformation_functions['join'](data, other_data, **params['join_params'])
            elif transform_type == DataTransformation.PIVOT:
                data = self.transformation_functions['pivot'](data, **params)
            elif transform_type == DataTransformation.UNPIVOT:
                data = self.transformation_functions['unpivot'](data, **params)
                
        return data
        
    def _get_db_connection(self, connection_string: str) -> sqlite3.Connection:
        """Get or create database connection."""
        if connection_string not in self.db_connections:
            self.db_connections[connection_string] = sqlite3.connect(connection_string)
        return self.db_connections[connection_string]
        
    def watch_file(self, filepath: str, callback: Callable[[str], None]):
        """Watch a file for changes."""
        class Handler(FileSystemEventHandler):
            def on_modified(self, event):
                if not event.is_directory and event.src_path == filepath:
                    callback(filepath)
                    
        if filepath not in self.file_observers:
            observer = Observer()
            handler = Handler()
            observer.schedule(handler, str(Path(filepath).parent), recursive=False)
            observer.start()
            self.file_observers[filepath] = observer
            
    def stop_watching(self, filepath: str):
        """Stop watching a file."""
        if filepath in self.file_observers:
            self.file_observers[filepath].stop()
            self.file_observers[filepath].join()
            del self.file_observers[filepath]
            
    async def cleanup(self):
        """Clean up resources."""
        # Stop all file observers
        for observer in self.file_observers.values():
            observer.stop()
        for observer in self.file_observers.values():
            observer.join()
            
        # Close database connections
        for conn in self.db_connections.values():
            conn.close()
            
        # Clear caches
        self.data_cache.clear()
        self.file_observers.clear()
        self.db_connections.clear()
