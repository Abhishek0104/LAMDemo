"""
Streamlit Frontend for Gallery Image Search Agent
A ChatGPT-like interface with image gallery display
"""

import streamlit as st
import json
from datetime import datetime
from src.main import initialize_agent
from PIL import Image
import io

# Page configuration
st.set_page_config(
    page_title="Gallery Search Agent",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .message-container {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #E3F2FD;
        border-left: 4px solid #2196F3;
    }
    .assistant-message {
        background-color: #F5F5F5;
        border-left: 4px solid #757575;
    }
    .image-gallery {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 1rem;
        padding: 1rem;
    }
    .stat-card {
        background-color: #F0F2F5;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# Session state initialization
if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.agent = None
    st.session_state.cache_info = None

# Initialize agent
@st.cache_resource
def load_agent():
    """Load and cache the agent"""
    try:
        agent = initialize_agent()
        return agent
    except Exception as e:
        st.error(f"Failed to initialize agent: {str(e)}")
        return None

# Sidebar configuration
with st.sidebar:
    st.title("⚙️ Gallery Agent Settings")

    st.markdown("---")

    # Model information
    st.subheader("Model Info")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Model", "Gemini 2.5")
    with col2:
        st.metric("Status", "🟢 Active")

    st.markdown("---")

    # Cache statistics
    st.subheader("Cache Statistics")
    if st.session_state.agent:
        cache_size = len(st.session_state.agent.search_cache) if st.session_state.agent else 0
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Cached Searches", cache_size)
        with col2:
            st.metric("TTL (minutes)", st.session_state.agent.cache_ttl_minutes if st.session_state.agent else 30)
        with col3:
            st.metric("Messages", len(st.session_state.messages))

    st.markdown("---")

    # Clear conversation button
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    # Settings
    st.subheader("Settings")
    show_cache_info = st.checkbox("Show cache details", value=False)
    auto_scroll = st.checkbox("Auto-scroll to latest", value=True)

    st.markdown("---")

    # Help section
    st.subheader("❓ Quick Help")
    with st.expander("How to use"):
        st.markdown("""
        1. **Search Images**: Ask to find images by description
           - "Find beach photos"
           - "Show me sunset images"

        2. **Filter Results**: Narrow down results
           - "Show only excellent quality"
           - "From Colorado location"

        3. **Perform Actions**: Delete or tag images
           - "Delete all blurry images"
           - "Tag these as favorites"

        4. **Get Statistics**: Analyze your gallery
           - "Show me quality distribution"
           - "How many images total?"
        """)

    with st.expander("Features"):
        st.markdown("""
        ✅ Real-time image search
        ✅ Context-optimized (88% token savings)
        ✅ Smart caching for operations
        ✅ Multi-step workflows
        ✅ Gallery display
        """)

# Main chat interface
st.title("🖼️ Gallery Image Search Agent")
st.markdown("*ChatGPT-like interface for intelligent image gallery management*")

st.markdown("---")

# Load agent
agent = load_agent()
if not agent:
    st.error("❌ Failed to initialize agent. Check your API key and configuration.")
    st.stop()

# Display conversation history
st.subheader("💬 Conversation")

# Message display container
message_container = st.container()

with message_container:
    for i, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant"):
                # Display message content
                st.markdown(message["content"])

                # Display images if available
                if "images" in message and message["images"]:
                    st.subheader("📸 Images Found")

                    # Create columns for image gallery
                    cols = st.columns(3)
                    for idx, img_data in enumerate(message["images"]):
                        col = cols[idx % 3]
                        with col:
                            st.markdown(f"**{img_data.get('filename', 'Image')}**")

                            # Display image metadata
                            metadata = {
                                "ID": img_data.get("id"),
                                "Location": img_data.get("location", "N/A"),
                                "Quality": img_data.get("quality", "N/A"),
                                "Tags": ", ".join(img_data.get("tags", [])[:3])
                            }

                            # Create a simple text representation
                            for key, value in metadata.items():
                                st.caption(f"**{key}**: {value}")

                            st.divider()

                # Display cache info if available
                if show_cache_info and "cache_info" in message:
                    with st.expander("📊 Cache Details"):
                        st.json(message["cache_info"])

# Chat input
st.markdown("---")

# Input area
col1, col2 = st.columns([0.95, 0.05])

with col1:
    user_input = st.chat_input(
        "Ask about your gallery... (Search, filter, delete, tag, analyze)",
        key="chat_input"
    )

# Process user input
if user_input:
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().isoformat()
    })

    # Show spinner while processing
    with st.spinner("🤖 Thinking..."):
        try:
            # Invoke agent
            result = agent.invoke(user_input)

            # Extract response
            assistant_response = ""
            images = []
            cache_info = None

            # Build response from conversation history
            for msg in result.conversation_history:
                if msg["role"] == "assistant":
                    assistant_response = msg["content"]
                    break

            # Try to extract images from cache
            if agent.search_cache:
                last_search = agent._get_last_search_results()
                if last_search and last_search.get("full_images"):
                    images = last_search["full_images"][:6]  # Limit to 6 images
                    cache_info = {
                        "total_found": last_search.get("total_count"),
                        "cached_at": str(last_search.get("timestamp")),
                        "query": last_search.get("query")
                    }

            # Add assistant message
            message_obj = {
                "role": "assistant",
                "content": assistant_response,
                "timestamp": datetime.now().isoformat()
            }

            if images:
                message_obj["images"] = images

            if cache_info and show_cache_info:
                message_obj["cache_info"] = cache_info

            # Check for errors
            if result.error:
                message_obj["error"] = result.error

            st.session_state.messages.append(message_obj)

            # Rerun to display new message
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"⚠️ Error occurred: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p style='color: #888; font-size: 0.8rem;'>
        🖼️ Gallery Image Search Agent | Powered by Gemini 2.5 | LangChain & LangGraph
    </p>
    <p style='color: #AAA; font-size: 0.75rem;'>
        Context Optimized • Smart Caching • 88% Token Savings
    </p>
</div>
""", unsafe_allow_html=True)
