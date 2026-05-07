import json
from pathlib import Path
from datetime import datetime
from fastmcp import FastMCP

BASE_DIR = Path(__file__).parent / "data"
BASE_DIR.mkdir(exist_ok=True)

mcp = FastMCP("Permission-Aware MCP Server")


def _log(operation: str) -> None:
    with open(BASE_DIR / "audit.log", "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {operation}\n")


@mcp.tool()
def read_file(filepath: str) -> str:
    """Read a file from the data directory. Risk: LOW"""
    try:
        path = BASE_DIR / filepath
        if not path.exists():
            return f"Error: File {filepath} not found"
        return path.read_text()
    except Exception as e:
        return f"Error reading file: {str(e)}"


@mcp.tool()
def write_file(filepath: str, content: str) -> str:
    """Write content to a file in the data directory. Risk: MEDIUM"""
    try:
        (BASE_DIR / filepath).write_text(content)
        _log(f"WRITE: {filepath}")
        return f"Successfully wrote to {filepath}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


@mcp.tool()
def delete_file(filepath: str) -> str:
    """Delete a file from the data directory. Risk: HIGH"""
    try:
        path = BASE_DIR / filepath
        if not path.exists():
            return f"Error: File {filepath} not found"
        path.unlink()
        _log(f"DELETE: {filepath}")
        return f"Successfully deleted {filepath}"
    except Exception as e:
        return f"Error deleting file: {str(e)}"


@mcp.tool()
def execute_command(command: str) -> str:
    """Simulate a system command. Risk: CRITICAL — execution disabled for security."""
    _log(f"EXECUTE (simulated): {command}")
    return f"Simulated execution of: {command}\n(Actual execution disabled for security)"


@mcp.resource("file://audit/log")
def get_audit_log() -> str:
    """Return the audit log of all operations."""
    log = BASE_DIR / "audit.log"
    return log.read_text() if log.exists() else "No audit log entries yet."


@mcp.resource("file://config/permissions")
def get_permissions_config() -> str:
    """Return the current permissions configuration."""
    perm_file = BASE_DIR / "permissions.json"
    if not perm_file.exists():
        return json.dumps({
            "read_file": "allow",
            "write_file": "ask",
            "delete_file": "deny",
            "execute_command": "deny",
        }, indent=2)
    return perm_file.read_text()


@mcp.prompt()
def security_review(operation: str, risk_level: str) -> list[dict]:
    """Return a security review prompt for an operation."""
    return [{
        "role": "user",
        "content": f"""Review this operation for security implications:

Operation: {operation}
Risk Level: {risk_level}

Please analyze:
1. What data or systems could be affected?
2. What are the potential security risks?
3. What safeguards should be in place?
4. Should this operation require user approval?
5. What should be logged for audit purposes?""",
    }]


if __name__ == "__main__":
    mcp.run(transport="stdio")
