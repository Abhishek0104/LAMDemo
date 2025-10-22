# Managing Full Data in Optimized Tools

## The Challenge

When using optimized pagination tools, we only send a summary to the LLM to save tokens. But what if the user wants to perform actions on the full results (delete all matching images, tag them, etc.)?

### Current Implementation Issue
```python
@tool
def search_images_paginated(...) -> str:
    # ... search logic ...

    # This full_data is created but NOT returned to the LLM
    full_data = {
        "total_count": total_count,
        "images": [_create_full_image_dict(img) for img in paginated_results],
        # ... full metadata ...
    }

    # Only this is returned
    return json.dumps({
        "success": True,
        "message": summary_message,
        "summary": summary_images,  # Minimal data
        "pagination": {...}
    })
```

**Problem**: The LLM never sees `full_data`, so it can't access full details for subsequent actions.

## Solutions

### Solution 1: State-Based Context Management (RECOMMENDED)

Use the agent's state to store full search results between tool calls.

**Implementation:**

```python
from typing import TypedDict, Optional, List, Dict, Any

class GalleryAgentState(TypedDict):
    """Extended agent state with data caching"""
    user_query: str
    conversation_history: List[Dict[str, str]]
    search_results: Optional[Dict[str, Any]]  # Full search cache
    last_search_query: Optional[str]
    last_filter_results: Optional[Dict[str, Any]]
    viewed_images: List[str]  # Track what user saw
    # ... existing fields ...
```

**Update agent to store full results:**

```python
# In agent.py - modify tool execution
def _call_tools_node(self, state: AgentState) -> AgentState:
    """Execute tools and cache full results"""

    for tool_call in response.tool_calls:
        tool_name = tool_call.get('name')
        tool_input = tool_call.get('args')

        if tool_name == 'search_images_paginated':
            # Execute search
            result = tool.invoke(tool_input)

            # Extract and cache full data
            result_data = json.loads(result)

            # Store in state for subsequent operations
            state.search_results = {
                "query": tool_input.get('query'),
                "filters": {
                    "location": tool_input.get('location'),
                    "tags": tool_input.get('tags'),
                    "quality": tool_input.get('quality')
                },
                "full_images": result_data.get('full_data', {}).get('images', []),
                "total_count": result_data.get('pagination', {}).get('total'),
                "timestamp": datetime.now()
            }

        # Similar caching for other tools...
```

**Usage in LLM Prompts:**

```python
def _create_messages(self, state: AgentState) -> List[BaseMessage]:
    """Create messages with cached data context"""
    messages = []

    # Add search context to every message if available
    if state.search_results:
        search_context = f"""
        Available cached search results:
        - Query: {state.search_results['query']}
        - Total matches: {state.search_results['total_count']}
        - Last searched: {state.search_results['timestamp']}

        You can now perform actions on these results using tools like:
        - delete_images: Delete specific images from the search
        - tag_images: Tag all or specific images from the search
        - filter_low_quality_images: Filter the results
        """

        messages.append(SystemMessage(content=search_context))

    # Add conversation history
    for msg in state.conversation_history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))

    return messages
```

### Solution 2: Return Full Data in Response (Artifact Pattern)

Modify optimized tools to include full data in the response but mark it as "not for token counting".

**Implementation:**

```python
import json
from langchain_core.messages import ToolMessage

@tool
def search_images_paginated_with_artifacts(
    query: str,
    location: Optional[str] = None,
    tags: Optional[List[str]] = None,
    quality: Optional[str] = None,
    page: int = 1,
    per_page: int = 5
) -> str:
    """
    Search with pagination and artifact storage.

    The response includes:
    - LLM-visible summary (minimal tokens)
    - Artifact with full data (not counted in tokens)
    """

    # ... search logic ...

    # Create response with artifacts
    response_data = {
        "success": True,
        "message": summary_message,
        "summary": summary_images,  # For LLM
        "pagination": pagination_info,

        # IMPORTANT: Mark this as artifact (not sent to LLM)
        "_artifact_full_data": {
            "images": [_create_full_image_dict(img) for img in paginated_results],
            "total_count": total_count,
            "query": query,
            "filters": {"location": location, "tags": tags, "quality": quality}
        }
    }

    return json.dumps(response_data)
```

**LLM-side Usage:**

