"""
LAM For Gallery - Intelligent Image Search Agent
A LangChain and LangGraph-based agent for gallery image search and management
using Google Gemini API.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__description__ = "Intelligent image gallery search and management agent"

from src.main import initialize_agent
from src.agent import GalleryAgent
from src.types import (
    ImageMetadata,
    SearchQuery,
    SearchResult,
    FilterResult,
    DeleteResult,
    AgentAction,
    AgentState,
    ToolResult,
)
from src.tools import GALLERY_TOOLS

__all__ = [
    "initialize_agent",
    "GalleryAgent",
    "ImageMetadata",
    "SearchQuery",
    "SearchResult",
    "FilterResult",
    "DeleteResult",
    "AgentAction",
    "AgentState",
    "ToolResult",
    "GALLERY_TOOLS",
]
