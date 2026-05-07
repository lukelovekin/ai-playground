import sys
import json
import gradio as gr
from pathlib import Path
from datetime import datetime
from types import SimpleNamespace
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI


DEFAULT_PERMISSIONS = {
    "read_file": "allow",
    "write_file": "ask",
    "delete_file": "deny",
    "execute_command": "deny",
}

RISK_LEVELS = {
    "read_file": "low",
    "write_file": "medium",
    "delete_file": "high",
    "execute_command": "critical",
}


class MCPPermissionHostApp:
    """GPT-4o-mini AI host with client-side permission enforcement and pending-approval flow."""

    def __init__(self, server_script: str):
        self.server_script = server_script
        self.permissions_file = Path("data/permissions.json")
        self.permissions_file.parent.mkdir(exist_ok=True)
        self.audit_log_file = self.permissions_file.parent / "audit.log"
        self.session = None
        self.exit_stack = AsyncExitStack()
        self._connected = False
        self.permissions = self._load_permissions()
        self.llm_client = OpenAI()
        self.model = "gpt-4o-mini"
        self.conversation_history: list[dict] = []
        self.pending_approval: dict | None = None

    def _load_permissions(self) -> dict:
        if self.permissions_file.exists():
            return json.loads(self.permissions_file.read_text())
        return DEFAULT_PERMISSIONS.copy()

    def _check_permission(self, tool_name: str, arguments: dict) -> str:
        arg_key = f"{tool_name}:{json.dumps(arguments, sort_keys=True)}"
        return self.permissions.get(arg_key) or self.permissions.get(tool_name, "ask")

    def _log_audit(self, operation: str, decision: str, reason: str = "") -> None:
        entry = f"[{datetime.now().isoformat()}] {operation} - Decision: {decision}"
        if reason:
            entry += f" - Reason: {reason}"
        with open(self.audit_log_file, "a") as f:
            f.write(entry + "\n")

    async def connect(self) -> None:
        if self._connected:
            return
        server_params = StdioServerParameters(command="python3", args=[self.server_script])
        read, write = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.session = await self.exit_stack.enter_async_context(ClientSession(read, write))
        await self.session.initialize()
        self._connected = True

    async def _list_tools(self):
        await self.connect()
        return (await self.session.list_tools()).tools

    async def _call_tool_with_permission(self, tool_name: str, arguments: dict, approved: bool = False):
        await self.connect()
        permission = self._check_permission(tool_name, arguments)

        if permission == "deny":
            self._log_audit(f"TOOL: {tool_name}", "DENIED", "Policy: deny")
            return [SimpleNamespace(text=f"Permission denied for tool: {tool_name}")]

        if permission == "ask" and not approved:
            self._log_audit(f"TOOL: {tool_name}", "ASK", "Awaiting approval")
            return [SimpleNamespace(text=(
                f"Permission required for tool: {tool_name}\n"
                f"Arguments: {json.dumps(arguments, indent=2)}\n\n"
                "Type 'yes' to approve or 'no' to cancel."
            ))]

        self._log_audit(f"TOOL: {tool_name}", "ALLOWED", f"Policy: {permission}")
        return (await self.session.call_tool(tool_name, arguments=arguments)).content

    async def _list_resources(self):
        await self.connect()
        return (await self.session.list_resources()).resources

    async def _read_resource(self, uri: str):
        await self.connect()
        return (await self.session.read_resource(uri=uri)).contents

    async def _list_prompts(self):
        await self.connect()
        return (await self.session.list_prompts()).prompts

    async def _get_prompt(self, name: str, arguments: dict):
        await self.connect()
        return (await self.session.get_prompt(name=name, arguments=arguments)).messages

    async def cleanup(self) -> None:
        await self.exit_stack.aclose()

    async def get_available_tools(self) -> list[dict]:
        mcp_tools = await self._list_tools()
        openai_tools = []

        for tool in mcp_tools:
            perm = self.permissions.get(tool.name, "ask")
            risk = RISK_LEVELS.get(tool.name, "medium")
            schema: dict = {"type": "object", "properties": {}}
            if hasattr(tool, "inputSchema") and isinstance(tool.inputSchema, dict):
                schema["properties"] = tool.inputSchema.get("properties", {})
                if tool.inputSchema.get("required"):
                    schema["required"] = tool.inputSchema["required"]
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": f"{tool.description or tool.name} (Permission: {perm}, Risk: {risk})",
                    "parameters": schema,
                },
            })

        openai_tools += [
            {"type": "function", "function": {"name": "mcp_list_resources", "description": "List MCP resources", "parameters": {"type": "object", "properties": {}}}},
            {"type": "function", "function": {"name": "mcp_read_resource", "description": "Read a resource by URI", "parameters": {"type": "object", "properties": {"uri": {"type": "string"}}, "required": ["uri"]}}},
            {"type": "function", "function": {"name": "mcp_list_prompts", "description": "List MCP prompt templates", "parameters": {"type": "object", "properties": {}}}},
            {"type": "function", "function": {"name": "mcp_get_prompt", "description": "Get a rendered prompt template", "parameters": {"type": "object", "properties": {"name": {"type": "string"}, "arguments": {"type": "object"}}, "required": ["name"]}}},
        ]

        return openai_tools

    async def execute_tool(self, tool_name: str, arguments: dict) -> str:
        await self.connect()

        if tool_name == "mcp_list_resources":
            resources = await self._list_resources()
            lines = [f"- {r.uri}" + (f" ({r.name})" if r.name else "") + (f": {r.description}" if r.description else "") for r in resources]
            return "Available resources:\n" + "\n".join(lines)

        if tool_name == "mcp_read_resource":
            uri = arguments.get("uri")
            if not uri:
                return "Error: URI is required"
            try:
                contents = await self._read_resource(uri)
                if isinstance(contents, list) and contents:
                    c = contents[0]
                    return c.text if hasattr(c, "text") else str(c)
                return str(contents)
            except Exception as e:
                return f"Error reading resource: {e}"

        if tool_name == "mcp_list_prompts":
            prompts = await self._list_prompts()
            lines = [f"- {p.name}" + (f": {p.description}" if p.description else "") for p in prompts]
            return "Available prompts:\n" + "\n".join(lines)

        if tool_name == "mcp_get_prompt":
            name = arguments.get("name")
            if not name:
                return "Error: Prompt name is required"
            try:
                messages = await self._get_prompt(name, arguments.get("arguments", {}))
                return f"Prompt: {name}\n\n" + "\n\n".join(
                    f"[{getattr(m, 'role', 'unknown')}]: {m.content.text if hasattr(m.content, 'text') else m.content}"
                    for m in messages
                )
            except Exception as e:
                return f"Error getting prompt: {e}"

        try:
            result = await self._call_tool_with_permission(tool_name, arguments)
            if isinstance(result, list) and result:
                c = result[0]
                text = c.text if hasattr(c, "text") else str(c)
                # Store pending approval if tool requires it
                if "Permission required for tool:" in text:
                    self.pending_approval = {"tool_name": tool_name, "arguments": arguments}
                return text
            return str(result)
        except Exception as e:
            return f"Error executing tool: {e}"

    async def chat(self, user_message: str, history: list) -> str:
        await self.connect()

        # Handle pending approval responses
        if self.pending_approval:
            lowered = user_message.strip().lower()
            if lowered in ("yes", "approve", "ok", "confirm", "y"):
                tool_name = self.pending_approval["tool_name"]
                arguments = self.pending_approval["arguments"]
                self.pending_approval = None
                result = await self._call_tool_with_permission(tool_name, arguments, approved=True)
                text = result[0].text if isinstance(result, list) and result and hasattr(result[0], "text") else str(result)
                response_text = f"Operation approved and executed.\n\n{text}"
            elif lowered in ("no", "deny", "cancel", "n"):
                self.pending_approval = None
                response_text = "Operation cancelled."
            else:
                response_text = None

            if response_text is not None:
                self.conversation_history.extend([
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": response_text},
                ])
                return response_text

        self.conversation_history.append({"role": "user", "content": user_message})
        tools = await self.get_available_tools()

        kwargs: dict = {"model": self.model, "messages": self.conversation_history}
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response = self.llm_client.chat.completions.create(**kwargs)
        if not response or not response.choices:
            return "Error: No response from LLM"

        assistant_message = response.choices[0].message

        if assistant_message.tool_calls:
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message.content or "",
                "tool_calls": [
                    {"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                    for tc in assistant_message.tool_calls
                ],
            })

            for tool_call in assistant_message.tool_calls:
                tool_result = await self.execute_tool(
                    tool_call.function.name,
                    json.loads(tool_call.function.arguments),
                )
                self.conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(tool_result),
                })

            final = self.llm_client.chat.completions.create(model=self.model, messages=self.conversation_history)
            if not final or not final.choices:
                return "Error: No response from LLM after tool execution"
            final_message = final.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": final_message})
            return final_message

        self.conversation_history.append({"role": "assistant", "content": assistant_message.content})
        return assistant_message.content

    def _permission_summary(self) -> str:
        lines = ["### Current Permission Policies\n"]
        for tool, policy in self.permissions.items():
            risk = RISK_LEVELS.get(tool, "medium")
            lines.append(f"- **{tool}**: {policy.upper()} (Risk: {risk})")
        return "\n".join(lines)

    def create_interface(self):
        async def chat_wrapper(message, history):
            if not message.strip():
                return history
            response = await self.chat(message, history)
            return history + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": response},
            ]

        async def reset():
            self.conversation_history = []
            return []

        with gr.Blocks(title="MCP Permission AI Host") as interface:
            gr.Markdown(f"# MCP Permission AI Host\n**Model:** {self.model} | Permissions enforced with audit logging")

            chatbot = gr.Chatbot(label="Conversation", height=500, type="messages")
            with gr.Row():
                msg = gr.Textbox(label="Your message", placeholder="Ask me to use MCP tools...", scale=4)
                clear = gr.Button("Clear", scale=1)

            with gr.Accordion("Permission Status", open=False):
                gr.Markdown(self._permission_summary())

            msg.submit(fn=chat_wrapper, inputs=[msg, chatbot], outputs=chatbot).then(lambda: "", outputs=msg)
            clear.click(fn=reset, outputs=chatbot)

        return interface


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 perm_host_app.py <server_script>")
        print("Example: python3 perm_host_app.py perm_server.py")
        sys.exit(1)

    client = MCPPermissionHostApp(sys.argv[1])
    client.create_interface().queue().launch(server_name="127.0.0.1", server_port=7864)


if __name__ == "__main__":
    main()
