import base64
import json
import os
from html import escape
from typing import Any
from urllib.parse import urljoin

import pandas as pd
import requests
from dotenv import load_dotenv
from IPython.display import HTML, display

load_dotenv()

BASE_URL = os.getenv("M3_EMAIL_SERVER_API_URL")

session = requests.Session()
session.headers.update({"User-Agent": "LF-ADP-EmailClient/1.0"})


def print_html(content: Any, title: str | None = None, is_image: bool = False):
    """
    Pretty-print content inside a styled card.

    - is_image=True + string content: render as <img>.
    - DataFrame/Series: render as HTML table.
    - Otherwise: show as <pre><code>.
    """
    def image_to_base64(image_path: str) -> str:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")

    if is_image and isinstance(content, str):
        b64 = image_to_base64(content)
        rendered = (
            f'<img src="data:image/png;base64,{b64}" alt="Image" '
            'style="max-width:100%; height:auto; border-radius:8px;">'
        )
    elif isinstance(content, pd.DataFrame):
        rendered = content.to_html(classes="pretty-table", index=False, border=0, escape=False)
    elif isinstance(content, pd.Series):
        rendered = content.to_frame().to_html(classes="pretty-table", border=0, escape=False)
    elif isinstance(content, str):
        rendered = f"<pre><code>{escape(content)}</code></pre>"
    else:
        rendered = f"<pre><code>{escape(str(content))}</code></pre>"

    css = """
    <style>
    .pretty-card {
        font-family: ui-sans-serif, system-ui;
        border: 2px solid transparent;
        border-radius: 14px;
        padding: 14px 16px;
        margin: 10px 0;
        background: linear-gradient(#fff, #fff) padding-box,
                    linear-gradient(135deg, #3b82f6, #9333ea) border-box;
        color: #111;
        box-shadow: 0 4px 12px rgba(0,0,0,.08);
    }
    .pretty-title { font-weight: 700; margin-bottom: 8px; font-size: 14px; color: #111; }
    .pretty-card pre, .pretty-card code {
        background: #f3f4f6; color: #111; padding: 8px; border-radius: 8px;
        display: block; overflow-x: auto; font-size: 13px; white-space: pre-wrap;
    }
    .pretty-card img { max-width: 100%; height: auto; border-radius: 8px; }
    .pretty-card table.pretty-table { border-collapse: collapse; width: 100%; font-size: 13px; color: #111; }
    .pretty-card table.pretty-table th, .pretty-card table.pretty-table td {
        border: 1px solid #e5e7eb; padding: 6px 8px; text-align: left;
    }
    .pretty-card table.pretty-table th { background: #f9fafb; font-weight: 600; }
    </style>
    """

    title_html = f'<div class="pretty-title">{title}</div>' if title else ""
    display(HTML(css + f'<div class="pretty-card">{title_html}{rendered}</div>'))


def pretty_display(title: str, response: requests.Response):
    """Render an HTTP response in a styled block; returns parsed content."""
    status = response.status_code
    try:
        content = response.json()
        body = json.dumps(content, indent=2)
    except Exception:
        content = response.text
        body = content

    html = f"""
    <div style='border:1px solid #ccc; border-left:5px solid #007bff; padding:10px;
                margin:10px 0; background:#f9f9f9; color:#000;'>
        <strong style='color:#007bff'>{escape(title)}:</strong>
        <span style='color:{"green" if status == 200 else "red"}'> Status {status}</span>
        <pre style='font-size:12px; margin-top:10px; white-space:pre-wrap; color:#000;'>{escape(body)}</pre>
    </div>
    """
    display(HTML(html))
    return content


def reset_database() -> dict:
    """Calls the /reset_database endpoint."""
    r = session.get(f"{BASE_URL}/reset_database")
    r.raise_for_status()
    return r.json()


def test_send_email():
    payload = {
        "recipient": "test@example.com",
        "subject": "Test Subject",
        "body": "This is a test email body.",
    }
    return pretty_display("POST /send", session.post(f"{BASE_URL}/send", json=payload))


def test_list_emails():
    return pretty_display("GET /emails", session.get(f"{BASE_URL}/emails"))


def test_search_emails(q: str = "report"):
    return pretty_display(
        f"GET /emails/search?q={q}",
        session.get(f"{BASE_URL}/emails/search", params={"q": q}),
    )


def test_filter_emails(
    recipient: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
):
    params = {k: v for k, v in {"recipient": recipient, "date_from": date_from, "date_to": date_to}.items() if v}
    return pretty_display("GET /emails/filter", session.get(f"{BASE_URL}/emails/filter", params=params))


def test_unread_emails():
    return pretty_display("GET /emails/unread", session.get(f"{BASE_URL}/emails/unread"))


def test_get_email(email_id: str):
    return pretty_display(f"GET /emails/{email_id}", session.get(f"{BASE_URL}/emails/{email_id}"))


def test_mark_read(email_id: str):
    return pretty_display(f"PATCH /emails/{email_id}/read", session.patch(f"{BASE_URL}/emails/{email_id}/read"))


def test_mark_unread(email_id: str):
    return pretty_display(f"PATCH /emails/{email_id}/unread", session.patch(f"{BASE_URL}/emails/{email_id}/unread"))


def test_delete_email(email_id: str):
    return pretty_display(f"DELETE /emails/{email_id}", session.delete(f"{BASE_URL}/emails/{email_id}"))


def call_llm_email_agent(
    prompt: str,
    api_url: str | None = None,
    timeout: int = 30,
) -> dict:
    """
    Calls the LLM server with a natural-language instruction.

    Args:
        prompt: Instruction for the agent.
        api_url: Base URL of the LLM server; falls back to M3_LLM_SERVER_URL env var.
        timeout: HTTP timeout in seconds.

    Returns:
        dict with keys: ok, status, response, raw.
    """
    base = api_url or os.getenv("M3_LLM_SERVER_URL")
    if not base:
        raise RuntimeError(
            "M3_LLM_SERVER_URL is not set. Add it to your .env (e.g., http://127.0.0.1:5001)."
        )

    endpoint = (
        base
        if base.rstrip("/").endswith("/prompt")
        else urljoin(base.rstrip("/") + "/", "prompt")
    )

    try:
        r = requests.post(endpoint, json={"prompt": prompt}, timeout=timeout)
    except requests.RequestException as e:
        return {"ok": False, "status": None, "response": None, "raw": str(e)}

    try:
        data = r.json()
    except ValueError:
        data = r.text

    return {
        "ok": r.status_code == 200,
        "status": r.status_code,
        "response": data.get("response") if isinstance(data, dict) else None,
        "raw": data,
    }
