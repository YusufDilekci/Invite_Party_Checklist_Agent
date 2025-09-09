from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_tavily import TavilySearch
from retriver import retriever
from langchain.tools import tool
from langgraph.types import interrupt
from dotenv import load_dotenv
from config import MCP_CONFIG
import asyncio
load_dotenv()


def get_mcp_tools(query: str) -> str:
    """
    Get MCP (Model Context Protocol) tools from GitHub server.
    
    Args:
        config: Configuration object containing user authentication details
        
    Returns:
        List of available MCP tools from the GitHub server
    """
    client = MultiServerMCPClient(MCP_CONFIG)
    mcp_tools = asyncio.run(client.get_tools())

    return "".join(mcp_tools)


@tool
def web_search(query: str) -> str:
    """
    Search the web for current information using Tavily Search.
    
    Args:
        query: The search query to find current information on the web
        
    Returns:
        Web search results with relevant information
    """
    search_tool = TavilySearch(max_results=3)
    return search_tool.invoke(query)


@tool
def retrieval(query: str) -> str:
    """
    Search for information about party invites and people who might attend.
    Returns relevant information about people, their relationships, and contact details.
    
    Args:
        query: The search query about people, relationships, or party attendees
        
    Returns:
        Information about relevant people and their details
    """
    try:
        nodes = retriever.retrieve(query)
        
        if not nodes:
            return "No relevant information found in the party invites database."
        
        results = []
        for i, node in enumerate(nodes, 1):
            results.append(f"Result {i}:")
            results.append(f"Content: {node.text}")
            results.append(f"Relevance Score: {node.score:.3f}")
            if node.metadata:
                results.append(f"Metadata: {node.metadata}")
            results.append("---")
        
        return "\n".join(results)
    except Exception as e:
        return f"Error searching party invites: {str(e)}"

@tool
def human_assistance(query: str) -> str:
    """Request assistance from a human for complex party planning decisions."""
    print(f"\n🤝 Human assistance requested:")
    print(f"Query: {query}")
    human_response = interrupt({"query": query})
    return human_response["data"]

tools = [web_search, retrieval, human_assistance, get_mcp_tools] 

if __name__ == "__main__":
    # Example usage
    print(web_search("What's the weather like for a party this weekend?"))
    print(retrieval("Who should I invite to my birthday party?"))
    print(human_assistance("Should I hire a DJ or a live band for the party?"))
    print(get_mcp_tools("List available MCP tools"))