"""
Usage Examples for Gallery Image Search Agent
Demonstrates various ways to use the agent and tools
"""

import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import initialize_agent
from src.tools import (
    search_images, filter_low_quality_images, delete_images,
    tag_images, analyze_image_metadata, get_related_images,
    SAMPLE_IMAGES
)
from src.types import SearchQuery
import json


def pretty_print(title: str, data: dict):
    """Pretty print results"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    print(json.dumps(data, indent=2, default=str))


def example_1_basic_search():
    """Example 1: Basic image search"""
    print("\n" + "█"*60)
    print("EXAMPLE 1: Basic Image Search")
    print("█"*60)

    # Search for beach photos
    result = search_images("beach", limit=5)

    pretty_print("Beach Photo Search", {
        "query": "beach",
        "found": result['data']['total_count'],
        "images": [
            {
                "id": img['id'],
                "filename": img['filename'],
                "tags": img['tags']
            }
            for img in result['data']['images']
        ]
    })


def example_2_filtered_search():
    """Example 2: Search with location filter"""
    print("\n" + "█"*60)
    print("EXAMPLE 2: Filtered Search")
    print("█"*60)

    # Search with multiple filters
    result = search_images(
        query="",
        location="California",
        tags=["landscape"],
        quality="excellent",
        limit=10
    )

    pretty_print("Filtered Search Results", {
        "filters": {
            "location": "California",
            "tags": ["landscape"],
            "quality": "excellent"
        },
        "found": result['data']['total_count'],
        "images": [img['filename'] for img in result['data']['images']]
    })


def example_3_quality_analysis():
    """Example 3: Analyze image quality"""
    print("\n" + "█"*60)
    print("EXAMPLE 3: Quality Analysis")
    print("█"*60)

    # Get metadata analysis
    result = analyze_image_metadata()

    pretty_print("Gallery Statistics", result['data'])


def example_4_find_blurry_images():
    """Example 4: Find and report blurry images"""
    print("\n" + "█"*60)
    print("EXAMPLE 4: Identify Blurry Images")
    print("█"*60)

    # Filter low quality images
    result = filter_low_quality_images(threshold="blurry")

    pretty_print("Low Quality Images", {
        "threshold": "blurry",
        "removed_count": len(result['data']['removed']),
        "kept_count": len(result['data']['kept']),
        "blurry_images": [
            img['filename'] for img in result['data']['removed']
        ]
    })


def example_5_tag_images():
    """Example 5: Add tags to images"""
    print("\n" + "█"*60)
    print("EXAMPLE 5: Tag Multiple Images")
    print("█"*60)

    # Tag specific images
    result = tag_images(
        image_ids=["img_001", "img_002", "img_004"],
        tags=["favorite", "best-of-2024"]
    )

    pretty_print("Tagging Result", {
        "images_updated": result['data']['updated_count'],
        "image_ids": result['data']['image_ids'],
        "tags_added": result['data']['tags_added']
    })


def example_6_find_related_images():
    """Example 6: Find related images"""
    print("\n" + "█"*60)
    print("EXAMPLE 6: Find Related Images")
    print("█"*60)

    # Get related images
    result = get_related_images("img_001")

    pretty_print("Related Images", {
        "source_image": result['data']['source_image']['filename'],
        "related_count": result['data']['relation_count'],
        "related_images": [
            img['filename'] for img in result['data']['related_images']
        ]
    })


def example_7_workflow_scenario():
    """Example 7: Real-world workflow scenario"""
    print("\n" + "█"*60)
    print("EXAMPLE 7: Real-World Scenario")
    print("█"*60)
    print("\nScenario: Clean up photo library from beach vacation")
    print("-" * 60)

    # Step 1: Search for beach photos
    print("\n1️⃣  Searching for beach photos...")
    beach_photos = search_images("beach", limit=20)
    print(f"   Found {beach_photos['data']['total_count']} beach photos")

    # Step 2: Filter for low quality
    print("\n2️⃣  Filtering for low quality images...")
    low_quality = filter_low_quality_images(threshold="poor")
    print(f"   Found {len(low_quality['data']['removed'])} poor quality images")

    # Step 3: Report findings
    print("\n3️⃣  Summary:")
    print(f"   - Total beach photos: {beach_photos['data']['total_count']}")
    print(f"   - Low quality: {len(low_quality['data']['removed'])}")
    print(f"   - Good to keep: {len(low_quality['data']['kept'])}")

    # Step 4: Tag the good ones
    good_image_ids = [img['id'] for img in low_quality['data']['kept'][:5]]
    if good_image_ids:
        print(f"\n4️⃣  Tagging {len(good_image_ids)} good photos...")
        tag_result = tag_images(good_image_ids, ["vacation", "beach"])
        print(f"   Tagged {tag_result['data']['updated_count']} images")


def example_8_agent_usage():
    """Example 8: Using the full agent with natural language"""
    print("\n" + "█"*60)
    print("EXAMPLE 8: Using the Agent")
    print("█"*60)

    try:
        print("\nInitializing agent...")
        agent = initialize_agent()

        # Sample natural language query
        query = "Find all sunset photos from beaches in excellent quality"
        print(f"\nUser Query: {query}")

        # Note: This requires GOOGLE_API_KEY to be set
        print("\n⚠️  Note: This requires GOOGLE_API_KEY environment variable")
        print("To test, run: export GOOGLE_API_KEY='your-key' && python examples.py")

    except Exception as e:
        print(f"Agent initialization note: {e}")


def example_9_direct_database_access():
    """Example 9: Direct access to sample database"""
    print("\n" + "█"*60)
    print("EXAMPLE 9: Sample Database Content")
    print("█"*60)

    print(f"\nTotal images in database: {len(SAMPLE_IMAGES)}")
    print("\nAll images:")
    for img in SAMPLE_IMAGES:
        print(f"  • {img.filename}")
        print(f"    - Location: {img.location}")
        print(f"    - Quality: {img.quality}")
        print(f"    - Tags: {', '.join(img.tags)}")
        print()


def example_10_advanced_tool_usage():
    """Example 10: Advanced tool usage patterns"""
    print("\n" + "█"*60)
    print("EXAMPLE 10: Advanced Tool Usage")
    print("█"*60)

    # Pattern 1: Chained operations
    print("\n1. Chained Operations:")
    print("   - Search → Filter → Tag")

    search_result = search_images("mountain", limit=10)
    quality_result = filter_low_quality_images("good")
    good_images = [img['id'] for img in quality_result['data']['kept']]
    tag_result = tag_images(good_images[:3], ["processed"])

    print(f"   Search found: {search_result['data']['total_count']} images")
    print(f"   Quality filter kept: {len(good_images)} images")
    print(f"   Tagged: {tag_result['data']['updated_count']} images")

    # Pattern 2: Batch analysis
    print("\n2. Batch Analysis:")
    metadata = analyze_image_metadata()
    print(f"   Total images: {metadata['data']['total_images']}")
    print(f"   Locations: {', '.join(metadata['data']['locations'])}")
    print(f"   Unique tags: {metadata['data']['total_unique_tags']}")


def run_all_examples():
    """Run all examples"""
    print("\n")
    print("╔" + "═"*58 + "╗")
    print("║" + " "*15 + "GALLERY AGENT USAGE EXAMPLES" + " "*15 + "║")
    print("╚" + "═"*58 + "╝")

    examples = [
        example_1_basic_search,
        example_2_filtered_search,
        example_3_quality_analysis,
        example_4_find_blurry_images,
        example_5_tag_images,
        example_6_find_related_images,
        example_7_workflow_scenario,
        example_8_agent_usage,
        example_9_direct_database_access,
        example_10_advanced_tool_usage,
    ]

    for i, example_func in enumerate(examples, 1):
        try:
            example_func()
        except Exception as e:
            print(f"\n❌ Error in example {i}: {str(e)}")
            import traceback
            traceback.print_exc()

    print("\n" + "═"*60)
    print("All examples completed!")
    print("═"*60)


if __name__ == "__main__":
    # Run specific example or all
    import sys

    if len(sys.argv) > 1:
        example_num = int(sys.argv[1])
        if 1 <= example_num <= 10:
            globals()[f'example_{example_num}_' + ['basic_search', 'filtered_search',
                                                      'quality_analysis', 'find_blurry_images',
                                                      'tag_images', 'find_related_images',
                                                      'workflow_scenario', 'agent_usage',
                                                      'direct_database_access',
                                                      'advanced_tool_usage'][example_num-1]]()
        else:
            print("Please specify example number 1-10")
    else:
        run_all_examples()
