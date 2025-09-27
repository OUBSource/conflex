from typing import Any, Dict, Type, Optional
from pydantic import BaseModel, ValidationError as PydanticValidationError

from .exceptions import ValidationError

def validate_with_schema(config: Dict[str, Any], schema: Type[BaseModel]) -> BaseModel:
    """Validate configuration against Pydantic schema."""
    try:
        return schema(**config)
    except PydanticValidationError as e:
        raise ValidationError(f"Configuration validation failed: {e}") from e