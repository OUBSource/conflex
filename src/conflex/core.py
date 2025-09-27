from pathlib import Path
from typing import Any, Dict, Optional, Type, Union
from pydantic import BaseModel

from .loaders import load_file, load_env
from .validators import validate_with_schema
from .exceptions import ConfigError, ValidationError

class Config:
    """Smart configuration manager."""
    
    def __init__(self):
        self._data: Dict[str, Any] = {}
    
    def load_file(self, filepath: str, merge: bool = True) -> 'Config':
        """Load configuration from file."""
        try:
            file_data = load_file(filepath)
            
            if merge:
                self._merge_data(file_data)
            else:
                self._data = file_data
            
            return self
        except Exception as e:
            raise ConfigError(f"Failed to load file {filepath}: {e}") from e
    
    def load_env(self, prefix: str = "", merge: bool = True) -> 'Config':
        """Load configuration from environment variables."""
        try:
            env_data = load_env(prefix)
            
            if merge:
                self._merge_data(env_data)
            else:
                self._data = env_data
            
            return self
        except Exception as e:
            raise ConfigError(f"Failed to load environment variables: {e}") from e
    
    def _merge_data(self, new_data: Dict[str, Any]) -> None:
        """Recursively merge new data into existing configuration."""
        def _merge_dicts(base: Dict, update: Dict) -> Dict:
            for key, value in update.items():
                if (key in base and isinstance(base[key], dict) 
                    and isinstance(value, dict)):
                    base[key] = _merge_dicts(base[key], value)
                else:
                    base[key] = value
            return base
        
        self._data = _merge_dicts(self._data, new_data)
    
    def validate(self, schema: Type[BaseModel]) -> BaseModel:
        """Validate configuration against Pydantic schema."""
        return validate_with_schema(self._data, schema)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot notation."""
        keys = key.split('.')
        value = self._data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary."""
        return self._data.copy()
    
    def __repr__(self) -> str:
        return f"Config(data={self._data})"

def load_config(
    files: Optional[Union[str, list]] = None,
    env_prefix: str = "",
    schema: Optional[Type[BaseModel]] = None,
    required: bool = True
) -> Union[Config, BaseModel]:
    """
    High-level function to load and validate configuration.
    
    Args:
        files: Single file path or list of file paths (loaded in order)
        env_prefix: Prefix for environment variables
        schema: Pydantic schema for validation
        required: If True, raises error when no config files found
    
    Returns:
        Config object or validated schema instance
    """
    config = Config()
    files_loaded = False
    
    # Load files
    if files:
        if isinstance(files, str):
            files = [files]
        
        for file_path in files:
            try:
                if Path(file_path).exists():
                    config.load_file(file_path)
                    files_loaded = True
                    print(f"✓ Loaded config from: {file_path}")
                else:
                    print(f"⚠ Config file not found: {file_path}")
            except Exception as e:
                print(f"⚠ Failed to load {file_path}: {e}")
    
    # Load environment variables
    if env_prefix:
        try:
            env_data = load_env(env_prefix)
            if env_data:
                config.load_env(env_prefix)
                print(f"✓ Loaded environment variables with prefix: {env_prefix}")
        except Exception as e:
            print(f"⚠ Failed to load environment variables: {e}")
    
    # Check if any configuration was loaded
    if not config.to_dict() and required:
        raise ConfigError("No configuration sources provided or all sources are empty")
    
    # Validate if schema provided
    if schema:
        try:
            return config.validate(schema)
        except ValidationError as e:
            print(f"❌ Configuration validation failed:")
            print(f"Current config: {config.to_dict()}")
            raise
    
    return config