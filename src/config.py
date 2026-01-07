"""
Configuration for the Refactoring Swarm system.
"""

# Model Configuration
# Choose based on your API tier and rate limit needs

# Available models with their rate limits:
# - gemini-1.5-flash: 15 RPM, 1M TPM, 1500 RPD (RECOMMENDED for free tier)
# - gemini-2.0-flash-exp: 10 RPM, 250K TPM, 500 RPD
# - gemini-1.5-pro: 2 RPM, 32K TPM, 50 RPD (slowest but most capable)

DEFAULT_MODEL = "gemini-1.5-flash-latest"  # Best balance of speed and rate limits

# Rate limiting configuration (automatically set based on model)
RATE_LIMITS = {
    "gemini-1.5-flash-latest": {
        "rpm": 15,  # Requests per minute
        "tpm": 1_000_000,  # Tokens per minute
        "rpd": 1500,  # Requests per day
        "interval": 4.5  # Seconds between requests (60/15 + buffer)
    },
    "gemini-1.5-flash": {
        "rpm": 15,
        "tpm": 1_000_000,
        "rpd": 1500,
        "interval": 4.5
    },
    "gemini-2.0-flash-exp": {
        "rpm": 10,
        "tpm": 250_000,
        "rpd": 500,
        "interval": 6.5  # Seconds between requests (60/10 + buffer)
    },
    "gemini-1.5-pro": {
        "rpm": 2,
        "tpm": 32_000,
        "rpd": 50,
        "interval": 31  # Seconds between requests (60/2 + buffer)
    }
}

# Orchestrator Configuration
MAX_ITERATIONS = 10  # Maximum self-healing loop iterations
ENABLE_BACKUPS = True  # Create backup files before modifying

# Logging Configuration
LOG_DIR = "logs"
LOG_FILE = "experiment_data.json"

# Sandbox Configuration
SANDBOX_DIR = "sandbox"
