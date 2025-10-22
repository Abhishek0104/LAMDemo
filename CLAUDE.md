# CLAUDE.md - Development Guide

Guidance for Claude Code when working on this Gallery Agent project.

## Quick Start

```bash
# Activate environment
source .venv/bin/activate

# Run agent with Gemini API
python -m src.main

# Run tests
python examples/test_agent.py

# Check token efficiency
python examples/test_context_efficiency.py
```

## Project Overview

**Gallery Image Search Agent** - LLM-powered agent using:
- **LangChain**: Tool definitions and orchestration
- **LangGraph**: Agentic workflow orchestration
- **Google Gemini 2.5-flash**: LLM backend
- **Hybrid Optimization**: Pagination (tokens) + Caching (data)

## Build & Test Commands

```bash
# Format code
black src/

# Type checking
mypy src/

# Run main application
python -m src.main

# Run tool tests
python examples/test_agent.py

# Performance analysis
python examples/test_context_efficiency.py
```

## Architecture Overview

### High-Level Flow
```
User Query
    ↓
Gemini LLM (sees summary only, ~200 tokens)
    ↓
Agent (stores full data in cache)
    ↓
Tools (execute with cached data, no re-fetch)
    ↓
Result (efficient and complete)
```

### Core Components

| Component | File | Purpose |
|-----------|------|---------|
| **Agent** | `src/agent.py` | LangGraph orchestration + caching |
| **Tools** | `src/tools_optimized.py` | Gallery operations (search, delete, tag) |
| **LLM** | `src/main.py` | Gemini initialization |
| **Types** | `src/types.py` | Pydantic data models |

### Key Design Patterns

1. **Pagination Pattern**: Search returns paginated summary to LLM
2. **Caching Pattern**: Full data cached internally for operations
3. **State Management**: Cache stored in agent, auto-managed
4. **Context Injection**: Cache context added to system prompt

## Directory Structure

```
src/                 - Production code
docs/               - Detailed documentation (6 guides)
examples/           - Runnable examples and tests
```

See `DIRECTORY_STRUCTURE.md` for complete layout.

## Key Development Workflows

### Adding a New Tool

1. Open `src/tools_optimized.py`
2. Create function with `@tool` decorator
3. Return JSON: `{"success": bool, "message": str, ...}`
4. Add to `GALLERY_TOOLS_OPTIMIZED` list
5. Test with `examples/test_agent.py`

Example:
```python
@tool
def my_new_tool(param: str) -> str:
    """Tool description for LLM."""
    # Implementation
    return json.dumps({
        "success": True,
        "message": "Result summary",
        "data": {...}
    })
```

### Modifying Agent Logic

1. Edit `src/agent.py`
2. Update relevant node function
3. Run tests: `python examples/test_agent.py`
4. Check tokens: `python examples/test_context_efficiency.py`

### Debugging Agent

```python
# Check cache state
agent = initialize_agent()
agent.invoke("Find images")
print(f"Cache: {len(agent.search_cache)}")

# Get cached results
cached = agent._get_last_search_results()
print(f"Found: {cached['total_count']} images")

# Access specific images
images = agent._get_cached_images(['img_001'])
```

## Setup and Prerequisites

### Requirements
- Python 3.9+
- Google Gemini API key
- LangChain + LangGraph

### Environment Setup

```bash
# Copy template
cp .env.example .env

# Add your API key
echo "GOOGLE_API_KEY=your_key_here" >> .env

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

**`.env` Variables**:
```
GOOGLE_API_KEY=<your gemini api key>
LLM_TEMPERATURE=0.7
LLM_TOP_P=0.9
LLM_TOP_K=40
```

## Code Standards

- ✓ Type hints required on all functions
- ✓ Docstrings on public methods
- ✓ JSON string return format for tools
- ✓ Comprehensive error handling
- ✓ Cache validation on TTL

## Performance Metrics

| Operation | Tokens | Time |
|-----------|--------|------|
| Single search | ~200 | <1s |
| Multi-operation workflow | ~350-400 | ~3-5s |
| Cache retrieval | 0 (cached) | <100ms |
| **Overall savings** | **88%** | **Fast** |

## Important Files

| File | What | Edit When |
|------|------|-----------|
| `src/agent.py` | Agent logic + caching | Adding cache features |
| `src/tools_optimized.py` | Gallery tools | Adding new tools |
| `src/main.py` | LLM init | Changing model |
| `src/types.py` | Data types | New data structures |
| `docs/` | Guides | Documenting features |

## Testing & Debugging

### Quick Tests
```bash
# Test tools directly
python examples/test_agent.py

# Check efficiency gains
python examples/test_context_efficiency.py

# Run full workflow
python -m src.main
```

### Debug Checklist

- [ ] `.env` file exists with API key
- [ ] Virtual environment activated
- [ ] All dependencies installed
- [ ] No syntax errors
- [ ] Type hints valid
- [ ] Docstrings present

## Common Issues

| Issue | Solution |
|-------|----------|
| "Model not found" | Check Gemini model name in `src/main.py` |
| Empty cache | Verify search executed successfully |
| High token usage | Using original tools? Switch to optimized |
| Cache expired | Increase `cache_ttl_minutes` if needed |

## Documentation Structure

- `README.md` - Start here
- `QUICKSTART.md` - 5-minute setup
- `DIRECTORY_STRUCTURE.md` - File organization
- `ARCHITECTURE.md` - System design
- `docs/CONTEXT_OPTIMIZATION.md` - Token optimization
- `docs/FULL_DATA_CACHING_GUIDE.md` - Caching architecture
- `docs/USING_OPTIMIZED_TOOLS.md` - Tool usage guide

## Git Workflow

### Before Committing
- [ ] Format with `black src/`
- [ ] Add type hints
- [ ] Write docstrings
- [ ] Pass tests
- [ ] Don't commit `.env`
- [ ] Clean `__pycache__`

### Files Never Commit
- `.env` (use `.env.example`)
- `.venv/` (virtual env)
- `__pycache__/` (Python cache)
- `.pyc` files

## Resources

- **LangChain**: https://python.langchain.com
- **LangGraph**: https://langchain-ai.github.io/langgraph
- **Gemini API**: https://ai.google.dev
- **This Project**: See `docs/` folder

## Version Info

- **Python**: 3.9+
- **LangChain**: Latest
- **Status**: Production Ready
- **Last Updated**: October 22, 2024
