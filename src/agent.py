"""
LangGraph Agent for Gallery Image Search and Management
"""

from typing import Optional, Any, Dict, List
from datetime import datetime
import json
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.tools import Tool
from src.tools_optimized import GALLERY_TOOLS_OPTIMIZED
from src.types import AgentState, AgentAction


class GalleryAgent:
    """
    LangGraph-based agent for gallery image search and management.
    Uses Gemini API through LangChain for intelligent decision making.
    """

    def __init__(self, llm, tools: Optional[List[Tool]] = None):
        """
        Initialize the gallery agent.

        Args:
            llm: LangChain LLM instance (Gemini in this case)
            tools: List of LangChain tools (defaults to GALLERY_TOOLS_OPTIMIZED)
        """
        self.llm = llm
        self.tools = tools or GALLERY_TOOLS_OPTIMIZED
        self.tool_map = {tool.name: tool for tool in self.tools}

        # Bind tools to the LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        # Search results cache for multi-step operations
        self.search_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl_minutes = 30

        # Build the LangGraph workflow
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine for the agent."""

        # Define the state graph
        workflow = StateGraph(AgentState)

        # Define nodes
        workflow.add_node("start", self._start_node)
        workflow.add_node("process_input", self._process_input_node)
        workflow.add_node("call_tools", self._call_tools_node)
        workflow.add_node("process_results", self._process_results_node)
        workflow.add_node("end", self._end_node)

        # Define edges
        workflow.add_edge("start", "process_input")
        workflow.add_conditional_edges(
            "process_input",
            self._should_call_tools,
            {
                "call_tools": "call_tools",
                "end": "end"
            }
        )
        workflow.add_edge("call_tools", "process_results")
        workflow.add_conditional_edges(
            "process_results",
            self._should_continue,
            {
                "continue": "process_input",
                "end": "end"
            }
        )
        workflow.add_edge("end", END)

        # Set entry point
        workflow.set_entry_point("start")

        return workflow.compile()

    def _start_node(self, state: AgentState) -> AgentState:
        """Initialize the agent state."""
        state.current_step = "start"
        state.conversation_history.append({
            "role": "user",
            "content": state.user_query
        })
        return state

    def _process_input_node(self, state: AgentState) -> AgentState:
        """Process user input and decide on actions."""
        state.current_step = "process_input"

        # Create messages for the LLM
        messages = self._create_messages(state)

        # Call the LLM to decide on actions
        response = self.llm_with_tools.invoke(messages)

        # Store the response
        state.conversation_history.append({
            "role": "assistant",
            "content": str(response.content) if hasattr(response, 'content') else str(response)
        })

        # Extract tool calls from response (don't store yet - will track after execution)
        if not (hasattr(response, 'tool_calls') and response.tool_calls):
            state.is_complete = True

        return state

    def _should_call_tools(self, state: AgentState) -> str:
        """Determine if we should call tools."""
        # Check if the last response has tool calls
        messages = self._create_messages(state)
        response = self.llm_with_tools.invoke(messages)

        if hasattr(response, 'tool_calls') and response.tool_calls:
            return "call_tools"
        return "end"

    def _call_tools_node(self, state: AgentState) -> AgentState:
        """Execute the tools called by the LLM."""
        state.current_step = "call_tools"

        messages = self._create_messages(state)
        response = self.llm_with_tools.invoke(messages)

        if hasattr(response, 'tool_calls'):
            tool_results = []

            for tool_call in response.tool_calls:
                tool_name = tool_call.get('name') or tool_call.get('type')
                tool_input = tool_call.get('args') or tool_call.get('input')

                if tool_name in self.tool_map:
                    try:
                        tool = self.tool_map[tool_name]
                        result = tool.invoke(tool_input)

                        # Parse result if it's a string (JSON)
                        if isinstance(result, str):
                            try:
                                result_data = json.loads(result)
                            except:
                                result_data = result
                        else:
                            result_data = result

                        # Cache search results for subsequent operations
                        if tool_name == 'search_images_paginated':
                            self._cache_search_results(tool_input, result_data)

                        # Track the executed action
                        # Map tool names to AgentAction types
                        action_type_map = {
                            'search_images_paginated': 'search',
                            'search_images': 'search',
                            'filter_low_quality_images': 'filter',
                            'delete_images': 'delete',
                            'analyze_image_metadata': 'analyze',
                            'tag_images': 'tag'
                        }
                        action_type = action_type_map.get(tool_name, 'search')
                        state.actions_taken.append(AgentAction(
                            type=action_type,
                            params={"tool": tool_name, "input": tool_input}
                        ))

                        tool_results.append({
                            "tool": tool_name,
                            "input": tool_input,
                            "output": result_data
                        })
                    except Exception as e:
                        state.error = f"Tool execution error for {tool_name}: {str(e)}"
                        tool_results.append({
                            "tool": tool_name,
                            "input": tool_input,
                            "output": {"error": str(e)}
                        })

            # Store tool results in state
            state.conversation_history.append({
                "role": "assistant",
                "content": f"Tool results: {json.dumps(tool_results, default=str)}"
            })

        return state

    def _process_results_node(self, state: AgentState) -> AgentState:
        """Process the results from tool execution."""
        state.current_step = "process_results"

        # Get the latest response from LLM with tool results
        messages = self._create_messages(state)
        response = self.llm_with_tools.invoke(messages)

        state.conversation_history.append({
            "role": "assistant",
            "content": str(response.content) if hasattr(response, 'content') else str(response)
        })

        return state

    def _should_continue(self, state: AgentState) -> str:
        """Determine if the agent should continue processing."""
        # For now, stop after processing one round of tools
        # In a more complex agent, this could loop for multi-step reasoning
        return "end"

    def _end_node(self, state: AgentState) -> AgentState:
        """Finalize the agent execution."""
        state.current_step = "end"
        state.is_complete = True
        return state

    def _cache_search_results(self, query_params: Dict[str, Any],
                             result_data: Dict[str, Any]) -> None:
        """
        Cache search results for use in subsequent operations.

        Args:
            query_params: Original search parameters
            result_data: Result data from the search tool
        """
        # Create cache key from query parameters
        cache_key = json.dumps(query_params, sort_keys=True)

        # Extract full image data if available
        full_images = result_data.get('images', [])

        self.search_cache[cache_key] = {
            "query": query_params.get('query'),
            "filters": {
                "location": query_params.get('location'),
                "tags": query_params.get('tags'),
                "quality": query_params.get('quality')
            },
            "full_images": full_images,
            "total_count": len(full_images),
            "timestamp": datetime.now(),
            "pagination": result_data.get('pagination', {})
        }

    def _get_cached_images(self, image_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Retrieve full image metadata from cache.

        Args:
            image_ids: List of image IDs to retrieve

        Returns:
            List of full image data dictionaries
        """
        cached_images = []

        for cache_entry in self.search_cache.values():
            # Check if cache is still valid
            if not self._is_cache_valid(cache_entry['timestamp']):
                continue

            for img in cache_entry['full_images']:
                if img.get('id') in image_ids:
                    cached_images.append(img)

        return cached_images

    def _get_last_search_results(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recent search results from cache.

        Returns:
            Latest search cache entry or None
        """
        if not self.search_cache:
            return None

        # Filter valid caches
        valid_caches = [
            cache for cache in self.search_cache.values()
            if self._is_cache_valid(cache['timestamp'])
        ]

        if not valid_caches:
            return None

        # Return most recent
        return max(valid_caches, key=lambda x: x['timestamp'])

    def _is_cache_valid(self, timestamp: datetime) -> bool:
        """Check if cache entry is still valid based on TTL."""
        elapsed_minutes = (datetime.now() - timestamp).total_seconds() / 60
        return elapsed_minutes < self.cache_ttl_minutes

    def _create_messages(self, state: AgentState) -> List[BaseMessage]:
        """Create message list with context about cached searches."""
        messages = []

        # Add system context about available cached searches
        last_search = self._get_last_search_results()
        if last_search:
            search_context = f"""
Note: You have access to previously searched images:
- Query: "{last_search['query']}"
- Results: {last_search['total_count']} images found
- Available filters: Location, quality, tags

You can perform actions on these images using:
- delete_images: Delete specific images from the search results
- tag_images: Add tags to images from the search results
- filter_low_quality_images: Filter by quality

Reference the image IDs from the previous search results when performing actions.
"""
            messages.append(SystemMessage(content=search_context))

        # Add conversation history
        for msg in state.conversation_history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))

        return messages

    async def invoke_async(self, user_query: str) -> AgentState:
        """
        Invoke the agent asynchronously.

        Args:
            user_query: The user's query

        Returns:
            Final agent state
        """
        initial_state = AgentState(
            user_query=user_query,
            conversation_history=[],
            search_results=None,
            actions_taken=[],
            current_step="initialized",
            is_complete=False
        )

        final_state = await self.graph.ainvoke(initial_state)
        return final_state

    def invoke(self, user_query: str) -> AgentState:
        """
        Invoke the agent synchronously.

        Args:
            user_query: The user's query

        Returns:
            Final agent state
        """
        initial_state = AgentState(
            user_query=user_query,
            conversation_history=[],
            search_results=None,
            actions_taken=[],
            current_step="initialized",
            is_complete=False
        )

        # Convert AgentState to dict for graph.invoke()
        final_state_dict = self.graph.invoke(initial_state.model_dump())

        # Convert result back to AgentState
        if isinstance(final_state_dict, dict):
            return AgentState(**final_state_dict)
        return final_state_dict

    def get_response(self) -> Optional[str]:
        """Get the final response from the agent."""
        if self.graph:
            return "Agent workflow ready for invocation"
        return None
