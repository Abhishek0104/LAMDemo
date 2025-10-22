# Development Guide - LAM For Gallery

Guide for developers who want to extend and customize the Gallery Image Search Agent.

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────┐
│           User Interface / Application               │
└──────────────────────┬────────────────────────────┬─┘
                       │                            │
              ┌────────▼─────────┐      ┌──────────▼────────┐
              │  LangGraph Agent  │      │  Tool Execution   │
              │  (agent.py)       │      │  (tools.py)       │
              └────────┬──────────┘      └──────────┬────────┘
                       │                            │
              ┌────────▼────────────────────────────▼────────┐
              │      Google Gemini API (ChatGoogleGenerativeAI)│
              │  - Natural Language Understanding             │
              │  - Tool Selection & Orchestration             │
              │  - Response Generation                        │
              └─────────────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────────┐
        │                                 │
    ┌───▼────┐                       ┌───▼────┐
    │Gallery  │                       │ Image  │
    │Database │                       │Storage │
    └────────┘                       └────────┘
```

## Module Descriptions

### `src/types.py`
Pydantic models for type safety and validation.

**Key Models:**
- `ImageMetadata`: Single image with all metadata
- `SearchQuery`: Search parameters
- `SearchResult`: Search results container
- `AgentState`: Agent execution state
- `FilterResult`: Filter operation results
- `DeleteResult`: Delete operation results

**Usage:**
```python
from src.types import ImageMetadata, SearchResult
image = ImageMetadata(id="img_001", filename="photo.jpg", ...)
```

### `src/tools.py`
LangChain tool definitions with dummy implementations.

**Key Components:**
- `SAMPLE_IMAGES`: Mock database
- Tool functions decorated with `@tool`
- `GALLERY_TOOLS`: List of all tools for agent

**Adding a New Tool:**
```python
@tool
def my_new_tool(param1: str) -> Dict[str, Any]:
    """Tool description."""
    # Implementation
    return {"success": True, "data": {...}, "message": "..."}

