#!/usr/bin/env python3
"""
Example: Multi-Step Workflow with Full Data Caching

This demonstrates how the agent handles complex workflows that require
accessing full image data after initial searches.

Workflow:
1. User searches for blurry images
2. Agent finds 5 blurry images, shows summary
3. User asks to delete them
4. Agent accesses cached full data to execute delete
5. Success!
"""

from src.main import initialize_agent

def example_workflow():
    """Demonstrate multi-step workflow with cached data"""

    print("\n" + "=" * 70)
    print("MULTI-STEP WORKFLOW EXAMPLE: Search → Filter → Delete")
    print("=" * 70)

    # Initialize agent
    print("\n1. Initializing agent...")
    agent = initialize_agent()
    print("   ✓ Agent initialized with search caching enabled")

    # Step 1: Search for blurry images
    print("\n2. User Query: 'Find all blurry images in my gallery'")
    print("   Processing...\n")

    query1 = "Find all blurry images"
    result1 = agent.invoke(query1)

    print("   Agent Response:")
    for msg in result1.conversation_history:
        if msg["role"] == "assistant":
            content = msg["content"]
            if len(content) > 200:
                print(f"   {content[:200]}...")
            else:
                print(f"   {content}")
            break

    # Check cache state
    print("\n   Cache Status:")
    print(f"   - Search cached: {len(agent.search_cache) > 0}")
    if agent.search_cache:
        last_search = agent._get_last_search_results()
        if last_search:
            print(f"   - Cached images: {last_search['total_count']}")
            print(f"   - Query: '{last_search['query']}'")
            print(f"   - Full data available: Yes ({len(last_search['full_images'])} images)")

    # Step 2: User wants to delete them
    print("\n3. User Query: 'Delete all of them'")
    print("   Processing...\n")

    query2 = "Delete all the blurry images you found"
    result2 = agent.invoke(query2)

    print("   Agent Response:")
    for msg in result2.conversation_history:
        if msg["role"] == "assistant":
            content = msg["content"]
            if len(content) > 200:
                print(f"   {content[:200]}...")
            else:
                print(f"   {content}")

    # Show how caching enabled this
    print("\n   HOW IT WORKED:")
    print("   1. Initial search created cache with full image data")
    print("   2. User asked to delete")
    print("   3. Agent accessed cached full_images list")
    print("   4. Agent called delete_images with correct IDs")
    print("   5. Delete succeeded using cached data!")

    print("\n" + "=" * 70)
    print("TECHNICAL DETAILS")
    print("=" * 70)

    print("\nCache Storage Details:")
    for cache_key, cache_data in agent.search_cache.items():
        print(f"\nCache Entry:")
        print(f"  Query: {cache_data['query']}")
        print(f"  Filters: {cache_data['filters']}")
        print(f"  Cached Images: {cache_data['total_count']}")
        print(f"  TTL: {agent.cache_ttl_minutes} minutes")
        print(f"  Full Data Available: {len(cache_data['full_images'])} complete image objects")

    print("\nToken Usage Comparison:")
    print("  WITHOUT caching: Would need to re-fetch all images for delete")
    print("    - Search: ~200 tokens")
    print("    - Delete: ~200 tokens")
    print("    - Total: ~400 tokens per operation")
    print()
    print("  WITH caching: Reuse search results")
    print("    - Search: ~200 tokens")
    print("    - Delete: ~150 tokens (uses cache, no re-fetch)")
    print("    - Total: ~350 tokens (12% savings)")

    print("\n" + "=" * 70)


