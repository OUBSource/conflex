from pydantic import BaseModel
from conflex import load_config

# Define your configuration schema with default values where possible
class DatabaseConfig(BaseModel):
    host: str = "localhost"
    port: int = 5432
    username: str = "postgres"
    password: str = ""

class AppConfig(BaseModel):
    debug: bool = False
    database: DatabaseConfig = DatabaseConfig()
    api_key: str = ""

# Create test config files first
def create_test_files():
    """Create example config files for testing"""
    import os
    os.makedirs('tests/configs', exist_ok=True)
    
    # Base config
    with open('tests/configs/base.yaml', 'w') as f:
        f.write("""
debug: true
database:
  host: localhost
  port: 5432
api_key: base_key_123
        """)
    
    # Production config (overrides some values)
    with open('tests/configs/production.yaml', 'w') as f:
        f.write("""
debug: false
database:
  host: production-db.example.com
  port: 5432
  username: admin
api_key: ${PROD_API_KEY}
        """)

# Usage examples:
if __name__ == "__main__":
    create_test_files()
    
    print("=== Example 1: Simple loading ===")
    try:
        config = load_config('tests/configs/base.yaml', required=False)
        print("Config loaded successfully!")
        print(f"Database host: {config.get('database.host')}")
        print(f"Debug mode: {config.get('debug')}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n=== Example 2: Multiple file inheritance ===")
    try:
        config = load_config([
            'tests/configs/base.yaml', 
            'tests/configs/production.yaml'
        ], required=False)
        print("Config loaded successfully!")
        print(f"Database host: {config.get('database.host')}")  # Should show production host
        print(f"Debug mode: {config.get('debug')}")  # Should show false (overridden)
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n=== Example 3: With validation ===")
    try:
        # Set some environment variables for testing
        import os
        os.environ['MYAPP_DATABASE_PASSWORD'] = 'env_secret'
        os.environ['MYAPP_API_KEY'] = 'env_api_key'
        
        validated_config = load_config(
            files=['tests/configs/base.yaml', 'tests/configs/production.yaml'],
            env_prefix='MYAPP_',
            schema=AppConfig,
            required=False
        )
        
        print("Config validated successfully!")
        print(f"Database host: {validated_config.database.host}")
        print(f"Database password: {validated_config.database.password}")  # From env
        print(f"API Key: {validated_config.api_key}")
        
    except Exception as e:
        print(f"Validation error: {e}")
    
    print("\n=== Example 4: Empty config (should work with defaults) ===")
    try:
        # Test with non-existent files but with schema defaults
        empty_config = load_config(
            files=['non_existent.yaml'],
            schema=AppConfig,
            required=False  # Don't require files to exist
        )
        
        print("Empty config handled successfully!")
        print(f"Default database host: {empty_config.database.host}")
        print(f"Default debug mode: {empty_config.debug}")
        
    except Exception as e:
        print(f"Error: {e}")