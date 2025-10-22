# Quick Start Guide - LAM For Gallery

Get up and running with the Gallery Image Search Agent in 5 minutes.

## 1. Prerequisites

- Python 3.8 or higher
- Google Gemini API key (free tier available at [ai.google.dev](https://ai.google.dev))

## 2. Setup

### Step 1: Install Dependencies
```bash
cd LAMForGallery
pip install -r requirements.txt
```

### Step 2: Configure API Key
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Gemini API key
# GOOGLE_API_KEY=your_actual_api_key_here
```

Or set as environment variable:
```bash
export GOOGLE_API_KEY="your_api_key_here"
```

## 3. Run Examples

### Option A: Run Agent with Sample Queries
```bash
python -m src.main
```

This will demonstrate the agent processing sample gallery queries.

### Option B: Test Tools Directly
```bash
python -m src.test_agent
```

This showcases:
- Individual tool functionality
- Tool schemas
- Agent workflow
- Available capabilities

## 4. Use in Your Code

```python
from src.main import initialize_agent

# Initialize agent
agent = initialize_agent()

# Ask a question
result = agent.invoke("Find all beach photos from October 2024")

# Print results
for msg in result.conversation_history:
    print(f"{msg['role'].upper()}: {msg['content']}")
```

## 5. Available Tools

| Tool | Purpose |
|------|---------|
| `search_images` | Search with natural language and filters |
| `filter_low_quality_images` | Find blurry or poor quality images |
| `delete_images` | Remove images by ID |
| `tag_images` | Add tags to multiple images |
| `analyze_image_metadata` | Get gallery statistics |
| `get_related_images` | Find related images |

## 6. Example Queries

Try these natural language queries:

```
"Find all sunset photos from beaches"
"Show me blurry images"
"How many photos do I have from Colorado?"
"Delete all poor quality images"
"Tag all mountain photos with hiking"
"What's the quality distribution of my gallery?"
```

## 7. Project Structure

```
src/
├── types.py      → Data models (ImageMetadata, SearchResult, etc.)
├── tools.py      → Tool definitions (search, filter, delete, etc.)
├── agent.py      → LangGraph agent implementation
└── main.py       → Initialization and entry point
```

## 8. Next Steps

### Integrate Real Data
Replace `SAMPLE_IMAGES` in `src/tools.py` with:
- Database queries (SQLite, PostgreSQL, MongoDB)
- File system scanning
- Cloud storage APIs

### Enhance Tools
Implement real functionality for:
- Image quality detection (OpenCV, PIL)
- Similarity search (embeddings)
- Batch operations
- Advanced filtering

### Deploy
- Create Flask/FastAPI endpoints
- Containerize with Docker
- Deploy to cloud (GCP, AWS, Heroku)

## 9. Troubleshooting

**Q: "GOOGLE_API_KEY not found"**
- Ensure .env file exists with `GOOGLE_API_KEY=your_key`
- Or set environment variable: `export GOOGLE_API_KEY="..."`

**Q: "Module not found"**
- Run: `pip install -r requirements.txt`
- Ensure you're in the project directory

**Q: "Agent not using tools"**
- Check API key is valid
- Review error in `result.error`
- Test tool directly: `python -c "from src.tools import search_images; print(search_images('beach'))"`

## 10. Key Features

✅ **Natural Language Search** - Ask in plain English
✅ **Multiple Filters** - Date, location, tags, quality
✅ **Intelligent Agent** - Uses Gemini to understand intent
✅ **Tool Integration** - 6 built-in gallery tools
✅ **Extensible** - Easy to add new tools
✅ **Type Safe** - Pydantic models for validation
✅ **Error Handling** - Graceful error management

## 11. API Reference Quick Lookup

### search_images
```python
search_images(
    query="beach",
    location="California",
    tags=["sunset"],
    quality="excellent",
    limit=10
)
```

### filter_low_quality_images
```python
filter_low_quality_images(threshold="blurry")
```

### delete_images
```python
delete_images(image_ids=["img_001", "img_002"])
```

### tag_images
```python
tag_images(
    image_ids=["img_001"],
    tags=["favorite", "vacation"]
)
```

### analyze_image_metadata
```python
analyze_image_metadata()
```

### get_related_images
```python
get_related_images(image_id="img_001")
```

## 12. Architecture Overview

```
User Query
    ↓
[Gemini LLM] ← understands intent
    ↓
[Tool Selection] ← decides which tools to use
    ↓
[Tool Execution] ← runs selected tools
    ↓
[Result Processing] ← formats response
    ↓
Response to User
```

## Need Help?

- Check full documentation in [Readme.md](./Readme.md)
- Review tool definitions in [src/tools.py](./src/tools.py)
- See examples in [src/test_agent.py](./src/test_agent.py)
- Run tests with `python -m src.test_agent`

---

Happy searching! 🎨📷
