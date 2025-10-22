"""
Test and example usage of the Gallery Image Search Agent
"""

import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from src.main import initialize_agent
from src.tools import (
    search_images, filter_low_quality_images, delete_images,
    tag_images, analyze_image_metadata, get_related_images
)


def test_tools_directly():
    """Test individual tools directly without the agent."""
    print("\n" + "="*60)
    print("TESTING TOOLS DIRECTLY")
    print("="*60)

    # Test 1: Search images
    print("\n1. Testing search_images tool...")
    result = search_images.invoke({"query": "beach", "limit": 3})
    print(f"   Result: Found {result['data']['total_count']} images")
    for img in result['data']['images'][:2]:
        print(f"   - {img['filename']}: {img['tags']}")

    # Test 2: Analyze metadata
    print("\n2. Testing analyze_image_metadata tool...")
    result = analyze_image_metadata.invoke({})
    print(f"   Total images: {result['data']['total_images']}")
    print(f"   Quality distribution: {result['data']['quality_distribution']}")
    print(f"   Locations: {result['data']['locations']}")

    # Test 3: Filter low quality
    print("\n3. Testing filter_low_quality_images tool...")
    result = filter_low_quality_images.invoke({"threshold": "blurry"})
    print(f"   Removed: {len(result['data']['removed'])} images")
    print(f"   Kept: {len(result['data']['kept'])} images")

    # Test 4: Get related images
    print("\n4. Testing get_related_images tool...")
    result = get_related_images.invoke({"image_id": "img_001"})
    print(f"   Source: {result['data']['source_image']['filename']}")
    print(f"   Related images: {len(result['data']['related_images'])}")
    for img in result['data']['related_images']:
        print(f"   - {img['filename']}")

    # Test 5: Tag images
    print("\n5. Testing tag_images tool...")
    result = tag_images.invoke({"image_ids": ["img_001", "img_002"], "tags": ["favorite", "vacation"]})
    print(f"   Updated: {result['data']['updated_count']} images")
    print(f"   Tags added: {result['data']['tags_added']}")

    # Test 6: Delete images
    print("\n6. Testing delete_images tool...")
    result = delete_images.invoke({"image_ids": ["img_999", "img_003"]})
    print(f"   Deleted: {result['data']['count']} images")


def test_agent_with_queries():
    """Test the agent with sample queries using Google Gemini API."""
    print("\n" + "="*60)
    print("TESTING AGENT WITH QUERIES (using Google Gemini)")
    print("="*60)

    try:
        # Initialize agent with Gemini API
        print("\nInitializing agent with Google Gemini API...")
        agent = initialize_agent()
        print("✓ Agent initialized successfully")

        # Sample queries the agent can handle
        sample_queries = [
            "Find all beach photos from October 2024",
            "Show me blurry images that need cleanup",
            "What's the quality distribution of my gallery?",
        ]

        for i, query in enumerate(sample_queries, 1):
            print(f"\n{i}. Query: {query}")
            print("   Processing...")

            try:
                result = agent.invoke(query)

                print(f"   Status: {'Complete' if result.is_complete else 'In Progress'}")

                # Display conversation
                if result.conversation_history:
                    print(f"   Response:")
                    for msg in result.conversation_history:
                        if msg["role"] == "assistant":
                            content = msg["content"]
                            if len(content) > 150:
                                print(f"     {content[:150]}...")
                            else:
                                print(f"     {content}")

                if result.error:
                    print(f"   Error: {result.error}")

            except Exception as e:
                print(f"   Error processing query: {str(e)}")

    except ValueError as e:
        print(f"\n⚠ Error: {str(e)}")
        print("\nMake sure GOOGLE_API_KEY is set in the .env file")
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()


def test_tool_schemas():
    """Display the schemas of available tools."""
    print("\n" + "="*60)
    print("AVAILABLE TOOLS AND SCHEMAS")
    print("="*60)

    tools = [
        search_images,
        filter_low_quality_images,
        delete_images,
        tag_images,
        analyze_image_metadata,
        get_related_images,
    ]

    for tool in tools:
        print(f"\nTool: {tool.name}")
        print(f"Description: {tool.description}")
        if hasattr(tool, 'args'):
            print(f"Parameters:")
            for param_name, param_info in tool.args.items():
                print(f"  - {param_name}: {param_info}")


def demonstrate_workflow():
    """Demonstrate the typical workflow of the agent."""
    print("\n" + "="*60)
    print("AGENT WORKFLOW DEMONSTRATION")
    print("="*60)

    workflow_steps = [
        {
            "step": 1,
            "description": "User provides a query",
            "example": "Find all sunset photos from beaches in October"
        },
        {
            "step": 2,
            "description": "Agent understands the intent",
            "example": "Intent: Search with filters for location='beach', tags containing 'sunset', date range"
        },
        {
            "step": 3,
            "description": "Agent selects appropriate tools",
            "example": "Tool selected: search_images with parameters"
        },
        {
            "step": 4,
            "description": "Tools execute and return results",
            "example": "Results: 3 matching images found"
        },
        {
            "step": 5,
            "description": "Agent processes and formats response",
            "example": "Response: 'Found 3 sunset photos from Malibu Beach in October'"
        },
    ]

    for item in workflow_steps:
        print(f"\nStep {item['step']}: {item['description']}")
        print(f"  Example: {item['example']}")


def main():
    """Run all tests and demonstrations."""
    print("\n" + "="*80)
    print(" "*20 + "GALLERY IMAGE SEARCH AGENT - TESTS")
    print("="*80)

    # Test 1: Direct tool testing
    test_tools_directly()

    # Test 2: Tool schemas
    test_tool_schemas()

    # Test 3: Workflow demonstration
    demonstrate_workflow()

    # Test 4: Agent testing (optional - can be slow with API calls)
    # Uncomment to test with actual Gemini API
    # test_agent_with_queries()

    print("\n" + "="*80)
    print(" "*25 + "TESTS COMPLETED")
    print("="*80)
    print("\nTo test the agent with Google Gemini API, uncomment test_agent_with_queries()")
    print("Or run: python -m src.main")


if __name__ == "__main__":
    main()