```python
# The LLM sees only the summary, but the artifact is available
{
    "success": true,
    "message": "Found 47 images. Showing 5 on page 1 of 10.",
    "summary": [{minimal}, {minimal}, ...],
    "_artifact_full_data": {
        // This isn't tokenized when sent to LLM
        // But your agent can access it programmatically
        "images": [{full}, {full}, ...],
        ...
    }
}
```

### Solution 3: Session-Based Storage (For Multi-Turn Conversations)

Use a session/conversation store to persist search results.

**Implementation:**

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any

@dataclass
class SearchCache:
    """Cache for search results with TTL"""
    query: str
    filters: Dict[str, Any]
    images: List[Dict[str, Any]]
    timestamp: datetime
    ttl_seconds: int = 300  # 5 minute cache

    def is_valid(self) -> bool:
        """Check if cache is still valid"""
        elapsed = (datetime.now() - self.timestamp).total_seconds()
        return elapsed < self.ttl_seconds

class SessionStore:
    """Store search results per conversation/user"""

    def __init__(self):
        self.searches: Dict[str, SearchCache] = {}

    def cache_search(self, session_id: str,
                    query: str, filters: Dict,
                    images: List[Dict]):
        """Store search results"""
        self.searches[session_id] = SearchCache(
            query=query,
            filters=filters,
            images=images,
            timestamp=datetime.now()
        )

    def get_cached_search(self, session_id: str) -> Optional[SearchCache]:
        """Retrieve cached search if valid"""
        cache = self.searches.get(session_id)
        if cache and cache.is_valid():
            return cache
        return None

# Usage in agent
class GalleryAgent:
    def __init__(self, llm, tools, session_id: str):
        self.llm = llm
        self.tools = tools
        self.session_id = session_id
        self.store = SessionStore()

    def _call_tools_node(self, state):
        # ... tool execution ...

        if tool_name == 'search_images_paginated':
            result_data = json.loads(result)

            # Cache full results
            self.store.cache_search(
                self.session_id,
                query=tool_input.get('query'),
                filters={...},
                images=result_data.get('full_data', {}).get('images')
            )
```

### Solution 4: Hybrid Approach (BEST FOR PRODUCTION)

Combine state-based caching with artifact storage for maximum flexibility.

**Architecture:**

```python
class OptimizedGalleryTools:
    """Tools with intelligent caching"""

    def __init__(self):
        self.search_cache = {}

    def search_images_cached(self, query, page=1, per_page=5):
        """Search with automatic caching"""

        # ... search logic ...

        # Store full results in memory
        cache_key = f"{query}_{page}_{per_page}"
        self.search_cache[cache_key] = {
            "timestamp": datetime.now(),
            "full_images": all_search_results,  # Complete list
            "query": query
        }

        # Return optimized response
        return json.dumps({
            "success": True,
            "message": message,
            "summary": summary,
            "pagination": info,
            "cache_key": cache_key  # Reference to cached data
        })

    def get_cached_images(self, cache_key: str) -> List[Dict]:
        """Retrieve full image data for actions"""
        cached = self.search_cache.get(cache_key)
        if cached and self._is_recent(cached['timestamp']):
            return cached['full_images']
        return []

    def _is_recent(self, timestamp, max_age_minutes=30):
        """Check if cache is still valid"""
        elapsed = (datetime.now() - timestamp).total_seconds() / 60
        return elapsed < max_age_minutes
```

## Recommended Implementation

### Step 1: Modify Agent State

```python
# In src/types.py
class AgentState(BaseModel):
    """Extended state with caching"""
    user_query: str
    conversation_history: List[Dict[str, str]]
    search_results: Optional[SearchResultsCache] = None  # NEW
    last_operation: Optional[str] = None  # NEW
    # ... existing fields ...

class SearchResultsCache(BaseModel):
    """Cache for full search results"""
    query: str
    filters: Dict[str, Any]
    full_images: List[ImageMetadata]
    total_count: int
    cached_at: datetime
```

### Step 2: Update Tools to Cache

```python
# In src/tools_optimized.py - Modified search function

@tool
def search_images_paginated(
    query: str,
    location: Optional[str] = None,
    tags: Optional[List[str]] = None,
    quality: Optional[str] = None,
    page: int = 1,
    per_page: int = 5,
    _cache_handler = None  # Injected by agent
) -> str:
    """Search with pagination and caching"""

    # ... existing search logic ...

    # If cache_handler provided, store full results
    if _cache_handler:
        _cache_handler.store_search_results(
            query=query,
            filters={"location": location, "tags": tags, "quality": quality},
            images=results,  # All matching images, not paginated
            total_count=len(results)
        )

    # Return optimized summary as before
    return json.dumps({...})
