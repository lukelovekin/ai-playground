from datetime import datetime
from fastmcp import FastMCP
from utils import get_path, BASE_DIR


def register(mcp: FastMCP) -> None:

    @mcp.resource("file:///{file_name}")
    async def read_file_resource(file_name: str) -> dict:
        """Return file content by path."""
        try:
            path = get_path(file_name)
            if not path.exists() or not path.is_file():
                return {"error": f"Error: {file_name} is not a valid file"}
            return {"file_content": path.read_text(encoding="utf-8")}
        except Exception as e:
            return {"error": f"Error reading file: {str(e)}"}

    @mcp.resource("dir://.")
    async def list_files_resource() -> dict:
        """Return directory listing with metadata."""
        try:
            path = get_path(".")
            if not path.exists() or not path.is_dir():
                return {"error": f"{path} is not a valid directory"}

            items = []
            for item in path.iterdir():
                stat = item.stat()
                items.append({
                    "name": item.name,
                    "path": str(item.relative_to(BASE_DIR)),
                    "type": "directory" if item.is_dir() else "file",
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                })

            return {"items": items}
        except Exception as e:
            return {"error": f"Error listing files: {e}"}
