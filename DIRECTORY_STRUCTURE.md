# Project Directory Structure

## Overview

```
LAMForGallery/
├── src/                          # Core application code
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # Entry point - initializes agent with Gemini
│   ├── agent.py                 # LangGraph agent with caching
│   ├── types.py                 # Pydantic models and type definitions
│   ├── tools.py                 # Original gallery tools
│   ├── tools_optimized.py       # Context-optimized tools (RECOMMENDED)
│   └── config.py                # Configuration settings
│
├── docs/                         # Documentation (organized by topic)
│   ├── CONTEXT_OPTIMIZATION.md              # Token optimization guide
│   ├── CONTEXT_OPTIMIZATION_SUMMARY.md      # Implementation summary
│   ├── USING_OPTIMIZED_TOOLS.md             # How to use optimized tools
│   ├── MANAGING_FULL_DATA.md                # Full data caching guide
│   ├── FULL_DATA_CACHING_GUIDE.md          # Comprehensive caching guide
│   └── QUICK_REFERENCE_CACHING.md           # Quick reference
│
├── examples/                     # Examples and tests
│   ├── example_multi_step_workflow.py       # Multi-step workflow demo
│   ├── examples.py                          # General examples
│   ├── test_agent.py                        # Agent testing
│   └── test_context_efficiency.py           # Efficiency comparison tests
│
├── Root Documentation
│   ├── README.md                 # Main documentation
│   ├── QUICKSTART.md             # Quick start guide
│   ├── CLAUDE.md                 # Instructions for Claude Code
│   ├── DEVELOPMENT.md            # Development guidelines
│   ├── PROJECT_SUMMARY.md        # Project overview
│   ├── PROJECT_CHECKLIST.md      # Implementation checklist
│   ├── INDEX.md                  # Documentation index
│   └── ARCHITECTURE.md           # Architecture overview
│
├── Configuration Files
│   ├── .env                      # Environment variables (local, not in git)
│   ├── .env.example              # Example environment variables
│   ├── .gitignore                # Git ignore rules
│   ├── requirements.txt          # Python dependencies
│   ├── package.json              # Node.js config
│   └── tsconfig.json             # TypeScript config
│
└── .venv/                        # Virtual environment (excluded from git)
```

## Key Directories

### `src/` - Core Code

**Purpose**: Main application logic

**Key Files**:
- `main.py` - Entry point, initializes agent with Gemini API
- `agent.py` - LangGraph agent with search result caching
- `tools.py` - Original tools (reference only)
- `tools_optimized.py` - **USE THIS** - Context-efficient tools with pagination
- `types.py` - Type definitions (Pydantic models)

**When to modify**:
- Adding new tools → `tools_optimized.py`
- Changing agent logic → `agent.py`
- Adding types → `types.py`

### `docs/` - Documentation

**Purpose**: Detailed guides organized by topic

**Contents**:
- Optimization guides (context, tokens)
- Caching strategies
- Tool usage guides
- Quick references

**When to read**:
- Need token optimization → `docs/CONTEXT_OPTIMIZATION.md`
- Want to use optimized tools → `docs/USING_OPTIMIZED_TOOLS.md`
- Need caching details → `docs/FULL_DATA_CACHING_GUIDE.md`

### `examples/` - Examples and Tests

**Purpose**: Demonstration code and test scripts

**Contents**:
- `example_multi_step_workflow.py` - Multi-step agent workflows
- `test_agent.py` - Agent testing
- `test_context_efficiency.py` - Token usage comparison

**When to run**:
- Test agent locally → `python -m src.main`
- See efficiency gains → `examples/test_context_efficiency.py`
- Test tools directly → `examples/test_agent.py`

### Root Documentation

**Purpose**: High-level project documentation

**Key Files**:
- `README.md` - Start here
- `QUICKSTART.md` - Get running in 5 minutes
- `ARCHITECTURE.md` - System design
- `DEVELOPMENT.md` - Development workflow

## File Organization Rules

### Core Code (src/)
✓ Production-ready code only
✓ No test code
✓ No examples
✓ Type hints required
✓ Docstrings required

