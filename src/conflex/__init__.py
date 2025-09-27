"""Conflex - Smart configuration manager for Python."""

from .core import Config, load_config
from .exceptions import ConfigError, ValidationError

__version__ = "0.1.0"
__all__ = ["Config", "load_config", "ConfigError", "ValidationError"]