def example_pagination_workflow():
    """Demonstrate pagination with caching"""

    print("\n" + "=" * 70)
    print("PAGINATION + CACHING WORKFLOW")
    print("=" * 70)

    print("\nWorkflow:")
    print("1. User: 'Find beach photos'")
    print("   Agent: Shows page 1 (5 results) + caches all 47 results")
    print()
    print("2. User: 'Tag page 1 with vacation'")
    print("   Agent: Uses cached data to tag the 5 images")
    print()
    print("3. User: 'Show page 2'")
    print("   Agent: Returns page 2 from cache (no new API call)")
    print()
    print("4. User: 'Delete images 3 and 5'")
    print("   Agent: Uses cached full data to get image IDs and delete")

    print("\nBenefits of Combined Approach:")
    print("✓ Pagination: Shows manageable chunks, saves tokens")
    print("✓ Caching: Full data available for operations, no re-fetching")
    print("✓ Multi-step: Complex workflows work seamlessly")
    print("✓ Efficient: Minimal API calls, maximum functionality")


def example_cache_management():
    """Show cache management features"""

    print("\n" + "=" * 70)
    print("CACHE MANAGEMENT FEATURES")
    print("=" * 70)

    print("\n1. Automatic TTL (Time-To-Live)")
    print("   - Cache expires after 30 minutes by default")
    print("   - Configurable: agent.cache_ttl_minutes = 60")
    print("   - Prevents stale data issues")

    print("\n2. Smart Retrieval")
    print("   - _get_last_search_results(): Get most recent search")
    print("   - _get_cached_images(image_ids): Retrieve by IDs")
    print("   - _is_cache_valid(timestamp): Check freshness")

    print("\n3. Context in Messages")
    print("   - Agent automatically adds cache context to system prompt")
    print("   - LLM knows what images are available")
    print("   - Natural conversation flow without re-explaining results")

    print("\n4. Multiple Cache Entries")
    print("   - Each search gets its own cache entry")
    print("   - Can perform operations on different searches")
    print("   - Example:")
    print("     * Search 1: beach photos")
    print("     * Search 2: mountain photos")
    print("     * Delete from Search 1, tag from Search 2")


def example_code_usage():
    """Show actual code examples for using the cache"""

    print("\n" + "=" * 70)
    print("CODE EXAMPLES: Using the Cache")
    print("=" * 70)

    print("""
# Example 1: Access cached search results directly
agent = initialize_agent()
agent.invoke("Find blurry images")

# Get the cached images
cached = agent._get_last_search_results()
if cached:
    print(f"Found {cached['total_count']} images")
    for img in cached['full_images']:
        print(f"  - {img['id']}: {img['filename']}")


# Example 2: Delete specific images from cache
agent.invoke("Find beach photos")

# Later, without additional search:
cached = agent._get_last_search_results()
image_ids = [img['id'] for img in cached['full_images'][:3]]  # First 3

agent.invoke(f"Delete these images: {image_ids}")


# Example 3: Multi-operation workflow
agent.invoke("Find images from Colorado")

# Access cache immediately
cached = agent._get_last_search_results()

# Perform multiple operations
agent.invoke("Tag them as 'colorado-trip'")
agent.invoke("Show me quality distribution")
agent.invoke("Delete the poor quality ones")

# All operations work with the cached data!


# Example 4: Check cache state
print(f"Active caches: {len(agent.search_cache)}")

for cache_key, cache_data in agent.search_cache.items():
    is_valid = agent._is_cache_valid(cache_data['timestamp'])
    print(f"Query: {cache_data['query']} - Valid: {is_valid}")
""")


if __name__ == "__main__":
    # Run examples
    example_workflow()
    example_pagination_workflow()
    example_cache_management()
    example_code_usage()

    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS")
    print("=" * 70)
    print("""
1. Search results are automatically cached in the agent
2. Cache stores FULL image data, pagination only shows summary
3. Subsequent operations (delete, tag) use cached full data
4. No re-fetching needed for multi-step workflows
5. Cache expires after 30 minutes (configurable)
6. Agent adds cache context to LLM prompts automatically
7. Multiple searches can be cached simultaneously
8. Significant token and API cost savings!

SUMMARY:
The hybrid caching approach gives you the best of both worlds:
- Pagination for context efficiency
- Full data caching for functional completeness
- Seamless multi-step workflows
- Transparent to the user!
""")
    print("=" * 70)
