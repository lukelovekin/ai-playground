from fastmcp import FastMCP, Context
from utils import get_path, DocumentGeneratorSchema


def register(mcp: FastMCP) -> None:

    @mcp.prompt()
    async def code_review(file_path: str, ctx: Context) -> str:
        """Return a code review prompt for the given file."""
        try:
            path = get_path(file_path)
            if not path.exists() or not path.is_file():
                error_msg = f"Error: {file_path} is not a valid file"
                await ctx.warning(error_msg)
                raise FileNotFoundError(error_msg)

            current_code = path.read_text(encoding="utf-8").strip()
            language = path.suffix.lower()

            prompt = f"""You are an expert code editor. Review the following code quality.

File: {file_path}
Language (file suffix): {language or "unknown"}

Current code:
'''
{current_code}
'''

Provide a comprehensive evaluation of the code:

""".strip()
            await ctx.info("Successfully returned prompt")
            return prompt
        except Exception as e:
            await ctx.error(f"Error preparing code review prompt: {e}")
            raise

    @mcp.prompt()
    async def documentation_generator(ctx: Context) -> str:
        """Elicit file info and return a documentation-generation prompt."""
        try:
            result = await ctx.elicit(
                message="Please provide the subject file name and the documentation file name",
                response_type=DocumentGeneratorSchema,
            )

            file_path = result.data.file_path
            path = get_path(file_path)

            if not path.exists() or not path.is_file():
                error_msg = f"Error: {file_path} is not a valid file"
                await ctx.warning(error_msg)
                raise FileNotFoundError(error_msg)

            code = path.read_text(encoding="utf-8").strip()
            language = path.suffix.lower()
            doc_name = result.data.name

            prompt = f"""You are an expert technical writer and documentation specialist. Create documentation for the following code file:

File: {file_path}
Language (file suffix): {language or "unknown"}

Current code:
'''
{code}
'''

Use MCP tools available to you to create the separate documentation file:
- **CRITICAL DETAIL: Name that separate document EXACTLY: {doc_name}**
- Add the .md suffix yourself if the name doesn't include it already""".strip()

            await ctx.info("Successfully returned prompt")
            return prompt
        except Exception as e:
            await ctx.error(f"Error generating code documentation prompt: {e}")
            raise
