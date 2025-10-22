# Architecture - LAM For Gallery

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        User / Application                        │
│                    (CLI, Web UI, API Client)                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  Main Entry Point│
                    │  (src/main.py)   │
                    └────────┬────────┘
                             │
        ┌────────────────────┴────────────────────┐
        │                                         │
   ┌────▼──────┐                          ┌──────▼────┐
   │ Config    │                          │ Agent Init │
   │ (src/config.py)                      │ (GalleryAgent)
   └────┬──────┘                          └──────┬────┘
        │                                        │
        └────────────────┬───────────────────────┘
                         │
                ┌────────▼────────┐
                │  LangGraph Agent │
                │  (src/agent.py)  │
                │                  │
                │ State Machine:   │
                │ start →          │
                │ process_input → │
                │ call_tools →    │
                │ process_result →
                │ end              │
                └────────┬────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   ┌────▼─────┐  ┌──────▼──────┐  ┌─────▼────┐
   │ LLM Binding
   │          │  │ Tool Manager │  │ State    │
   │ (ChatGoogleGenerativeAI)  │  │ Manager  │
   │          │  │              │  │          │
   └────┬─────┘  └──────┬───────┘  └─────┬────┘
        │                │               │
        └────────────────┼───────────────┘
                         │
        ┌────────────────▼────────────────┐
        │      Tool Executor              │
        │      (src/tools.py)             │
        │                                 │
        │  ├─ search_images              │
        │  ├─ filter_low_quality         │
        │  ├─ delete_images              │
        │  ├─ tag_images                 │
        │  ├─ analyze_metadata           │
        │  └─ get_related_images         │
        │                                 │
        │  Backed by:                     │
        │  SAMPLE_IMAGES (mock db)        │
        └────────────────┬────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
   ┌────▼──────┐                   ┌─────▼────┐
   │ Return     │                   │ Error    │
   │ Results    │                   │ Handling │
   │            │                   │          │
   └────┬──────┘                   └─────┬────┘
        │                               │
        └───────────────┬───────────────┘
                        │
                ┌───────▼────────┐
                │  Result Models │
                │  (src/types.py)│
                │                │
                │ SearchResult   │
                │ FilterResult   │
                │ DeleteResult   │
                │ AgentState     │
                └────────┬───────┘
                         │
                    ┌────▼─────┐
                    │ Response  │
                    │ to User   │
                    └───────────┘
```

## Data Flow Diagram

```
User Input (Natural Language Query)
│
├─→ [Tokenization & Understanding]
│
├─→ [Intent Recognition]
│   ├─ Search intent?
│   ├─ Filter intent?
│   ├─ Delete intent?
│   ├─ Tag intent?
│   └─ Analyze intent?
│
├─→ [Tool Selection]
│   └─ LLM decides which tools to use
│       with what parameters
│
├─→ [Tool Execution]
│   ├─ search_images() if search intent
│   ├─ filter_low_quality_images() if filter
│   ├─ delete_images() if delete
│   ├─ tag_images() if tag
│   └─ analyze_image_metadata() if analyze
│
├─→ [Result Processing]
│   ├─ Type validation (Pydantic)
│   ├─ Error checking
│   └─ Result formatting
│
├─→ [Response Generation]
│   └─ LLM creates human-readable response
│
└─→ User Response

