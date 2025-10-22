"""
LangChain Tool Definitions for Gallery Agent
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from langchain.tools import tool
from src.types import (
    ImageMetadata, SearchQuery, SearchResult, FilterResult,
    DeleteResult, ToolResult
)


# Dummy database of sample images for demonstration
SAMPLE_IMAGES = [
    ImageMetadata(
        id="img_001",
        filename="beach_sunset.jpg",
        path="/gallery/beach_sunset.jpg",
        uploaded_at=datetime(2024, 10, 15, 10, 30),
        captured_at=datetime(2024, 10, 15, 18, 45),
        location="Malibu Beach, California",
        tags=["beach", "sunset", "landscape", "nature"],
        relations=["img_002", "img_003"],
        quality="excellent",
        width=4000,
        height=3000,
        size=2500000,
    ),
    ImageMetadata(
        id="img_002",
        filename="beach_people.jpg",
        path="/gallery/beach_people.jpg",
        uploaded_at=datetime(2024, 10, 15, 10, 32),
        captured_at=datetime(2024, 10, 15, 18, 50),
        location="Malibu Beach, California",
        tags=["beach", "people", "group photo"],
        relations=["img_001", "img_003"],
        quality="good",
        width=4000,
        height=3000,
        size=2300000,
    ),
    ImageMetadata(
        id="img_003",
        filename="beach_blurry.jpg",
        path="/gallery/beach_blurry.jpg",
        uploaded_at=datetime(2024, 10, 15, 10, 35),
        captured_at=datetime(2024, 10, 15, 19, 00),
        location="Malibu Beach, California",
        tags=["beach", "blurry"],
        relations=["img_001", "img_002"],
        quality="blurry",
        width=4000,
        height=3000,
        size=2100000,
    ),
    ImageMetadata(
        id="img_004",
        filename="mountain_hike.jpg",
        path="/gallery/mountain_hike.jpg",
        uploaded_at=datetime(2024, 9, 20, 14, 15),
        captured_at=datetime(2024, 9, 20, 15, 30),
        location="Rocky Mountains, Colorado",
        tags=["mountain", "hiking", "landscape"],
        relations=["img_005"],
        quality="excellent",
        width=3840,
        height=2160,
        size=1800000,
    ),
    ImageMetadata(
        id="img_005",
        filename="mountain_selfie.jpg",
        path="/gallery/mountain_selfie.jpg",
        uploaded_at=datetime(2024, 9, 20, 14, 20),
        captured_at=datetime(2024, 9, 20, 15, 45),
        location="Rocky Mountains, Colorado",
        tags=["mountain", "selfie", "people"],
        relations=["img_004"],
        quality="good",
        width=3840,
        height=2160,
        size=1600000,
    ),
    ImageMetadata(
        id="img_006",
        filename="city_lights.jpg",
        path="/gallery/city_lights.jpg",
        uploaded_at=datetime(2024, 8, 10, 20, 45),
        captured_at=datetime(2024, 8, 10, 22, 30),
        location="New York City, New York",
        tags=["city", "night", "lights", "skyline"],
        relations=[],
        quality="excellent",
        width=5120,
        height=3200,
        size=3100000,
    ),
]


@tool
def search_images(query: str,
                  location: Optional[str] = None,
                  tags: Optional[List[str]] = None,
                  quality: Optional[str] = None,
                  limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Search for images in the gallery based on query text and metadata filters.

    Args:
        query: Text-based search query (searches filenames, tags, locations)
        location: Filter by location
        tags: Filter by tags (matches if any tag is in the image)
        quality: Filter by quality ('excellent', 'good', 'poor', 'blurry')
        limit: Maximum number of results to return

    Returns:
        Dictionary containing search results with matching images
    """
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

    # Apply limit
    if limit:
        results = results[:limit]

    search_result = SearchResult(
        images=results,
        total_count=len(results),
        query=SearchQuery(
            text=query,
            location=location,
            tags=tags,
            quality=quality,
            limit=limit
        ),
        executed_at=datetime.now()
    )

    return {
        "success": True,
        "data": search_result.model_dump(),
        "message": f"Found {len(results)} images matching the query"
    }


