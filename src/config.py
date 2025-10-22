"""
Configuration and constants for the Gallery Image Search Agent
"""

import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()


class GeminiConfig:
    """Configuration for Google Gemini API"""

    # API Configuration
    API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    MODEL: str = os.getenv("GEMINI_MODEL", "gemini-pro")

    # LLM Parameters
    TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    TOP_P: float = float(os.getenv("LLM_TOP_P", "0.9"))
    TOP_K: int = int(os.getenv("LLM_TOP_K", "40"))
    MAX_OUTPUT_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "2048"))


class AgentConfig:
    """Configuration for the Gallery Agent"""

    # Max conversation history to maintain
    MAX_HISTORY: int = int(os.getenv("MAX_HISTORY", "20"))

    # Default search limit
    DEFAULT_SEARCH_LIMIT: int = int(os.getenv("DEFAULT_SEARCH_LIMIT", "10"))

    # Enable debug logging
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Timeout for tool execution (seconds)
    TOOL_TIMEOUT: int = int(os.getenv("TOOL_TIMEOUT", "30"))

    # Enable multi-step reasoning
    MULTI_STEP_REASONING: bool = (
        os.getenv("MULTI_STEP_REASONING", "true").lower() == "true"
    )


class QualityThresholds:
    """Quality level definitions"""

    EXCELLENT = "excellent"
    GOOD = "good"
    POOR = "poor"
    BLURRY = "blurry"

    LEVELS = [EXCELLENT, GOOD, POOR, BLURRY]

    # Numeric mapping for quality comparison
    QUALITY_SCORES = {
        EXCELLENT: 4,
        GOOD: 3,
        POOR: 2,
        BLURRY: 1,
    }


class ToolConfig:
    """Configuration for tools"""

    # Tools that require confirmation before execution
    CONFIRMATION_REQUIRED = ["delete_images"]

    # Tools that support batch operations
    BATCH_TOOLS = ["tag_images", "delete_images"]

    # Max batch size for operations
    MAX_BATCH_SIZE = 100


class Messages:
    """Standard messages for the agent"""

    WELCOME = "Welcome to the Gallery Image Search Agent. How can I help you?"

    SEARCH_PLACEHOLDER = "Searching for images matching your criteria..."

    FILTER_PLACEHOLDER = "Analyzing image quality..."

    DELETE_CONFIRMATION = "Are you sure you want to delete {count} images?"

    OPERATION_SUCCESS = "Operation completed successfully."

    OPERATION_FAILED = "An error occurred during the operation."

    INVALID_API_KEY = (
        "Invalid or missing GOOGLE_API_KEY. "
        "Please set it in .env file or environment variable."
    )


def validate_config() -> bool:
    """
    Validate the configuration.

    Returns:
        True if configuration is valid, False otherwise
    """
    if not GeminiConfig.API_KEY:
        print(f"⚠️  Warning: {Messages.INVALID_API_KEY}")
        return False

    if AgentConfig.DEBUG:
        print("🔍 Debug mode enabled")

    return True


def print_config() -> None:
    """Print current configuration (excluding sensitive data)."""
    print("\n" + "="*60)
    print("AGENT CONFIGURATION")
    print("="*60)

    print("\n📡 Gemini Configuration:")
    print(f"   Model: {GeminiConfig.MODEL}")
    print(f"   Temperature: {GeminiConfig.TEMPERATURE}")
    print(f"   Top-P: {GeminiConfig.TOP_P}")
    print(f"   Top-K: {GeminiConfig.TOP_K}")

    print("\n🤖 Agent Configuration:")
    print(f"   Max History: {AgentConfig.MAX_HISTORY}")
    print(f"   Default Search Limit: {AgentConfig.DEFAULT_SEARCH_LIMIT}")
    print(f"   Tool Timeout: {AgentConfig.TOOL_TIMEOUT}s")
    print(f"   Multi-step Reasoning: {AgentConfig.MULTI_STEP_REASONING}")
    print(f"   Debug Mode: {AgentConfig.DEBUG}")

    print("\n🔧 Tool Configuration:")
    print(f"   Confirmation Required: {ToolConfig.CONFIRMATION_REQUIRED}")
    print(f"   Batch Tools: {ToolConfig.BATCH_TOOLS}")
    print(f"   Max Batch Size: {ToolConfig.MAX_BATCH_SIZE}")

    print("\n" + "="*60)


# Export configuration objects
__all__ = [
    "GeminiConfig",
    "AgentConfig",
    "QualityThresholds",
    "ToolConfig",
    "Messages",
    "validate_config",
    "print_config",
]