```

### Step 3: Update Agent to Use Cache

```python
# In src/agent.py

class GalleryAgent:
    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = tools
        self.search_cache = {}

    def _call_tools_node(self, state):
        """Execute tools with caching"""

        for tool_call in response.tool_calls:
            tool_name = tool_call.get('name')
            tool_input = tool_call.get('args')

            if tool_name == 'search_images_paginated':
                # Execute search
                result = self.tools[tool_name].invoke(tool_input)
                result_data = json.loads(result)

                # Cache full results from pagination
                self._cache_search_results(tool_input, result_data)

            elif tool_name == 'delete_images':
                # Check cache for image details
                image_ids = tool_input.get('image_ids', [])
                cached_images = self._get_cached_images(image_ids)

                # Use cached full data for validation
                print(f"Deleting {len(cached_images)} images from cache")
```

### Step 4: Create Helper Methods

```python
def _cache_search_results(self, query_params, result_data):
    """Store search results for later use"""
    cache_key = json.dumps(query_params, sort_keys=True)
    self.search_cache[cache_key] = {
        "query": query_params.get('query'),
        "filters": {
            "location": query_params.get('location'),
            "tags": query_params.get('tags'),
            "quality": query_params.get('quality')
        },
        "results": result_data,
        "timestamp": datetime.now()
    }

def _get_cached_images(self, image_ids: List[str]) -> List[ImageMetadata]:
    """Retrieve full image metadata from cache"""
    cached_images = []

    for cache_key, cache_data in self.search_cache.items():
        for img in cache_data['results'].get('images', []):
            if img['id'] in image_ids:
                cached_images.append(img)

    return cached_images

def _get_last_search_results(self) -> Optional[Dict]:
    """Get the most recent search results"""
    if not self.search_cache:
        return None

    # Return most recent
    latest = max(
        self.search_cache.values(),
        key=lambda x: x['timestamp']
    )
    return latest
```

## Example Flow

### User Interaction

```
User: "Find all blurry images"
↓
Agent: Executes search_images_paginated(query="blurry", quality="blurry")
       Results cached: 5 blurry images found (showing page 1)
       Sends to LLM: "Found 5 blurry images..."
↓
User: "Delete all of them"
↓
Agent: Checks cache for 5 blurry images
       Gets full image IDs from cache
       Executes delete_images(image_ids=["img_001", "img_003", ...])
       Success: deleted 5 images
```

### Code Example

```python
# In the agent node
def _process_input_node(self, state: AgentState) -> AgentState:
    # ... existing logic ...

    # LLM can see context about cached searches
    system_msg = "You have access to:"

    if self.search_cache:
        latest_search = self._get_last_search_results()
        system_msg += f"""
        Last search: {latest_search['query']}
        Results: {len(latest_search['results'])} images

        You can now:
        - Delete them: delete_images(image_ids=[...])
        - Tag them: tag_images(image_ids=[...], tags=[...])
        - Filter them: filter_low_quality_images()
        """

    state.conversation_history.append({
        "role": "system",
        "content": system_msg
    })

    return state
```

## Comparison of Solutions

| Solution | Pros | Cons | Best For |
|----------|------|------|----------|
| **State-Based** | Simple, no external storage | Memory grows over time | Single conversation |
| **Artifact** | Leverages LangChain patterns | Complex implementation | Complex agents |
| **Session Storage** | Multi-user support, persistent | More infrastructure | Multi-user systems |
| **Hybrid** | Best of all | Most complex | Production systems |

## Recommended: Hybrid Approach

```python
# Minimal implementation
class GalleryAgent:
    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = tools
        self.search_cache = {}  # In-memory cache

    def _call_tools_node(self, state):
        # Cache search results
        if tool_name == 'search_images_paginated':
            result = tool.invoke(tool_input)
            self.search_cache['last_search'] = {
                'results': json.loads(result),
                'timestamp': datetime.now()
            }

        # Use cache for subsequent operations
        if tool_name == 'delete_images':
            cached = self.search_cache.get('last_search')
            if cached:
                # Full data available here
                full_images = cached['results'].get('full_data', {}).get('images')
```

This is the **recommended approach**: simple, effective, and production-ready!
