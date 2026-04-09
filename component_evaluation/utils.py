import base64
import json
import re
import urllib.parse
from typing import Any

import duckdb  # noqa: F401
import pandas as pd
from IPython.display import HTML, display


def print_html(content: Any, title: str | None = None, is_image: bool = False):
    """
    Pretty-print content inside a styled card.

    - is_image=True + string: render as <img>.
    - DataFrame/Series: render as HTML table.
    - Otherwise: show as <pre><code>.
    """
    from html import escape as _escape

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
        rendered = f"<pre><code>{_escape(content)}</code></pre>"
    else:
        rendered = f"<pre><code>{_escape(str(content))}</code></pre>"

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


def clean_json_block(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)
    return raw.strip()


_URL_RE = re.compile(r"https?://[^\s\)\]\}<>\"']+", re.IGNORECASE)


def _extract_hostname(url: str) -> str:
    try:
        host = urllib.parse.urlparse(url).hostname or ""
        return host[4:] if host.startswith("www.") else host
    except Exception:
        return ""


def extract_urls(text: str) -> list[dict[str, Any]]:
    """Extract URLs from arbitrary text. Returns list of {title, url, source} dicts."""
    if not isinstance(text, str):
        text = str(text)
    items = []
    for u in _URL_RE.findall(text):
        host = _extract_hostname(u)
        items.append({"title": None, "url": u, "source": host or None})
    return items


def evaluate_anytext_against_domains(
    TOP_DOMAINS: set[str], payload: Any, min_ratio: float = 0.4
):
    """
    Evaluate whether search results come from trusted domains.

    Accepts:
    - list[dict] (Tavily-like), or
    - dict with 'results' list, or
    - raw string (free text with links).

    Returns (ok, report_dict).
    """
    items: list = []
    if isinstance(payload, list):
        items = payload
    elif isinstance(payload, dict) and isinstance(payload.get("results"), list):
        items = payload["results"]
    elif isinstance(payload, str):
        s = payload.strip()
        if s.startswith("```"):
            s = re.sub(r"^```(?:json|text|markdown)?\s*", "", s)
            s = re.sub(r"\s*```$", "", s)
        try:
            maybe = json.loads(s)
            items = maybe if isinstance(maybe, list) else extract_urls(payload)
        except Exception:
            items = extract_urls(payload)
    else:
        items = extract_urls(str(payload))

    total = len(items)
    if total == 0:
        return False, {"total": 0, "approved": 0, "ratio": 0.0, "details": [], "note": "No items/links parsed"}

    details = []
    approved = 0
    for it in items:
        url = (it or {}).get("url")
        host = _extract_hostname(url or "")
        ok = any(host.endswith(dom) for dom in TOP_DOMAINS) if host else False
        if ok:
            approved += 1
        details.append({"title": (it or {}).get("title"), "url": url, "host": host, "approved": ok})

    ratio = approved / max(total, 1)
    ok = ratio >= min_ratio
    return ok, {"total": total, "approved": approved, "ratio": ratio, "details": details, "min_ratio": min_ratio}


def evaluate_references(
    history: list[tuple[str, str, str]], TOP_DOMAINS: set[str], min_ratio: float = 0.4
) -> str:
    """
    Find the most recent research_agent output, extract links, compare domains to
    TOP_DOMAINS, and return a Markdown PASS/FAIL report.
    """
    payload = None
    for _step, agent, output in reversed(history):
        if agent == "research_agent":
            payload = output
            break

    if payload is None:
        for _, _, output in reversed(history):
            if isinstance(output, str) and ("http://" in output or "https://" in output):
                payload = output
                break

    if payload is None:
        ok, report = False, {"total": 0, "approved": 0, "ratio": 0.0, "details": [], "min_ratio": min_ratio}
    else:
        ok, report = evaluate_anytext_against_domains(TOP_DOMAINS, payload, min_ratio=min_ratio)

    status = "✅ PASS" if ok else "❌ FAIL"
    header = f"### Evaluation — Tavily Top Domains ({status})"
    summary = (
        f"- Total: {report['total']}\n"
        f"- Approved: {report['approved']}\n"
        f"- Ratio: {report['ratio']:.0%} (min {int(min_ratio * 100)}%)\n"
    )
    rows = (report.get("details") or [])[:10]
    lines = ["| Host | Approved | Title |", "|---|:---:|---|"]
    for r in rows:
        lines.append(
            f"| {r.get('host') or '-'} | {'✅' if r.get('approved') else '—'} | {r.get('title') or r.get('url') or '-'} |"
        )
    note = "*Evaluation compares extracted link domains to a fixed allow-list (`TOP_DOMAINS`) and does not re-query tools.*"
    return "\n".join([header, summary, *lines, note])


def evaluate_tavily_results(TOP_DOMAINS: set[str], raw: Any, min_ratio: float = 0.4):
    """
    Evaluate whether Tavily search results mostly come from trusted domains.

    Args:
        TOP_DOMAINS: Set of trusted domains (e.g., {'arxiv.org', 'nature.com'}).
        raw: Tavily output — a list of dicts with 'url', a JSON string, or plain text with URLs.
        min_ratio: Minimum trusted ratio required to pass.

    Returns:
        tuple[bool, str]: (passed, markdown_report)
    """
    if isinstance(raw, str):
        try:
            results = json.loads(raw)
        except Exception:
            # Fall back to URL extraction from plain text
            url_pattern = re.compile(r"https?://[^\s\]\)>\}]+", flags=re.IGNORECASE)
            urls = url_pattern.findall(raw)
            if not urls:
                return False, "### Evaluation — Tavily Top Domains\nNo URLs detected in the provided text."
            results = [{"url": u} for u in urls]
    elif isinstance(raw, list):
        results = raw
    else:
        return False, f"❌ Unexpected input type: {type(raw)}"

    total = len(results)
    trusted_count = 0
    details = []
    for r in results:
        url = r.get("url", "") if isinstance(r, dict) else str(r)
        domain = url.split("/")[2] if "://" in url else url
        trusted = any(td in domain for td in TOP_DOMAINS)
        if trusted:
            trusted_count += 1
        details.append(f"- {url} → {'✅ TRUSTED' if trusted else '❌ NOT TRUSTED'}")

    ratio = trusted_count / total if total > 0 else 0.0
    flag = ratio >= min_ratio
    report = (
        f"### Evaluation — Tavily Top Domains\n"
        f"- Total results: {total}\n"
        f"- Trusted results: {trusted_count}\n"
        f"- Ratio: {ratio:.2%}\n"
        f"- Threshold: {min_ratio:.0%}\n"
        f"- Status: {'✅ PASS' if flag else '❌ FAIL'}\n\n"
        f"**Details:**\n" + "\n".join(details)
    )
    return flag, report
