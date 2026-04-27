# tool_use

Explores LLM tool calling via AISuite — covering automatic schema generation, manual JSON schema definitions, `max_turns` behaviour, and a multi-tool email management agent backed by a FastAPI service.

## Projects

### Functions as tools (`functions_as_tools.ipynb`)

Compares two approaches to registering Python functions as tools:

- **Automatic** — AISuite infers the JSON schema from type hints and docstrings.
- **Manual** — schemas are defined explicitly, giving full control over descriptions and constraints.

Also covers how `max_turns` controls agentic loops differently depending on schema approach.

### Email assistant agent (`email_assistant_agent.ipynb`)

A multi-tool agent backed by a live FastAPI email service (SQLite-backed mock inbox with 5 sample emails). The agent reasons over a natural language prompt and autonomously chains tool calls to complete tasks like reading, filtering, and sending emails.

**Available tools:**

```python
list_unread_emails()
search_emails(query: str)
get_email(email_id: int)
mark_email_as_read(email_id: int)
send_email(recipient: str, subject: str, body: str)
search_unread_from_sender(sender: str)
```

## Pattern

Tool calling / Function calling

## Tools

**AISuite**, **OpenAI** (o4-mini), **FastAPI**, **SQLite**

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```env
OPENAI_API_KEY=your_key_here
```

## Run

Open the relevant notebook in Jupyter. For the email assistant, the FastAPI backend must be running — see the notebook setup cells for startup instructions.
