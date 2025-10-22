"""
Main entry point for the Gallery Image Search Agent
Initializes the Gemini API and sets up the LangGraph agent
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from src.agent import GalleryAgent
from src.tools_optimized import GALLERY_TOOLS_OPTIMIZED


def initialize_agent(api_key: str = None) -> GalleryAgent:
    """
    Initialize the gallery search agent with Gemini API.

    Args:
        api_key: Google Gemini API key (uses GOOGLE_API_KEY env var if not provided)

    Returns:
        Initialized GalleryAgent instance
    """
    # Load environment variables
    load_dotenv()

    # Get API key
    if not api_key:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY not found. Please set it in .env file or pass it as argument."
            )

    # Initialize Gemini LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0.7,
        top_p=0.9,
        top_k=40
    )

    # Create and return the agent
    agent = GalleryAgent(llm=llm, tools=GALLERY_TOOLS_OPTIMIZED)
    return agent


def run_agent_example():
    """Run an example of the gallery agent."""
    try:
        # Initialize the agent
        print("Initializing Gallery Search Agent...")
        agent = initialize_agent()

        # Example queries
        queries = [
            "Find all mountain photos",
            "Show me blurry images that need cleanup",
            
        ]

        # Process queries
        for query in queries:
            print(f"\n{'='*60}")
            print(f"User Query: {query}")
            print(f"{'='*60}")

            # Invoke the agent
            result = agent.invoke(query)

            # Display results
            print(f"\nConversation History:")
            for msg in result.conversation_history:
                role = msg["role"].upper()
                print(f"\n{role}:")
                print(f"  {msg['content'][:200]}..." if len(msg['content']) > 200 else f"  {msg['content']}")

            print(f"\nAgent completed: {result.is_complete}")
            if result.error:
                print(f"Error: {result.error}")

    except Exception as e:
        print(f"Error running agent: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_agent_example()
