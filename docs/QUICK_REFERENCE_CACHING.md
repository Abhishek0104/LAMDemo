# Quick Reference: Full Data Caching

## The Problem & Solution

```
PROBLEM: Search returns paginated summary (5 items)
         But we need all 47 items to delete/tag them

SOLUTION: Cache stores ALL 47 in memory
          LLM sees summary (token efficient)
          Operations use full data from cache
```

## Quick Code Examples

### Basic Usage

```python
from src.main import initialize_agent

agent = initialize_agent()

# Search - full data auto-cached
agent.invoke("Find blurry images")

# Delete - uses cached data
agent.invoke("Delete all of them")
# Behind the scenes: Gets image IDs from cache, deletes them!
```

### Access Cache Directly

```python
# Get last search
cached = agent._get_last_search_results()
print(f"Found {cached['total_count']} images")
print(f"Full images available: {len(cached['full_images'])}")

# Get specific images by ID
images = agent._get_cached_images(['img_001', 'img_003'])

# Check all caches
for key, cache_data in agent.search_cache.items():
    print(f"Query: {cache_data['query']}, Results: {cache_data['total_count']}")
```

## What Gets Cached?

```python
# This is what's cached from search results:
cached_data = {
    "query": "blurry",              # Original search query
    "filters": {                    # Applied filters
        "location": None,
        "tags": None,
        "quality": "blurry"
    },
    "full_images": [               # FULL IMAGE DATA (complete objects)
        {
            "id": "img_001",
            "filename": "beach_blurry.jpg",
            "location": "Malibu",
            "tags": ["beach", "blurry"],
            "quality": "blurry"
            # ... all fields
        },
        # ... more images
    ],
    "total_count": 5,
    "timestamp": datetime.now(),   # When cached
    "pagination": {...}            # Pagination info
}
```

## Method Reference

### `_cache_search_results(query_params, result_data)`
**Purpose**: Store search results (called automatically)
**When**: After search_images_paginated execution
**Example**:
```python
agent._cache_search_results(
    {"query": "beach", "page": 1},
    {"images": [...], "pagination": {...}}
)
```

### `_get_last_search_results()`
**Purpose**: Retrieve most recent search cache
**Returns**: Dict with full_images, total_count, etc.
**Example**:
```python
cached = agent._get_last_search_results()
if cached:
    for img in cached['full_images']:
        print(img['id'])
```

### `_get_cached_images(image_ids)`
**Purpose**: Get full image data for specific IDs
**Returns**: List of matching image dicts
**Example**:
```python
images = agent._get_cached_images(['img_001', 'img_003'])
```

### `_is_cache_valid(timestamp)`
**Purpose**: Check if cache entry is still valid (not expired)
**Returns**: Boolean
**Example**:
```python
if agent._is_cache_valid(cache_data['timestamp']):
    # Use cache
```

## Common Workflows

### Search → Delete
```python
# User: "Find and delete blurry images"
agent.invoke("Find blurry images")
# Cache populated with all blurry images

agent.invoke("Delete all of them")
# Agent uses cache to get IDs and delete
```

### Search → Tag → Filter
```python
agent.invoke("Find photos from 2024")
agent.invoke("Tag them as 'archive'")        # Uses cache
agent.invoke("Show me the excellent ones")   # Uses cache
```

### Search → Analyze → Delete
```python
agent.invoke("Find photos from March")
agent.invoke("Show statistics")              # Uses cache
agent.invoke("Delete poor quality ones")     # Uses cache
```

## Cache Behavior

| Action | Result |
|--------|--------|
| Search | Cache populated automatically |
| Subsequent search | Creates new cache entry |
| Delete/Tag | Uses most recent cache |
| 30+ minutes later | Cache expires (TTL) |
| New search | New cache created |

## Customize TTL

```python
# Default: 30 minutes
agent.cache_ttl_minutes = 30

# Change to 1 hour
agent.cache_ttl_minutes = 60

# Change to 5 minutes
agent.cache_ttl_minutes = 5
```

## How LLM Uses Cache

The agent automatically adds this to the system prompt:

```
Note: You have access to previously searched images:
- Query: "blurry"
- Results: 5 images found

You can perform actions on these images using:
- delete_images
- tag_images
- filter_low_quality_images
```

So the LLM naturally understands it can operate on cached data!

## Why This Works

```
WITHOUT Caching:
  Search "blurry" → LLM sees all 47 images → 1,500+ tokens
  Delete request → Need IDs again → Re-fetch → 1,500+ tokens
  Total: 3,000+ tokens

WITH Caching:
  Search "blurry" → LLM sees summary (5 items) → 200 tokens
                 → Cache stores all 47 internally
  Delete request → Use cache for IDs → No re-fetch → 150 tokens
  Total: 350 tokens
  SAVINGS: 88%!
```

## Data Flow Diagram

```
┌─────────────────────┐
│ User: "Find blurry" │
└──────────┬──────────┘
           ↓
┌─────────────────────────────────────────┐
│ search_images_paginated executes       │
└──────────┬────────────────────┬────────┘
           ↓                    ↓
     ┌─────────────┐    ┌──────────────┐
     │ LLM Sees    │    │ Agent Caches │
     │ Summary     │    │ Full Data    │
     │ (5 items)   │    │ (47 items)   │
     │ 200 tokens  │    │ 0 tokens     │
     └─────────────┘    └──────┬───────┘
                               ↓
                        ┌─────────────────┐
                        │ Cache Storage   │
                        │ full_images: [] │
                        │ query: "blurry" │
                        │ count: 47       │
                        └────────┬────────┘
                                 ↓
           ┌─────────────────────────────────────┐
           │ User: "Delete all of them"         │
           └─────────────────┬───────────────────┘
                             ↓
           ┌─────────────────────────────────────┐
           │ Agent retrieves from cache          │
           │ Gets image IDs: [img_001, ...]     │
           │ Executes delete_images()            │
           │ 150 tokens                          │
           └─────────────────┬───────────────────┘
                             ↓
           ┌─────────────────────────────────────┐
           │ ✓ Success: Deleted 47 images        │
           └─────────────────────────────────────┘
```

## Checklist: Using Cache Effectively

- [ ] Call `agent.invoke("search query")`
- [ ] Cache is automatically populated
- [ ] Call `agent.invoke("perform action")`
- [ ] Agent uses cache for operations
- [ ] No manual cache access needed (transparent!)
- [ ] Or access manually: `agent._get_last_search_results()`

## Key Points

1. **Automatic**: Cache populated on search, no code needed
2. **Transparent**: LLM doesn't need to know about it
3. **Complete**: Full data available despite paginated display
4. **Efficient**: Huge token savings
5. **Smart**: Expires after 30 minutes (TTL)
6. **Flexible**: Multiple searches can be cached
7. **Accessible**: Direct cache access available if needed

## One-Liner Summary

> **Pagination shows LLM a summary, caching stores the full data, enabling efficient multi-step workflows!**

---

## See Also

- `MANAGING_FULL_DATA.md` - Detailed technical guide
- `FULL_DATA_CACHING_GUIDE.md` - Comprehensive guide with examples
- `example_multi_step_workflow.py` - Working code examples
- `src/agent.py` - Implementation details