```

## Component Interaction Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                      LANGCHAIN/LANGGRAPH                         │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐│
│  │               State Management (AgentState)                 ││
│  │                                                             ││
│  │  user_query                                                 ││
│  │  conversation_history ←────────────────────────────────────┐││
│  │  search_results                                            │││
│  │  actions_taken                                             │││
│  │  current_step                                              │││
│  │  is_complete                                               │││
│  │  error                                                     │││
│  └────────────────────────────────────────────────────────────┘││
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐│
│  │              Workflow Orchestration (LangGraph)             ││
│  │                                                             ││
│  │  Graph Structure:                                           ││
│  │                                                             ││
│  │    START                                                    ││
│  │     │                                                       ││
│  │     ├─→ PROCESS_INPUT (LLM: "What tools do I need?")     ││
│  │     │                                                       ││
│  │     ├─→ [Decision: Need tools?]                            ││
│  │     │        │                                              ││
│  │     │        ├─→ YES: CALL_TOOLS                           ││
│  │     │        │         │                                   ││
│  │     │        │         ├─→ PROCESS_RESULTS                ││
│  │     │        │         │         │                         ││
│  │     │        │         │         └─→ [Decision: Continue?]││
│  │     │        │         │              │                    ││
│  │     │        │         │              ├─→ YES: loop back  ││
│  │     │        │         │              └─→ NO: END         ││
│  │     │        │                                              ││
│  │     │        └─→ NO: END                                    ││
│  │     │                                                       ││
│  │     └─→ END → Return AgentState                            ││
│  │                                                             ││
│  └────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐│
│  │          Tool Binding (ChatGoogleGenerativeAI)              ││
│  │                                                             ││
│  │  Registered Tools:                                          ││
│  │  - search_images()                                         ││
│  │  - filter_low_quality_images()                             ││
│  │  - delete_images()                                         ││
│  │  - tag_images()                                            ││
│  │  - analyze_image_metadata()                                ││
│  │  - get_related_images()                                    ││
│  │                                                             ││
│  │  LLM knows:                                                 ││
│  │  - Tool names                                              ││
│  │  - Tool descriptions                                       ││
│  │  - Parameter names and types                               ││
│  │  - Return value formats                                    ││
│  │                                                             ││
│  └────────────────────────────────────────────────────────────┘│
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│                    TOOLS EXECUTION LAYER                         │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Search Tool                                             │  │
│  │  ├─ Input: query, location, tags, quality, limit        │  │
│  │  ├─ Logic: Filter SAMPLE_IMAGES                         │  │
│  │  └─ Output: SearchResult (images, total_count, query)  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Filter Tool                                             │  │
│  │  ├─ Input: threshold                                     │  │
│  │  ├─ Logic: Compare quality_score with threshold         │  │
│  │  └─ Output: FilterResult (removed, kept, criteria)      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Delete Tool                                             │  │
│  │  ├─ Input: image_ids                                     │  │
│  │  ├─ Logic: Mark images for deletion                      │  │
│  │  └─ Output: DeleteResult (deleted_ids, count)           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Tag Tool                                                │  │
│  │  ├─ Input: image_ids, tags                               │  │
│  │  ├─ Logic: Add tags to images                            │  │
│  │  └─ Output: ToolResult (updated_count, tags)            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Analyze Tool                                            │  │
│  │  ├─ Input: none                                          │  │
│  │  ├─ Logic: Aggregate stats from SAMPLE_IMAGES           │  │
│  │  └─ Output: Statistics (counts, distributions, etc)     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Relations Tool                                          │  │
│  │  ├─ Input: image_id                                      │  │
│  │  ├─ Logic: Find related images                           │  │
│  │  └─ Output: Related images list                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Pydantic Models (Type Safety & Validation)              │  │
│  │                                                           │  │
│  │  ImageMetadata                                            │  │
│  │  ├─ id, filename, path                                   │  │
│  │  ├─ uploaded_at, captured_at                             │  │
│  │  ├─ location, tags, relations                            │  │
│  │  └─ quality, dimensions, size                            │  │
│  │                                                           │  │
│  │  SearchResult                                             │  │
│  │  ├─ images: List[ImageMetadata]                          │  │
│  │  ├─ total_count: int                                     │  │
│  │  └─ query: SearchQuery                                   │  │
│  │                                                           │  │
│  │  FilterResult, DeleteResult, etc.                        │  │
│  │                                                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Sample Data (SAMPLE_IMAGES)                             │  │
│  │  ├─ img_001: beach_sunset.jpg                            │  │
│  │  ├─ img_002: beach_people.jpg                            │  │
│  │  ├─ img_003: beach_blurry.jpg                            │  │
│  │  ├─ img_004: mountain_hike.jpg                           │  │
│  │  ├─ img_005: mountain_selfie.jpg                         │  │
│  │  └─ img_006: city_lights.jpg                             │  │
│  │                                                           │  │
│  │  Real Implementation:                                     │  │
│  │  → Replace with database queries (SQLite, PostgreSQL)   │  │
│  │  → Use ORM (SQLAlchemy, Tortoise)                        │  │
│  │  → Connect to cloud storage (S3, GCS)                    │  │
│  │                                                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## Type System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Pydantic Type System (src/types.py)             │
│                                                              │
│  Input Models                                               │
│  ├─ SearchQuery                                             │
│  │  ├─ text: Optional[str]                                 │
│  │  ├─ date_range: Optional[DateRange]                     │
│  │  ├─ location: Optional[str]                             │
│  │  ├─ tags: Optional[List[str]]                           │
│  │  ├─ quality: Optional[Literal[...]]                     │
│  │  └─ limit: Optional[int]                                │
│  │                                                          │
│  Core Models                                                │
│  ├─ ImageMetadata (Full image information)                │
│  ├─ AgentState (Agent execution state)                    │
│  ├─ AgentAction (Action tracking)                         │
│  │                                                          │
│  Output Models                                              │
│  ├─ SearchResult                                            │
│  ├─ FilterResult                                            │
│  ├─ DeleteResult                                            │
│  ├─ ToolResult                                              │
│  │                                                          │
│  Validation Benefits                                        │
│  ├─ Runtime type checking                                   │
│  ├─ Automatic type conversion                              │
│  ├─ Detailed error messages                                │
│  ├─ JSON serialization/deserialization                     │
│  └─ IDE autocompletion support                             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Configuration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│         Configuration System (src/config.py)                │
│                                                              │
│  Environment Variables (.env)                              │
│  ├─ GOOGLE_API_KEY                                         │
│  ├─ GEMINI_MODEL (default: gemini-pro)                     │
│  ├─ LLM_TEMPERATURE (default: 0.7)                         │
│  ├─ LLM_TOP_P (default: 0.9)                               │
│  ├─ LLM_TOP_K (default: 40)                                │
│  └─ ... more options                                        │
│                                                              │
│  Config Classes                                             │
│  ├─ GeminiConfig                                            │
│  │  └─ Loads API and LLM parameters                        │
│  │                                                          │
│  ├─ AgentConfig                                             │
│  │  └─ Loads agent behavior settings                       │
│  │                                                          │
│  ├─ QualityThresholds                                       │
│  │  └─ Defines quality levels and scores                   │
│  │                                                          │
│  ├─ ToolConfig                                              │
│  │  └─ Tool-specific settings                              │
│  │                                                          │
│  └─ Messages                                                │
│     └─ Standard messages throughout app                    │
│                                                              │
│  Validation                                                 │
│  └─ validate_config() checks completeness                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Class Hierarchy

```
BaseModel (Pydantic)
├── ImageMetadata
├── SearchQuery
├── SearchResult
├── FilterResult
├── DeleteResult
├── AgentAction
├── ToolResult
└── AgentState

