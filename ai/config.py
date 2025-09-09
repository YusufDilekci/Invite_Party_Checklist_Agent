import os
from dotenv import load_dotenv

load_dotenv()


MCP_CONFIG = {
    "github": {
        "transport": "streamable_http",
        "url": "https://github.com/mcp/api",
        "headers": {
            "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN', '')}"
        }
    }
}
