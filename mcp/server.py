from fastmcp import FastMCP
import tools
import resources
import prompts

mcp = FastMCP("File Operations MCP Server")

tools.register(mcp)
resources.register(mcp)
prompts.register(mcp)

if __name__ == "__main__":
    mcp.run()
