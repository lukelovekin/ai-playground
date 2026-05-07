import asyncio
from fastmcp import FastMCP, Context
from utils import get_path


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    async def write_file(file_path: str, content: str, ctx: Context) -> str:
        """Write content to a file, reporting chunked progress."""
        try:
            path = get_path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            total = len(content)
            chunk_size = max(total // 10, 1)

            with open(path, "w", encoding="utf-8") as f:
                for i in range(0, total, chunk_size):
                    f.write(content[i:i + chunk_size])
                    written = min(i + chunk_size, total)
                    await ctx.report_progress(progress=written, total=total, message=f"Writing: {written}/{total}")
                    await asyncio.sleep(0.05)

            await ctx.report_progress(progress=total, total=total, message="Write complete")
            await ctx.info(f"File written successfully to: {file_path}")
            return f"File written successfully to: {file_path}"
        except Exception as e:
            await ctx.error(f"Error creating file: {str(e)}")
            raise

    @mcp.tool()
    async def delete_file(file_path: str, ctx: Context) -> str:
        """Delete a file from the project directory."""
        try:
            path = get_path(file_path)
            if path.is_file():
                path.unlink()
                await ctx.info(f"Successfully deleted file {file_path}")
                return f"Successfully deleted file {file_path}"
            elif path.is_dir():
                await ctx.warning(f"Error: {file_path} is a directory, not a file")
                return f"Error: {file_path} is a directory, not a file"
            else:
                await ctx.warning(f"File not found: {file_path}")
                return f"File not found: {file_path}"
        except Exception as e:
            await ctx.error(f"Error deleting file: {str(e)}")
            return f"Error deleting file: {str(e)}"
