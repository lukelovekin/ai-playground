import asyncio
import sys
import json
from urllib.parse import quote
from typing import Any
from contextlib import AsyncExitStack

from fastmcp import Client
from fastmcp.client.elicitation import ElicitResult

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL_ID = "claude-sonnet-4-5-20250929"


class MCPClient:
    def __init__(self):
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()

    async def connect_to_server(self, server_script_path: str) -> None:
        if not server_script_path.endswith(('.py', '.js', '.ts')):
            raise ValueError("Server script must be a .py, .js, or .ts file")

        self.client = Client(
            server_script_path,
            elicitation_handler=self.handle_elicitation,
            progress_handler=self.handle_progress,
            message_handler=self.handle_message,
        )
        await self.exit_stack.enter_async_context(self.client)

    async def handle_elicitation(self, message: str, response_type: type, params, context):
        print(f"Server asks: {message}")
        user_data = {}
        for field_name, field_type in response_type.__annotations__.items():
            user_input = input(f"Enter value for '{field_name}' ({field_type.__name__}): ").strip()
            if not user_input:
                return ElicitResult(action="decline")
            user_data[field_name] = user_input
        return response_type(**user_data)

    async def handle_progress(self, progress: float, total: float | None, message: str | None) -> None:
        if total is not None:
            print(f"Progress: {(progress / total) * 100:.1f}% - {message or ''}")
        else:
            print(f"Progress: {progress} - {message or ''}")

    async def handle_message(self, message) -> None:
        if hasattr(message, 'root'):
            method = message.root.method
            if method == "notifications/tools/list_changed":
                print("Server: tools changed")
            elif method == "notifications/resources/list_changed":
                print("Server: resources changed")

    async def _get_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": tool.name,
                "description": tool.description or "MCP Tool",
                "input_schema": tool.inputSchema,
            }
            for tool in await self.client.list_tools()
        ]

    async def _get_prompts(self):
        return await self.client.list_prompts()

    async def process_query(self, query: str) -> str:
        messages = [{"role": "user", "content": query}]
        available_tools = await self._get_tools()

        response = self.anthropic.messages.create(
            model=MODEL_ID,
            max_tokens=4096,
            messages=messages,
            tools=available_tools,
        )

        while response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for content in response.content:
                if content.type == "tool_use":
                    try:
                        result = await self.client.call_tool(content.name, content.input)
                        result_text = (
                            "\n".join(c.text if hasattr(c, "text") else str(c) for c in result.content)
                            if isinstance(result.content, list)
                            else result.content
                        )
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": content.id,
                            "content": result_text,
                        })
                    except Exception as e:
                        print(f"Error calling tool {content.name}: {e}")
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": content.id,
                            "content": f"Error: {str(e)}",
                            "is_error": True,
                        })

            messages.append({"role": "user", "content": tool_results})
            response = self.anthropic.messages.create(
                model=MODEL_ID,
                max_tokens=4096,
                messages=messages,
                tools=available_tools,
            )

        return "\n".join(c.text for c in response.content if hasattr(c, "text"))

    async def converse(self) -> None:
        print("\nEntering conversation mode. Type 'quit' or 'q' to exit.")
        while True:
            query = input("\nQuery: ").strip()
            if query.lower() in ("quit", "q"):
                break
            if not query:
                print("Please enter a query")
                continue
            try:
                print("\n" + await self.process_query(query))
            except Exception as e:
                print(f"Error processing query: {e}")

    async def prompt(self, prompt_name: str) -> None:
        try:
            prompts = await self._get_prompts()
            prompt_obj = next((p for p in prompts if p.name == prompt_name), None)
            if not prompt_obj:
                print(f"Prompt '{prompt_name}' not found")
                return

            print(prompt_obj)
            arguments = {}
            if prompt_obj.arguments:
                for arg in prompt_obj.arguments:
                    user_input = input(f"{arg.name} ({'required' if arg.required else 'optional'}): ").strip()
                    if not user_input and arg.required:
                        print(f"Error: {arg.name} is required")
                        return
                    if user_input:
                        arguments[arg.name] = user_input

            result = await self.client.get_prompt(prompt_name, arguments=arguments)
            print(await self.process_query(result.messages[0].content.text))
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")

    async def read_file(self) -> None:
        try:
            file_name = input("Enter file path: ").strip()
            resource = await self.client.read_resource(f"file:///{quote(file_name, safe='')}")
            file_content = json.loads(resource[0].text)["file_content"]
            print(f"File Content:\n {file_content}")
        except Exception as e:
            print(f"Error reading file: {e}")

    def _print_dir_listing(self, items: list[dict]) -> None:
        print(f"\n{'Type':<10} {'Size':>10} {'Modified':<25} {'Name'}")
        print("-" * 70)
        for item in items:
            size = f"{item['size']} B"
            print(f"{item['type']:<10} {size:>10}  {item['modified']:<25} {item['name']}")

    async def read_dir(self) -> None:
        try:
            resource = await self.client.read_resource("dir://.")
            self._print_dir_listing(json.loads(resource[0].text)["items"])
        except Exception as e:
            print(f"Error reading directory: {e}")

    async def menu(self) -> None:
        print("\nMCP Client Started!")

        menu_actions = {
            "1": lambda: self.prompt("documentation_generator"),
            "2": lambda: self.prompt("code_review"),
            "3": self.read_file,
            "4": self.read_dir,
            "5": self.converse,
            "q": self._quit,
            "quit": self._quit,
        }

        while True:
            choice = input("""
Select from the Menu
1. Generate Documentation
2. Review Code
3. Read File
4. Read Current Directory
5. Converse with Agent
q. Quit
> """).strip()

            action = menu_actions.get(choice)
            if not action:
                print("Invalid choice. Please try again.")
                continue
            if await action() == "quit":
                break

    async def _quit(self) -> str:
        print("Exiting client...")
        return "quit"

    async def cleanup(self) -> None:
        if self.exit_stack:
            await self.exit_stack.aclose()


async def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 client.py <server_path>")
        sys.exit(1)

    client = MCPClient()
    try:
        print(f"Connecting to server: {sys.argv[1]}")
        await client.connect_to_server(sys.argv[1])
        await client.menu()
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
