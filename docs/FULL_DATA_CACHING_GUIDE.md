# Full Data Caching Guide

## Problem Solved

**Your Question**: "How would you access the `full_data` for next action like delete images or something else?"

**The Solution**: Hybrid caching approach that automatically stores full image data while keeping the token-efficient summary in the LLM conversation.

## How It Works

### Flow Diagram

```
User Query: "Find blurry images"
    ↓
Agent executes search_images_paginated
    ↓
┌─────────────────────────────────────────────────┐
│ Result from Tool:                               │
│ ├─ Summary (5 minimal items) → Sent to LLM      │
│ └─ Full data (all results) → Cached in agent    │
└─────────────────────────────────────────────────┘
    ↓
LLM sees only summary (token efficient)
Agent stores full data (for operations)
    ↓
User: "Delete all of them"
    ↓
Agent retrieves full_data from cache
Agent calls delete_images with cached IDs
Success!
```

### Caching Implementation

**When search executes:**

```python
# In agent._call_tools_node()

if tool_name == 'search_images_paginated':
    result = tool.invoke(tool_input)  # Returns JSON with summary
    result_data = json.loads(result)

    # CRITICAL: Store full_data in cache
    self._cache_search_results(tool_input, result_data)
    #                          ↓
    #                  Full results cached!
```

**Cache structure:**

```python
self.search_cache = {
    "cache_key": {
        "query": "blurry",
        "filters": {"location": None, "tags": None, ...},
        "full_images": [  # ← Complete image metadata here
            {
                "id": "img_001",
                "filename": "beach_blurry.jpg",
                "location": "Malibu",
                "tags": ["beach", "blurry"],
                "quality": "blurry",
                # ... all fields included
            },
            # ... more images
        ],
        "total_count": 5,
        "timestamp": datetime.now(),
        "pagination": {...}
    }
}
```

## Accessing Full Data

### Method 1: Automatic System Prompt Context

The agent automatically adds cache context to system prompts:

```
Note: You have access to previously searched images:
- Query: "blurry"
- Results: 5 images found

You can perform actions on these images using:
- delete_images
- tag_images
- filter_low_quality_images
```

**Result**: The LLM naturally understands it can operate on cached images.

### Method 2: Direct Cache Access

```python
# Get last search results
agent = initialize_agent()
agent.invoke("Find beach photos")

# Access the cache
cached = agent._get_last_search_results()

# Use the full_images
if cached:
    image_ids = [img['id'] for img in cached['full_images']]
    print(f"Found images: {image_ids}")
    # Output: ['img_001', 'img_002', 'img_003']
```

### Method 3: Get Specific Images

```python
# Retrieve full data for specific image IDs
cached_images = agent._get_cached_images(['img_001', 'img_003'])

for img in cached_images:
    print(f"{img['id']}: {img['filename']} ({img['quality']})")
```

### Method 4: In a Workflow

```python
# Search
result1 = agent.invoke("Find blurry images")

# Access cache for operation
cached = agent._get_last_search_results()
if cached:
    # Get first 3 images
    to_delete = cached['full_images'][:3]
    ids = [img['id'] for img in to_delete]

    # Delete using full data from cache
    result2 = agent.invoke(f"Delete images: {', '.join(ids)}")
```

## Real-World Examples

### Example 1: Search → Delete

```python
agent = initialize_agent()

# Step 1: Search
print("Searching for blurry images...")
result = agent.invoke("Find all blurry images")

# Step 2: Agent finds 3 blurry images, caches them
print(f"Agent found: {len(agent._get_last_search_results()['full_images'])} images")

# Step 3: Delete (uses cache)
print("Deleting blurry images...")
result = agent.invoke("Delete all of them")
# The agent uses cached full_images to get IDs and delete!
```

### Example 2: Search → Filter → Tag

```python
agent = initialize_agent()

# Search for images
agent.invoke("Find photos from Colorado")
cached = agent._get_last_search_results()

# Analyze full data
excellent_quality = [
    img for img in cached['full_images']
    if img['quality'] == 'excellent'
]

print(f"Excellent quality images: {len(excellent_quality)}")

# Tag the excellent ones
excellent_ids = [img['id'] for img in excellent_quality]
agent.invoke(f"Tag these images as 'archive-ready': {excellent_ids}")
```

### Example 3: Complex Multi-Step Workflow

```python
agent = initialize_agent()

# Step 1: Analyze gallery
agent.invoke("Analyze my gallery")

# Step 2: Search for low quality
agent.invoke("Find poor quality images")
cached_poor = agent._get_last_search_results()

# Step 3: Get count from cache
poor_count = cached_poor['total_count']
print(f"Found {poor_count} poor quality images")

# Step 4: Filter options
if poor_count > 10:
    # Delete all
    agent.invoke("Delete all poor quality images")
else:
    # Review first
    image_ids = [img['id'] for img in cached_poor['full_images']]
    agent.invoke(f"Review these images for deletion: {image_ids}")
```

## Cache Management

### TTL (Time-To-Live)

```python
# Default: 30 minutes
agent.cache_ttl_minutes = 30

# Change it
agent.cache_ttl_minutes = 60  # 1 hour

# Check if cache is valid
is_valid = agent._is_cache_valid(timestamp)
```

### Multiple Searches

```python
# Each search gets its own cache entry
agent.invoke("Find beach photos")      # Cache 1
agent.invoke("Find mountain photos")   # Cache 2

# Both are accessible
print(f"Active caches: {len(agent.search_cache)}")

# Get all searches
for cache_data in agent.search_cache.values():
    print(f"Query: {cache_data['query']}, Results: {cache_data['total_count']}")
```

### Manual Cache Access

