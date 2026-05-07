import sys
import json
import gradio as gr
from pathlib import Path
from datetime import datetime
from types import SimpleNamespace
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


DEFAULT_PERMISSIONS = {
    "read_file": "allow",
    "write_file": "ask",
    "delete_file": "deny",
    "execute_command": "deny",
}


class MCPPermissionClientApp:
    """Gradio GUI client with permission management and audit log for a permission-aware MCP server."""

    def __init__(self, server_script: str):
        self.server_script = server_script
        self.permissions_file = Path("data/permissions.json")
        self.permissions_file.parent.mkdir(exist_ok=True)
        self.audit_log_file = self.permissions_file.parent / "audit.log"
        self.session = None
        self.exit_stack = AsyncExitStack()
        self._connected = False
        self.permissions = self._load_permissions()
        self.tools_cache: list[str] = []

    def _load_permissions(self) -> dict:
        if self.permissions_file.exists():
            return json.loads(self.permissions_file.read_text())
        return DEFAULT_PERMISSIONS.copy()

    def _save_permissions(self) -> None:
        self.permissions_file.write_text(json.dumps(self.permissions, indent=2))

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
                "Click 'Approve & Execute' to proceed."
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

    # --- GUI methods ---

    async def gui_list_tools(self):
        tools = await self._list_tools()
        self.tools_cache = [t.name for t in tools]
        output = ""
        for tool in tools:
            perm = self.permissions.get(tool.name, "ask")
            output += f"- {tool.name}  [{perm.upper()}]\n"
            if tool.description:
                output += f"  {tool.description}\n"
            output += "\n"
        choices = [f"{n} ({self.permissions.get(n, 'ask')})" for n in self.tools_cache]
        return output, gr.update(choices=choices)

    async def gui_call_tool(self, tool_selection: str, arguments_json: str, approved: bool = False):
        if not tool_selection:
            return "Please select a tool first"
        tool_name = tool_selection.split(" (")[0]
        try:
            arguments = json.loads(arguments_json) if arguments_json.strip() else {}
        except json.JSONDecodeError as e:
            return f"Invalid JSON: {e}"
        result = await self._call_tool_with_permission(tool_name, arguments, approved=approved)
        if isinstance(result, list) and result:
            content = result[0]
            return content.text if hasattr(content, "text") else str(content)
        return str(result)

    async def gui_list_resources(self):
        resources = await self._list_resources()
        output = ""
        for r in resources:
            output += f"- {r.uri}"
            if r.name:
                output += f"  ({r.name})"
            if r.description:
                output += f": {r.description}"
            output += "\n"
        return output or "No resources available"

    async def gui_read_resource(self, uri: str):
        if not uri.strip():
            return "Please enter a resource URI"
        contents = await self._read_resource(uri)
        if isinstance(contents, list) and contents:
            c = contents[0]
            return c.text if hasattr(c, "text") else str(c)
        return str(contents)

    async def gui_list_prompts(self):
        prompts = await self._list_prompts()
        output = ""
        choices = []
        for p in prompts:
            output += f"- {p.name}"
            if p.description:
                output += f": {p.description}"
            if getattr(p, "arguments", None):
                output += f"  (args: {', '.join(a.name for a in p.arguments)})"
            output += "\n"
            choices.append(p.name)
        return output, gr.update(choices=choices)

    async def gui_get_prompt(self, prompt_name: str, arguments_json: str):
        if not prompt_name:
            return "Please select a prompt first"
        try:
            arguments = json.loads(arguments_json) if arguments_json.strip() else {}
        except json.JSONDecodeError as e:
            return f"Invalid JSON: {e}"
        messages = await self._get_prompt(prompt_name, arguments)
        output = f"Prompt: {prompt_name}\n\n"
        for msg in messages:
            content = getattr(msg, "content", "")
            if hasattr(content, "text"):
                content = content.text
            output += f"[{getattr(msg, 'role', 'unknown')}]: {content}\n\n"
        return output

    async def gui_configure_permission(self, tool_name: str, policy: str):
        if not tool_name:
            return "Please select a tool"
        if policy not in ("allow", "deny", "ask"):
            return "Policy must be: allow, deny, or ask"
        self.permissions[tool_name] = policy
        self._save_permissions()
        return f"Updated: {tool_name} = {policy}"

    async def gui_view_audit_log(self):
        return self.audit_log_file.read_text() if self.audit_log_file.exists() else "No audit log entries yet."

    def create_interface(self):
        with gr.Blocks(title="MCP Permission Client") as interface:
            gr.Markdown("# MCP Permission Client")

            with gr.Tabs():
                with gr.Tab("Tools"):
                    with gr.Row():
                        with gr.Column():
                            list_tools_btn = gr.Button("List Tools", variant="primary")
                            tools_output = gr.Textbox(label="Available Tools", lines=10)
                        with gr.Column():
                            tool_dropdown = gr.Dropdown(label="Select Tool", choices=[], interactive=True)
                            tool_args = gr.Textbox(label="Arguments (JSON)", placeholder='{"filepath": "test.txt"}', lines=3)
                            with gr.Row():
                                call_tool_btn = gr.Button("Call Tool", variant="primary")
                                approve_tool_btn = gr.Button("Approve & Execute", variant="secondary")
                            tool_result = gr.Textbox(label="Result", lines=10)

                    list_tools_btn.click(fn=self.gui_list_tools, outputs=[tools_output, tool_dropdown])
                    call_tool_btn.click(fn=self.gui_call_tool, inputs=[tool_dropdown, tool_args], outputs=tool_result)

                    async def approve_and_execute(tool_selection, arguments_json):
                        return await self.gui_call_tool(tool_selection, arguments_json, approved=True)

                    approve_tool_btn.click(fn=approve_and_execute, inputs=[tool_dropdown, tool_args], outputs=tool_result)

                with gr.Tab("Resources"):
                    with gr.Row():
                        with gr.Column():
                            list_resources_btn = gr.Button("List Resources", variant="primary")
                            resources_output = gr.Textbox(label="Available Resources", lines=10)
                        with gr.Column():
                            resource_uri = gr.Textbox(label="Resource URI", placeholder="file://audit/log")
                            read_resource_btn = gr.Button("Read Resource", variant="primary")
                            resource_content = gr.Textbox(label="Content", lines=10)

                    list_resources_btn.click(fn=self.gui_list_resources, outputs=resources_output)
                    read_resource_btn.click(fn=self.gui_read_resource, inputs=resource_uri, outputs=resource_content)

                with gr.Tab("Prompts"):
                    with gr.Row():
                        with gr.Column():
                            list_prompts_btn = gr.Button("List Prompts", variant="primary")
                            prompts_output = gr.Textbox(label="Available Prompts", lines=5)
                        with gr.Column():
                            prompt_dropdown = gr.Dropdown(label="Select Prompt", choices=[], interactive=True)
                            prompt_args = gr.Textbox(label="Arguments (JSON)", placeholder='{"operation": "write_file", "risk_level": "MEDIUM"}', lines=2)
                            get_prompt_btn = gr.Button("Get Prompt", variant="primary")
                            prompt_result = gr.Textbox(label="Prompt Messages", lines=10)

                    list_prompts_btn.click(fn=self.gui_list_prompts, outputs=[prompts_output, prompt_dropdown])
                    get_prompt_btn.click(fn=self.gui_get_prompt, inputs=[prompt_dropdown, prompt_args], outputs=prompt_result)

                with gr.Tab("Permissions"):
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("**Configure Tool Permission**")
                            load_tools_btn = gr.Button("Load Tools", size="sm")
                            perm_tool = gr.Dropdown(label="Tool", choices=[], allow_custom_value=True)
                            perm_policy = gr.Radio(choices=["allow", "deny", "ask"], label="Policy", value="ask")
                            save_perm_btn = gr.Button("Save", variant="primary")
                            perm_result = gr.Textbox(label="Result", lines=2)
                        with gr.Column():
                            gr.Markdown("**Audit Log**")
                            view_audit_btn = gr.Button("View Audit Log", variant="secondary")
                            audit_output = gr.Textbox(label="Audit Log", lines=15)

                    async def load_tools_for_perm():
                        tools = await self._list_tools()
                        return gr.Dropdown(choices=[t.name for t in tools])

                    load_tools_btn.click(fn=load_tools_for_perm, outputs=perm_tool)
                    save_perm_btn.click(fn=self.gui_configure_permission, inputs=[perm_tool, perm_policy], outputs=perm_result)
                    view_audit_btn.click(fn=self.gui_view_audit_log, outputs=audit_output)

        return interface


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 perm_client_app.py <server_script>")
        print("Example: python3 perm_client_app.py perm_server.py")
        sys.exit(1)

    client = MCPPermissionClientApp(sys.argv[1])
    client.create_interface().queue().launch(server_name="127.0.0.1", server_port=7863)


if __name__ == "__main__":
    main()