@tool
def filter_low_quality_images(threshold: str = "poor") -> Dict[str, Any]:
    """
    Filter and identify low-quality images in the gallery.

    Args:
        threshold: Quality threshold to consider as 'bad'
                   ('excellent', 'good', 'poor', 'blurry')

    Returns:
        Dictionary containing images removed and kept after filtering
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

    filter_result = FilterResult(
        removed=removed,
        kept=kept,
        total_processed=len(SAMPLE_IMAGES),
        criteria=f"Quality threshold: {threshold}",
        executed_at=datetime.now()
    )

    return {
        "success": True,
        "data": filter_result.model_dump(),
        "message": f"Filtered gallery: {len(removed)} images marked for removal, {len(kept)} kept"
    }


@tool
def delete_images(image_ids: List[str]) -> Dict[str, Any]:
    """
    Delete images from the gallery by their IDs.

    Args:
        image_ids: List of image IDs to delete

    Returns:
        Dictionary containing deletion results
    """
    # In a real implementation, this would actually delete files
    # For now, just return the result
    valid_ids = [img_id for img_id in image_ids if any(img.id == img_id for img in SAMPLE_IMAGES)]

    delete_result = DeleteResult(
        deleted_ids=valid_ids,
        count=len(valid_ids),
        timestamp=datetime.now()
    )

    return {
        "success": True,
        "data": delete_result.model_dump(),
        "message": f"Successfully deleted {len(valid_ids)} images"
    }


@tool
def tag_images(image_ids: List[str], tags: List[str]) -> Dict[str, Any]:
    """
    Add tags to images in the gallery.

    Args:
        image_ids: List of image IDs to tag
        tags: Tags to add to the images

    Returns:
        Dictionary containing tagging results
    """
    updated_count = 0

    for image in SAMPLE_IMAGES:
        if image.id in image_ids:
            # Add tags that don't already exist
            for tag in tags:
                if tag not in image.tags:
                    image.tags.append(tag)
            updated_count += 1

    return {
        "success": True,
        "data": {
            "updated_count": updated_count,
            "tags_added": tags,
            "image_ids": image_ids
        },
        "message": f"Successfully added tags to {updated_count} images"
    }


@tool
def analyze_image_metadata() -> Dict[str, Any]:
    """
    Analyze and provide statistics about all images in the gallery.

    Returns:
        Dictionary containing metadata analysis
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

    return {
        "success": True,
        "data": {
            "total_images": total_images,
            "quality_distribution": quality_distribution,
            "locations": list(locations),
            "total_unique_tags": len(all_tags),
            "all_tags": list(all_tags),
            "total_storage_size": total_size,
            "average_file_size": total_size // total_images if total_images > 0 else 0
        },
        "message": f"Analyzed {total_images} images in gallery"
    }


@tool
def get_related_images(image_id: str) -> Dict[str, Any]:
    """
    Get all images related to a specific image.

    Args:
        image_id: ID of the image to find relations for

    Returns:
        Dictionary containing related images
    """
    target_image = None
    for image in SAMPLE_IMAGES:
        if image.id == image_id:
            target_image = image
            break

    if not target_image:
        return {
            "success": False,
            "data": None,
            "message": f"Image {image_id} not found"
        }

    related_images = []
    for image in SAMPLE_IMAGES:
        if image.id in target_image.relations:
            related_images.append(image)

    return {
        "success": True,
        "data": {
            "source_image": target_image.model_dump(),
            "related_images": [img.model_dump() for img in related_images],
            "relation_count": len(related_images)
        },
        "message": f"Found {len(related_images)} related images"
    }


# Create a list of all tools for registration with LangChain
GALLERY_TOOLS = [
    search_images,
    filter_low_quality_images,
    delete_images,
    tag_images,
    analyze_image_metadata,
    get_related_images,
]