```python
# See all cached searches
print(agent.search_cache.keys())

# Get specific cache
for key, cache_data in agent.search_cache.items():
    print(f"\nCache: {cache_data['query']}")
    print(f"  Timestamp: {cache_data['timestamp']}")
    print(f"  Count: {cache_data['total_count']}")
    print(f"  Valid: {agent._is_cache_valid(cache_data['timestamp'])}")
```

## Performance Impact

### Without Caching (Naive Approach)

```
Workflow: Search → Filter → Delete

Call 1 - Search:
  LLM sees: Full 47 image details
  Tokens: ~1,500
  ├─ Pagination info
  ├─ All image metadata
  └─ Complete listings

Call 2 - Filter:
  Need to re-fetch to filter
  OR return same data again
  Tokens: ~1,500+ (duplicate data)

Call 3 - Delete:
  Need IDs, might require re-fetching
  Tokens: ~1,500+ (more duplicates)

Total: ~4,500+ tokens (inefficient!)
```

### With Hybrid Approach (Pagination + Caching)

```
Workflow: Search → Filter → Delete

Call 1 - Search:
  LLM sees: 5 minimal summaries + pagination info
  Tokens: ~200
  Cache stores: All 47 full image objects (in memory, not tokens)

Call 2 - Filter:
  LLM asks to filter
  Agent uses CACHE (no new API call)
  Tokens: ~100

Call 3 - Delete:
  LLM asks to delete
  Agent uses CACHE for IDs (no re-fetching)
  Tokens: ~80

Total: ~380 tokens (92% reduction!)
Extra: Full data available when needed
```

## Architecture Benefits

```
┌─────────────────────────────────────────────┐
│ USER                                        │
│ Query: "Find and delete blurry images"     │
└────────────┬────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────┐
│ LLM (Sees pagination summary)              │
│ "Found 5 blurry. Delete them?"             │
├─────────────────────────────────────────────┤
│ Agent Cache (Sees full data)                │
│ Store: 5 complete image objects            │
│ Access when executing actions              │
└────────────┬────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────┐
│ Tools (Execute with cache data)            │
│ delete_images(image_ids=['img_001', ...])  │
│ Uses IDs from cache, no re-fetch needed    │
└────────────┬────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────┐
│ USER SATISFACTION                          │
│ Fast, efficient, complete workflow          │
└─────────────────────────────────────────────┘
```

## Implementation Checklist

- ✓ **Agent caching added** (`src/agent.py`)
  - `_cache_search_results()` - Store results
  - `_get_cached_images()` - Retrieve by ID
  - `_get_last_search_results()` - Get most recent
  - `_is_cache_valid()` - Check TTL

- ✓ **Tool integration** (`_call_tools_node`)
  - Search results auto-cached
  - Cache available for operations
  - System prompt includes context

- ✓ **Message context** (`_create_messages`)
  - LLM informed about cache
  - Can reference cached images
  - Natural conversation flow

- ✓ **Documentation**
  - `MANAGING_FULL_DATA.md` - Technical guide
  - `FULL_DATA_CACHING_GUIDE.md` - This file
  - `example_multi_step_workflow.py` - Code examples

## Common Patterns

### Pattern 1: Conditional Delete

```python
agent.invoke("Find blurry images")
cached = agent._get_last_search_results()

if cached['total_count'] < 10:
    # Delete all
    agent.invoke("Delete them")
else:
    # Ask user
    agent.invoke("There are many. Delete first 5?")
```

### Pattern 2: Batch Operations

```python
agent.invoke("Find all tagged 'archive'")
cached = agent._get_last_search_results()

# Process in batches
batch_size = 10
for i in range(0, len(cached['full_images']), batch_size):
    batch = cached['full_images'][i:i+batch_size]
    ids = [img['id'] for img in batch]
    agent.invoke(f"Tag batch {i//batch_size + 1}: {ids}")
```

### Pattern 3: Comparative Operations

```python
agent.invoke("Find beach photos")
beach_cached = agent._get_last_search_results()

agent.invoke("Find mountain photos")
mountain_cached = agent._get_last_search_results()

# Compare
beach_ids = {img['id'] for img in beach_cached['full_images']}
mountain_ids = {img['id'] for img in mountain_cached['full_images']}

common = beach_ids & mountain_ids
print(f"Images in both categories: {len(common)}")
```

## Troubleshooting

### Issue: Cache is empty after search

**Solution**: Cache is populated automatically. Check if search tool returns data:

```python
result = agent.invoke("Find images")
print(f"Cache size: {len(agent.search_cache)}")

if not agent.search_cache:
    print("Search may have failed. Check result:")
    print(result.error)
```

### Issue: Cache expired

**Solution**: Check TTL and extend if needed:

```python
cached = agent._get_last_search_results()
if not cached:
    print("Cache expired. Searching again...")
    agent.invoke("Find images")
else:
    print("Cache still valid")
```

### Issue: Multiple searches, not sure which to use

**Solution**: Use last search or find specific one:

```python
# Most recent
latest = agent._get_last_search_results()

# Or find specific
for key, cache_data in agent.search_cache.items():
    if 'beach' in cache_data['query']:
        print(f"Found beach search: {cache_data['total_count']} images")
        break
```

## Summary

**Key Points:**
1. ✓ Full data automatically cached on search
2. ✓ Pagination keeps tokens low for LLM
3. ✓ Full data available for operations
4. ✓ No re-fetching needed
5. ✓ Multiple searches supported
6. ✓ TTL prevents stale data
7. ✓ Transparent to user
8. ✓ Significant token savings!

**Result**: The best of both worlds - efficient pagination for the LLM, complete data for operations!