Tool (LangChain)
├── search_images
├── filter_low_quality_images
├── delete_images
├── tag_images
├── analyze_image_metadata
└── get_related_images

GalleryAgent
├── llm: ChatGoogleGenerativeAI
├── tools: List[Tool]
├── graph: StateGraph (LangGraph)
├── invoke() → AgentState
└── invoke_async() → AgentState (async)
```

## Execution Flow

```
1. User provides natural language query
   ↓
2. Agent.invoke(query) called
   ↓
3. Initial AgentState created
   ↓
4. State machine enters START node
   ↓
5. PROCESS_INPUT: Query sent to Gemini with tool definitions
   ↓
6. Gemini understands intent and selects tools
   ↓
7. Decision: Tools needed?
   ├─ NO → Jump to END node
   └─ YES → Continue to CALL_TOOLS node
   ↓
8. CALL_TOOLS: Execute selected tools with parameters
   ↓
9. Tools return results (SearchResult, FilterResult, etc.)
   ↓
10. PROCESS_RESULTS: Gemini processes tool outputs
   ↓
11. Decision: Continue reasoning?
    ├─ YES → Back to PROCESS_INPUT (multi-step)
    └─ NO → Jump to END node
   ↓
12. END: Finalize state
   ↓
13. Return AgentState with conversation history
   ↓
14. User receives final response with all interactions
```

## Technology Stack

```
┌─────────────────────────────────────────────────────────────┐
│                   Technology Stack                          │
│                                                              │
│  Runtime & Language                                         │
│  └─ Python 3.8+                                             │
│                                                              │
│  ML/AI Frameworks                                           │
│  ├─ LangChain (0.1.13)                                      │
│  ├─ LangGraph (0.0.45)                                      │
│  └─ Google Generative AI (0.3.5)                            │
│                                                              │
│  Data Validation & Serialization                            │
│  └─ Pydantic (2.5.0)                                        │
│                                                              │
│  Utilities                                                   │
│  └─ python-dotenv (1.0.0)                                  │
│                                                              │
│  External APIs                                              │
│  └─ Google Gemini API (Cloud)                               │
│                                                              │
│  Future Integration Possibilities                           │
│  ├─ PostgreSQL / SQLite (Database)                          │
│  ├─ OpenCV / PIL (Image Processing)                         │
│  ├─ FastAPI / Flask (Web Framework)                         │
│  ├─ Docker (Containerization)                               │
│  └─ Redis (Caching)                                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

This architecture is designed for:
- ✅ **Scalability**: Easy to add new tools and features
- ✅ **Maintainability**: Clear separation of concerns
- ✅ **Type Safety**: Full type hints and validation
- ✅ **Extensibility**: Modular components
- ✅ **Performance**: Efficient tool selection and execution
- ✅ **Reliability**: Error handling at each layer