# Add to GALLERY_TOOLS list
```

### `src/agent.py`
LangGraph-based agent orchestration.

**Key Class:** `GalleryAgent`
- Initializes with LLM and tools
- Builds state graph workflow
- Manages conversation history
- Executes tool calls
- Handles errors

**Workflow Nodes:**
1. `start`: Initialize state
2. `process_input`: Get LLM decision
3. `call_tools`: Execute selected tools
4. `process_results`: Format results
5. `end`: Finalize

### `src/main.py`
Entry point and agent initialization.

**Key Function:** `initialize_agent(api_key)`
- Sets up Gemini LLM
- Creates GalleryAgent instance
- Returns ready-to-use agent

### `src/config.py`
Configuration management with environment variables.

**Key Classes:**
- `GeminiConfig`: API and LLM settings
- `AgentConfig`: Agent behavior settings
- `QualityThresholds`: Quality levels
- `ToolConfig`: Tool-specific settings
- `Messages`: Standard messages

**Usage:**
```python
from src.config import GeminiConfig, AgentConfig
print(GeminiConfig.MODEL)
print(AgentConfig.DEBUG)
```

## Extending the Agent

### Adding a New Tool

**Step 1: Create Tool Function**
```python
# In src/tools.py
@tool
def search_by_date(start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Search images within a date range.

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)

    Returns:
        Dictionary with search results
    """
    # Implementation here
    results = [img for img in SAMPLE_IMAGES if img.captured_at ...]
    return {
        "success": True,
        "data": {"images": [img.dict() for img in results]},
        "message": f"Found {len(results)} images"
    }
```

**Step 2: Register Tool**
```python
# In src/tools.py, add to GALLERY_TOOLS
GALLERY_TOOLS = [
    search_images,
    filter_low_quality_images,
    # ... existing tools
    search_by_date,  # Add new tool
]
```

**Step 3: Use in Agent**
The agent will automatically detect and use the new tool.

### Replacing Dummy Implementations

**Example: Real Database Search**

Original (dummy):
```python
@tool
def search_images(query: str, ...) -> Dict[str, Any]:
    for image in SAMPLE_IMAGES:  # Dummy data
        if query in image.filename:
            results.append(image)
```

Enhanced (real database):
```python
@tool
def search_images(query: str, ...) -> Dict[str, Any]:
    # Connect to real database
    db = get_database_connection()

    # Build query
    sql = f"SELECT * FROM images WHERE filename LIKE %s"
    results = db.execute(sql, (f"%{query}%",))

    # Return real data
    return {"success": True, "data": {...}, "message": "..."}
```

### Integrating Real Image Processing

**Example: Real Quality Assessment**

```python
from PIL import Image
import cv2
import numpy as np

@tool
def filter_low_quality_images(threshold: str = "poor") -> Dict[str, Any]:
    """Filter using real image analysis"""
    removed = []
    kept = []

    for image_path in get_all_image_paths():
        # Load image
        img = cv2.imread(image_path)

        # Calculate blur (Laplacian variance)
        laplacian_var = cv2.Laplacian(img, cv2.CV_64F).var()

        if laplacian_var < BLUR_THRESHOLD:
            removed.append(ImageMetadata(...))
        else:
            kept.append(ImageMetadata(...))

    return {
        "success": True,
        "data": {"removed": removed, "kept": kept},
        "message": f"Filtered {len(removed)} blurry images"
    }
```

## Testing and Debugging

### Running Tests

```bash
# Run all tests
python -m src.test_agent

# Run specific example
python examples.py 1
```

### Debug Mode

Enable debug logging:
```bash
export DEBUG=true
python -m src.main
```

### Testing Individual Tools

```python
from src.tools import search_images

# Test tool directly
result = search_images("beach", limit=5)
print(result)
```

### Debugging Agent State

```python
from src.main import initialize_agent

agent = initialize_agent()
result = agent.invoke("test query")

# Inspect state
print(f"Query: {result.user_query}")
print(f"History: {result.conversation_history}")
print(f"Actions: {result.actions_taken}")
print(f"Error: {result.error}")
```

## Performance Optimization

### Tool Optimization

**1. Batch Operations**
```python
# Inefficient: Multiple calls
for img_id in image_ids:
    tag_images([img_id], tags)  # Called N times

# Efficient: Single batch call
tag_images(image_ids, tags)  # Called once
```

**2. Caching**
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_image_metadata(image_id: str):
    # Cache expensive operations
    return fetch_from_database(image_id)
```

**3. Lazy Loading**
```python
# Don't load all data upfront
def search_images(query: str, limit: int = 10) -> Dict:
    # Only fetch needed results
    results = fetch_results(query, limit=limit)
    return {"data": results}
```

### Agent Optimization

**1. Single-Step vs Multi-Step**
```python
# In config.py
MULTI_STEP_REASONING = False  # Faster but less accurate
MULTI_STEP_REASONING = True   # Slower but more accurate
```

**2. Tool Selection**
```python
# Let agent choose tools smartly
# Fewer tool calls = faster execution
```

**3. Result Limiting**
```python
# User asks for search
# Use limit parameter to reduce data transfer
search_images(query, limit=10)  # Not 1000
```

## Database Integration

### Example: SQLite Integration

```python
import sqlite3
from src.types import ImageMetadata

class GalleryDatabase:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id TEXT PRIMARY KEY,
                filename TEXT,
                path TEXT,
                location TEXT,
                quality TEXT,
                uploaded_at TIMESTAMP
            )
        ''')

    def search(self, query: str, limit: int = 10):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT * FROM images WHERE filename LIKE ? LIMIT ?',
            (f"%{query}%", limit)
        )
        return cursor.fetchall()

# Update tools.py
db = GalleryDatabase("gallery.db")

@tool
def search_images(query: str, ...) -> Dict:
    results = db.search(query, limit=limit)
    return {"success": True, "data": results, "message": "..."}
```

## Deployment

### Docker

```dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV GOOGLE_API_KEY=your_key

CMD ["python", "-m", "src.main"]
```

### API Server

```python
# Create api.py
from flask import Flask, request, jsonify
from src.main import initialize_agent

app = Flask(__name__)
agent = initialize_agent()

@app.route("/search", methods=["POST"])
def search():
    query = request.json.get("query")
    result = agent.invoke(query)
    return jsonify({
        "response": result.conversation_history[-1]["content"],
        "history": result.conversation_history
    })

if __name__ == "__main__":
    app.run(debug=True)
```

## Common Issues and Solutions

### Tool Not Being Called

**Problem:** Agent doesn't use a tool you created.

**Solutions:**
1. Check tool description is clear
2. Verify tool is in GALLERY_TOOLS
3. Test tool parameter types match signature
4. Enable debug mode to see LLM reasoning

### Performance Issues

**Problem:** Agent is slow.

**Solutions:**
1. Reduce search result limits
2. Cache frequently accessed data
3. Profile tool execution time
4. Optimize database queries
5. Use single-step reasoning mode

### LLM Not Understanding Intent

**Problem:** Agent misinterprets user query.

**Solutions:**
1. Provide more context in tool descriptions
2. Use clearer tool parameter names
3. Add examples in tool docstrings
4. Adjust LLM temperature (higher = more creative)

## Best Practices

1. **Type Safety**: Always use Pydantic models
2. **Error Handling**: Return proper error messages
3. **Logging**: Add logging for debugging
4. **Documentation**: Document tool parameters clearly
5. **Testing**: Test tools independently
6. **Performance**: Monitor and optimize tool execution
7. **Security**: Validate user inputs
8. **Consistency**: Follow existing code patterns

## Code Style

### Python Style Guide
- Follow PEP 8
- Use type hints
- Write docstrings for all functions
- Use 4-space indentation

### Tool Documentation Template
```python
@tool
def tool_name(param1: str, param2: int) -> Dict[str, Any]:
    """
    Brief description of what the tool does.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Dictionary with keys:
        - success (bool): Whether operation succeeded
        - data: Result data
        - message (str): Human-readable message
    """
```

## Resources

- [LangChain Documentation](https://python.langchain.com)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Google Gemini API](https://ai.google.dev)
- [Pydantic Documentation](https://docs.pydantic.dev)

---

Happy developing! 🚀
