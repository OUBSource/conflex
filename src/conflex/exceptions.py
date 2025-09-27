class ConfigError(Exception):
    """Base exception for all configuration errors."""
    pass

class ValidationError(ConfigError):
    """Raised when configuration validation fails."""
    pass

class LoaderError(ConfigError):
    """Raised when configuration loading fails."""
    pass