### Documentation (docs/)
✓ Detailed technical guides
✓ Topic-organized
✓ Links to code files
✓ Code examples in markdown

### Examples (examples/)
✓ Runnable Python scripts
✓ Demonstrates features
✓ Self-contained
✓ Well-commented

## What Each File Does

### Core Files

| File | Purpose | Modify When |
|------|---------|------------|
| `src/main.py` | Entry point, agent initialization | Changing Gemini model, API setup |
| `src/agent.py` | LangGraph agent, caching logic | Adding cache features, new nodes |
| `src/tools_optimized.py` | Context-efficient tools | Adding new gallery tools |
| `src/tools.py` | Original tools | Reference only, don't modify |
| `src/types.py` | Type definitions | Adding new data types |
| `src/config.py` | Configuration | Settings, constants |

### Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Overview and getting started |
| `QUICKSTART.md` | 5-minute setup guide |
| `docs/CONTEXT_OPTIMIZATION.md` | Token reduction strategies |
| `docs/FULL_DATA_CACHING_GUIDE.md` | Caching architecture |
| `ARCHITECTURE.md` | System design |
| `DEVELOPMENT.md` | Development guidelines |

## Directory Statistics

```
src/              - 6 files (main code)
docs/             - 6 files (detailed guides)
examples/         - 4 files (demo & tests)
Root docs         - 11 markdown files
```

## Key Design Decisions

### Why `docs/` Folder?
- Keeps root clean
- Easier to navigate
- Documentation organized by topic
- Can grow without cluttering root

### Why `examples/` Folder?
- Separates examples from core code
- Easy to find when needed
- Not part of main application
- Can be run independently

### Why Keep `tools.py`?
- Reference implementation
- Shows original approach (before optimization)
- Educational value
- Comparison basis

## Setup & Configuration

### Environment Variables (`.env`)
```
GOOGLE_API_KEY=your_key_here
LLM_TEMPERATURE=0.7
LLM_TOP_P=0.9
```

### Python Environment
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Common Commands

### Running the Application
```bash
cd /path/to/LAMForGallery

# Activate venv
source .venv/bin/activate

# Run main agent
python -m src.main

# Run tests
python examples/test_agent.py

# Check efficiency
python examples/test_context_efficiency.py
```

### Development
```bash
# Run with debugging
python -m src.main --debug

# Format code
black src/

# Type checking
mypy src/
```

## Navigation Guide

### "I want to..."

| Goal | File/Folder |
|------|------------|
| Understand the project | Start with `README.md` |
| Get it running quickly | Read `QUICKSTART.md` |
| Learn about optimization | Read `docs/CONTEXT_OPTIMIZATION.md` |
| Understand caching | Read `docs/FULL_DATA_CACHING_GUIDE.md` |
| Use optimized tools | Read `docs/USING_OPTIMIZED_TOOLS.md` |
| Modify the agent | Edit `src/agent.py` |
| Add a new tool | Edit `src/tools_optimized.py` |
| Run examples | Check `examples/` folder |
| Understand types | Read `src/types.py` |
| See architecture | Read `ARCHITECTURE.md` |

## Best Practices

### Code Organization
1. ✓ All core code in `src/`
2. ✓ All tools inherit from LangChain `@tool`
3. ✓ Type hints on all functions
4. ✓ Docstrings on all public methods

### Documentation
1. ✓ Detailed guides in `docs/`
2. ✓ Quick refs for common tasks
3. ✓ Links to source code
4. ✓ Code examples in markdown

### Version Control
1. ✓ `.env` not in git (use `.env.example`)
2. ✓ `.venv/` not in git
3. ✓ `__pycache__/` cleaned up
4. ✓ Large files documented

## Cleanup Status

✓ Documentation organized in `docs/`
✓ Examples moved to `examples/`
✓ Cache directories removed
✓ Hidden directories cleaned
✓ Structure documented

## Next Steps

1. Review the code in `src/`
2. Read `QUICKSTART.md` to get running
3. Explore `docs/` for detailed guides
4. Check `examples/` for code samples
5. Start building!

---

**Last Updated**: October 22, 2024
**Structure Version**: 1.0
