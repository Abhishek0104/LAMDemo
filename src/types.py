"""
Gallery Image Search Agent - Type Definitions and Models
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field


class ImageMetadata(BaseModel):
    """Represents metadata for a gallery image"""
    id: str = Field(..., description="Unique identifier for the image")
    filename: str = Field(..., description="Original filename")
    path: str = Field(..., description="File path to the image")
    uploaded_at: datetime = Field(..., description="Upload timestamp")
    captured_at: Optional[datetime] = Field(None, description="When the photo was taken")
    location: Optional[str] = Field(None, description="Geographic location of the image")
    tags: List[str] = Field(default_factory=list, description="Associated tags")
    relations: List[str] = Field(default_factory=list, description="Related image IDs")
    quality: Optional[Literal['excellent', 'good', 'poor', 'blurry']] = Field(
        None, description="Image quality assessment"
    )
    width: Optional[int] = Field(None, description="Image width in pixels")
    height: Optional[int] = Field(None, description="Image height in pixels")
    size: Optional[int] = Field(None, description="File size in bytes")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SearchQuery(BaseModel):
    """Represents a search query for gallery images"""
    text: Optional[str] = Field(None, description="Text-based search query")
    date_range: Optional[Dict[str, datetime]] = Field(
        None, description="Date range filter (start and end)"
    )
    location: Optional[str] = Field(None, description="Location filter")
    tags: Optional[List[str]] = Field(None, description="Tags filter")
    relations: Optional[List[str]] = Field(None, description="Relations filter")
    quality: Optional[Literal['excellent', 'good', 'poor', 'blurry']] = Field(
        None, description="Quality filter"
    )
    limit: Optional[int] = Field(None, description="Maximum number of results")


class SearchResult(BaseModel):
    """Represents search results"""
    images: List[ImageMetadata] = Field(..., description="List of matching images")
    total_count: int = Field(..., description="Total number of matching images")
    query: SearchQuery = Field(..., description="The query that was executed")
    executed_at: datetime = Field(..., description="Timestamp of execution")


class FilterResult(BaseModel):
    """Represents results of filtering operation"""
    removed: List[ImageMetadata] = Field(..., description="Images that were removed")
    kept: List[ImageMetadata] = Field(..., description="Images that were kept")
    total_processed: int = Field(..., description="Total images processed")
    criteria: str = Field(..., description="Filtering criteria applied")
    executed_at: datetime = Field(..., description="Timestamp of execution")


class DeleteResult(BaseModel):
    """Represents results of delete operation"""
    deleted_ids: List[str] = Field(..., description="IDs of deleted images")
    count: int = Field(..., description="Number of deleted images")
    timestamp: datetime = Field(..., description="Timestamp of deletion")


class AgentAction(BaseModel):
    """Represents an action taken by the agent"""
    type: Literal['search', 'filter', 'delete', 'analyze', 'tag'] = Field(
        ..., description="Type of action"
    )
    params: Dict[str, Any] = Field(..., description="Action parameters")


class ToolResult(BaseModel):
    """Represents the result of a tool execution"""
    success: bool = Field(..., description="Whether the tool execution was successful")
    data: Any = Field(..., description="Result data")
    message: str = Field(..., description="Result message")
    timestamp: datetime = Field(..., description="Execution timestamp")


class AgentState(BaseModel):
    """Represents the state of the agent during execution"""
    user_query: str = Field(..., description="User's original query")
    conversation_history: List[Dict[str, str]] = Field(
        default_factory=list, description="Chat history"
    )
    search_results: Optional[SearchResult] = Field(None, description="Current search results")
    actions_taken: List[AgentAction] = Field(
        default_factory=list, description="Actions performed by agent"
    )
    current_step: str = Field(..., description="Current agent step")
    is_complete: bool = Field(default=False, description="Whether the agent is done")
    error: Optional[str] = Field(None, description="Any error encountered")
