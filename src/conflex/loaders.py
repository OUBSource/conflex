import json
import os
from pathlib import Path
from typing import Any, Dict
import yaml

from .exceptions import LoaderError

def load_file(filepath: str) -> Dict[str, Any]:
    """Load configuration from file with auto-format detection."""
    path = Path(filepath)
    
    if not path.exists():
        raise LoaderError(f"Config file not found: {filepath}")
    
    content = path.read_text(encoding='utf-8')
    
    # Auto-detect format by extension
    if path.suffix.lower() in ['.yaml', '.yml']:
        return yaml.safe_load(content) or {}
    elif path.suffix.lower() == '.json':
        return json.loads(content)
    else:
        # Try to detect by content
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            try:
                return yaml.safe_load(content) or {}
            except yaml.YAMLError:
                raise LoaderError(f"Unsupported config format: {filepath}")

def load_env(prefix: str = "") -> Dict[str, Any]:
    """Load environment variables with optional prefix."""
    env_vars = {}
    prefix = prefix.upper()
    
    for key, value in os.environ.items():
        if prefix and key.startswith(prefix):
            # Remove prefix and convert to nested dict
            key_parts = key[len(prefix):].lstrip('_').lower().split('_')
            current = env_vars
            for part in key_parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[key_parts[-1]] = _parse_env_value(value)
    
    return env_vars

def _parse_env_value(value: str) -> Any:
    """Try to parse environment variable value to appropriate type."""
    if value.lower() in ('true', 'false'):
        return value.lower() == 'true'
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value