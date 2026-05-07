# mcp

A collection of MCP (Model Context Protocol) server and client implementations covering stdio transport, HTTP transport, permission enforcement, and multi-server connections.

## Stdio server + CLI client

A modular FastMCP server with a Claude-backed CLI client.

```
client.py  ──stdio──  server.py
                          ├── tools.py     write_file (chunked progress), delete_file
                          ├── resources.py file:///{file_name}, dir://.
                          └── prompts.py   code_review, documentation_generator
```

**Features:**
- `documentation_generator` elicits a file path and output name mid-execution via `ctx.elicit`
- `write_file` reports chunked progress via `ctx.report_progress`
- Client handles `notifications/tools/list_changed` and `notifications/resources/list_changed`
- Agentic loop: Claude calls tools iteratively until `stop_reason != "tool_use"`

**Run:**
```bash
python3 client.py server.py
```

The client launches `server.py` as a subprocess over stdio. Menu options: generate docs, review code, read file, list directory, free-form chat.

---

## HTTP server + Gradio clients

A FastMCP server over Streamable HTTP with two Gradio front-ends.

```
http_host_app.py   (port 7862)  ──┐
http_client_app.py (port 7861)  ──┴── Streamable HTTP ──  http_server.py (port 8000)
                                                               ├── tools    read_file, write_file, list_files
                                                               │            analyze_code (sampling demo)
                                                               ├── resource file://workspace/{filename}
                                                               └── prompts  review_code, analyze_security
```

**Features:**
- All file operations sandboxed to `workspace/`; path traversal blocked
- `analyze_code` demonstrates where `sampling/createMessage` would fire for server-initiated LLM calls
- `http_client_app.py` — tabbed GUI for direct tool/resource/prompt interaction
- `http_host_app.py` — GPT-4o-mini agentic loop; MCP tools converted to OpenAI function-calling format; resources and prompts exposed as synthetic tools

**Run** (three separate terminals):
```bash
python3 http_server.py
python3 http_client_app.py http://127.0.0.1:8000 ./workspace
python3 http_host_app.py http://127.0.0.1:8000 ./workspace
```

---

## Permission-aware server + clients

A stdio server with risk-annotated tools and audit logging, paired with a permission-enforcing GUI client and AI host. Permission checking is client-side — each tool is tagged allow/ask/deny and writes to an audit log.

```
perm_client_app.py (port 7863)  ──┐
perm_host_app.py   (port 7864)  ──┴── stdio ──  perm_server.py
                                                     ├── tools    read_file (LOW), write_file (MEDIUM)
                                                     │            delete_file (HIGH), execute_command (CRITICAL)
                                                     ├── resources file://audit/log, file://config/permissions
                                                     └── prompts  security_review
```

**Features:**
- `allow` — tool executes immediately; `deny` — blocked with audit entry; `ask` — requires explicit approval
- `perm_client_app.py` — tabbed GUI with a Permissions tab to configure per-tool policies and view the audit log; "Approve & Execute" button for ask-gated tools
- `perm_host_app.py` — GPT-4o-mini chat with pending-approval flow: when a tool is ask-gated, the model surfaces a confirmation prompt; typing `yes`/`no` approves or cancels the operation

**Run** (two separate terminals):
```bash
# GUI client
python3 perm_client_app.py perm_server.py

# AI host
python3 perm_host_app.py perm_server.py
```

---

## Multi-server client

A LangGraph ReAct agent connected to two external MCP servers simultaneously via `MultiServerMCPClient`.

- **Context7** (HTTP) — library and framework documentation
- **Met Museum** (stdio, via `npx`) — museum collection search

Maintains conversation memory across turns with `InMemorySaver`.

**Run:**
```bash
python3 multi_server_client.py
```

Requires Node.js for `npx metmuseum-mcp`.

---

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

`.env`:
```env
ANTHROPIC_API_KEY=your_key
OPENAI_API_KEY=your_key
```

## Project structure

```
mcp/
├── server.py              # FastMCP stdio server
├── client.py              # CLI client — Claude agentic loop, menu, elicitation handler
├── tools.py               # write_file (chunked progress), delete_file
├── resources.py           # file:/// and dir:// resources
├── prompts.py             # code_review, documentation_generator
├── utils.py               # BASE_DIR, get_path, Pydantic schemas
├── http_server.py         # FastMCP HTTP server (port 8000)
├── http_client.py         # Base MCPHTTPClient — Streamable HTTP transport
├── http_client_app.py     # Gradio GUI client (port 7861)
├── http_host_app.py       # AI host app — GPT-4o-mini + MCP tools (port 7862)
├── perm_server.py         # Permission-aware stdio server with audit logging
├── perm_client_app.py     # Gradio GUI client with permission management (port 7863)
├── perm_host_app.py       # AI host with pending-approval flow (port 7864)
├── multi_server_client.py # LangGraph ReAct agent — multi-server MCP client
└── requirements.txt
```
