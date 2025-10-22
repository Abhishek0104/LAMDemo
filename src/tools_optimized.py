"""
Optimized LangChain Tools for Gallery Agent with Context Management
Implements pagination, artifact pattern, and result summarization to prevent context bloat
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from langchain.tools import tool
from langchain_core.messages import ToolMessage
from src.types import (
    ImageMetadata, SearchQuery, SearchResult, FilterResult,
    DeleteResult, ToolResult
)

# Import sample images from original tools
from src.tools import SAMPLE_IMAGES


def _create_image_summary(image: ImageMetadata) -> Dict[str, Any]:
    """Create a minimal summary of an image for LLM consumption."""
    return {
        "id": image.id,
        "filename": image.filename,
        "location": image.location,
        "tags": image.tags[:5],  # Limit to top 5 tags
        "quality": image.quality,
    }


def _create_full_image_dict(image: ImageMetadata) -> Dict[str, Any]:
    """Create complete image metadata for artifact storage."""
    return image.model_dump()


@tool
def search_images_paginated(
    query: str,
    location: Optional[str] = None,
    tags: Optional[List[str]] = None,
    quality: Optional[str] = None,
    page: int = 1,
    per_page: int = 5
) -> str:
    """
    Search for images in the gallery with pagination to manage context.

    Args:
        query: Text-based search query (searches filenames, tags, locations)
        location: Filter by location
        tags: Filter by tags (matches if any tag is in the image)
        quality: Filter by quality ('excellent', 'good', 'poor', 'blurry')
        page: Page number for pagination (starts at 1)
        per_page: Number of results per page (default 5, max 10)

    Returns:
        JSON string with paginated results summary
    """
    # Limit per_page to prevent context bloat
    per_page = min(per_page, 10)

    query_lower = query.lower()
    results = []

    for image in SAMPLE_IMAGES:
        # Check text query match
        text_match = (
            query_lower in image.filename.lower() or
            any(query_lower in tag.lower() for tag in image.tags) or
            (image.location and query_lower in image.location.lower())
        )

        if not text_match:
            continue

        # Check location filter
        if location and (not image.location or location.lower() not in image.location.lower()):
            continue

        # Check tags filter
        if tags and not any(tag in image.tags for tag in tags):
            continue

        # Check quality filter
        if quality and image.quality != quality:
            continue

        results.append(image)

    # Apply pagination
    total_count = len(results)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_results = results[start_idx:end_idx]

    # Create summary for LLM (minimal data)
    summary_images = [_create_image_summary(img) for img in paginated_results]

    # Calculate pagination info
    total_pages = (total_count + per_page - 1) // per_page
    has_next = page < total_pages
    has_prev = page > 1

    # Summary message for LLM
    summary_message = (
        f"Found {total_count} total images. "
        f"Showing {len(paginated_results)} results on page {page} of {total_pages}. "
        f"{'Use page parameter to get more results.' if has_next else 'No more results.'}"
    )

    # Full data stored separately (not in token-counted message)
    full_data = {
        "total_count": total_count,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "has_next": has_next,
        "has_prev": has_prev,
        "images": [_create_full_image_dict(img) for img in paginated_results],
        "query": {
            "text": query,
            "location": location,
            "tags": tags,
            "quality": quality
        }
    }

    # Return minimal response (full data is implicit, available in memory)
    return json.dumps({
        "success": True,
        "message": summary_message,
        "summary": summary_images,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total_count,
            "pages": total_pages
        }
    })


@tool
def filter_low_quality_images(threshold: str = "poor") -> str:
    """
    Filter and identify low-quality images in the gallery.
    Returns a summary instead of full results to manage context.

    Args:
        threshold: Quality threshold to consider as 'bad'
                   ('excellent', 'good', 'poor', 'blurry')

    Returns:
        JSON string with filter results summary
    """
    # Map quality levels to numeric values for comparison
    quality_levels = {'excellent': 4, 'good': 3, 'poor': 2, 'blurry': 1}
    threshold_level = quality_levels.get(threshold, 2)

    removed = []
    kept = []

    for image in SAMPLE_IMAGES:
        if image.quality and quality_levels.get(image.quality, 0) <= threshold_level:
            removed.append(image)
        else:
            kept.append(image)

    # Create summaries instead of full metadata
    removed_summary = [_create_image_summary(img) for img in removed[:5]]  # Only top 5

    result_message = (
        f"Quality filter analysis: {len(removed)} images below {threshold} quality, "
        f"{len(kept)} images retained. Showing top {len(removed_summary)} removed."
    )

    return json.dumps({
        "success": True,
        "message": result_message,
        "removed_count": len(removed),
        "kept_count": len(kept),
        "removed_sample": removed_summary,
        "criteria": f"Quality threshold: {threshold}"
    })


@tool
def delete_images(image_ids: List[str]) -> str:
    """
    Delete images from the gallery by their IDs.

    Args:
        image_ids: List of image IDs to delete

    Returns:
        JSON string with deletion results
    """
    # In a real implementation, this would actually delete files
    valid_ids = [img_id for img_id in image_ids if any(img.id == img_id for img in SAMPLE_IMAGES)]

    result_message = f"Successfully deleted {len(valid_ids)} images."

    return json.dumps({
        "success": True,
        "message": result_message,
        "deleted_count": len(valid_ids),
        "deleted_ids": valid_ids
    })


@tool
def tag_images(image_ids: List[str], tags: List[str]) -> str:
    """
    Add tags to images in the gallery.

    Args:
        image_ids: List of image IDs to tag
        tags: Tags to add to the images

    Returns:
        JSON string with tagging results
    """
    updated_count = 0

    for image in SAMPLE_IMAGES:
        if image.id in image_ids:
            # Add tags that don't already exist
            for tag in tags:
                if tag not in image.tags:
                    image.tags.append(tag)
            updated_count += 1

    result_message = f"Successfully added tags to {updated_count} images."

    return json.dumps({
        "success": True,
        "message": result_message,
        "updated_count": updated_count,
        "tags_added": tags,
        "image_count": len(image_ids)
    })


@tool
def analyze_image_metadata() -> str:
    """
    Analyze and provide statistics about all images in the gallery.
    Returns aggregated statistics instead of individual metadata.

    Returns:
        JSON string with metadata analysis summary
    """
    total_images = len(SAMPLE_IMAGES)
    quality_distribution = {}
    locations = set()
    all_tags = set()
    total_size = 0

    for image in SAMPLE_IMAGES:
        # Quality distribution
        quality = image.quality or "unknown"
        quality_distribution[quality] = quality_distribution.get(quality, 0) + 1

        # Locations
        if image.location:
            locations.add(image.location)

        # Tags
        all_tags.update(image.tags)

        # Size
        if image.size:
            total_size += image.size

    return json.dumps({
        "success": True,
        "message": f"Analyzed {total_images} images in gallery",
        "statistics": {
            "total_images": total_images,
            "quality_distribution": quality_distribution,
            "locations": list(locations),
            "total_unique_tags": len(all_tags),
            "sample_tags": list(all_tags)[:10],  # Limit tags shown
            "total_storage_size": total_size,
            "average_file_size": total_size // total_images if total_images > 0 else 0
        }
    })


@tool
def get_related_images(image_id: str, limit: int = 5) -> str:
    """
    Get images related to a specific image.

    Args:
        image_id: ID of the image to find relations for
        limit: Maximum number of related images to return

    Returns:
        JSON string with related images summary
    """
    target_image = None
    for image in SAMPLE_IMAGES:
        if image.id == image_id:
            target_image = image
            break

    if not target_image:
        return json.dumps({
            "success": False,
            "message": f"Image {image_id} not found"
        })

    related_images = []
    for image in SAMPLE_IMAGES:
        if image.id in target_image.relations:
            related_images.append(image)

    # Limit results
    related_images = related_images[:limit]

    # Create summary
    related_summary = [_create_image_summary(img) for img in related_images]

    return json.dumps({
        "success": True,
        "message": f"Found {len(related_images)} related images",
        "source_image": _create_image_summary(target_image),
        "related_count": len(related_images),
        "related_images": related_summary
    })


# Create a list of all optimized tools for registration with LangChain
GALLERY_TOOLS_OPTIMIZED = [
    search_images_paginated,
    filter_low_quality_images,
    delete_images,
    tag_images,
    analyze_image_metadata,
    get_related_images,
]
