"""Portfolio chatbot — Gradio UI with ChromaDB RAG and Groq streaming."""
import base64
import os
from pathlib import Path
from groq import Groq
import gradio as gr
from dotenv import load_dotenv
from backend.models import ChatHistory, SessionState
from backend.rag import retrieve

load_dotenv()

_chroma_dir = Path(__file__).parent / "chroma_db"
if not _chroma_dir.exists():
    from backend.ingest import ingest
    ingest()

client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = "llama-3.3-70b-versatile"
SESSION_LIMIT = 30
MESSAGE_MAX_CHARS = 500

SYSTEM_PROMPT = (Path(__file__).parent / "data" / "system_prompt.txt").read_text()
CUSTOM_CSS = (Path(__file__).parent / "styles.css").read_text()


def _load_portrait() -> str:
    path = Path(__file__).parent / "prof_portrait.JPG"
    if path.exists():
        b64 = base64.b64encode(path.read_bytes()).decode()
        return f'<img src="data:image/jpeg;base64,{b64}" style="width:80px;height:80px;border-radius:50%;object-fit:cover;border:2px solid #4f6ef7;">'
    return '<div style="width:64px;height:64px;border-radius:50%;background:#2a2d3a;border:2px solid #4f6ef7;"></div>'


PORTRAIT_HTML = _load_portrait()

SUGGESTIONS = [
    "What has Luke worked on recently?",
    "What personal projects has he built recently?",
    "What's his engineering background?",
    "What is he looking for?",
    "What's he like to work with?",
]


def chat(message: str, raw_history: list[dict]):
    context = retrieve(message)
    history = ChatHistory.from_gradio(raw_history)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += history.to_messages()
    messages.append({
        "role": "user",
        "content": f"Context about Luke:\n{context.as_text()}\n\nQuestion: {message}",
    })

    response = ""
    stream = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=512,
        stream=True,
    )
    for chunk in stream:
        text = chunk.choices[0].delta.content
        if text:
            response += text
            yield response


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="Luke Lovekin — Software Engineer") as demo:

        # ── Header ──────────────────────────────────────
        with gr.Row(elem_id="header"):
            gr.HTML(
                f'<div style="display:flex;align-items:center;gap:20px;padding:8px 0">'
                f'{PORTRAIT_HTML}'
                f'<div><h1 style="font-size:1.25rem;font-weight:600;color:#e8eaf0;margin:0">Luke Lovekin</h1>'
                f'<p style="font-size:0.85rem;color:#8b8fa8;margin:2px 0 0">Software Engineer · Ask me anything</p></div>'
                f'</div>'
            )

        # ── Chat ─────────────────────────────────────────
        chatbot = gr.Chatbot(
            value=[],
            elem_id="chatbot",
            show_label=False,
            height=480,
        )

        # ── Suggested questions ──────────────────────────
        with gr.Row():
            suggestion_btns = [
                gr.Button(s, elem_classes=["suggestion-btn"], size="sm")
                for s in SUGGESTIONS
            ]

        # ── Input ────────────────────────────────────────
        with gr.Row(elem_id="input-row"):
            msg = gr.Textbox(
                placeholder="Ask about Luke's projects, skills, or background…",
                show_label=False,
                scale=9,
                elem_id="msg-box",
                autofocus=True,
            )
            send = gr.Button("Send", scale=1, elem_id="send-btn", variant="primary")

        # ── Session state ─────────────────────────────────
        session = gr.State(SessionState())

        # ── Footer ───────────────────────────────────────
        gr.HTML('<div id="footer">Powered by Groq · Llama 3.3 70B · RAG · ChromaDB</div>')

        # ── Event handlers ────────────────────────────────
        def submit(message: str, raw_history: list[dict], state: SessionState):
            if not message.strip():
                return "", raw_history, state
            if len(message) > MESSAGE_MAX_CHARS:
                error_msg = f"Message too long — please keep it under {MESSAGE_MAX_CHARS} characters."
                history = (
                    ChatHistory.from_gradio(raw_history)
                    .append("user", message[:80] + "…")
                    .append("assistant", error_msg)
                )
                return "", history.to_gradio(), state
            if state.is_exhausted:
                limit_msg = f"You've reached the {SESSION_LIMIT}-message session limit. Refresh the page to start a new session."
                history = (
                    ChatHistory.from_gradio(raw_history)
                    .append("user", message)
                    .append("assistant", limit_msg)
                )
                return "", history.to_gradio(), state
            history = (
                ChatHistory.from_gradio(raw_history)
                .append("user", message)
                .append("assistant", "")
            )
            return "", history.to_gradio(), state.increment()

        def stream_response(raw_history: list[dict], state: SessionState):
            if not raw_history or state.is_exhausted:
                yield raw_history
                return
            history = ChatHistory.from_gradio(raw_history)
            user_msg = history.messages[-2].content
            prior = ChatHistory(messages=history.messages[:-2])
            for partial in chat(user_msg, prior.to_gradio()):
                yield history.with_last_content(partial).to_gradio()

        def _wire(trigger):
            trigger(submit, [msg, chatbot, session], [msg, chatbot, session]).then(
                stream_response, [chatbot, session], chatbot
            )

        _wire(msg.submit)
        _wire(send.click)

        for btn, suggestion in zip(suggestion_btns, SUGGESTIONS):
            btn.click(
                fn=lambda s=suggestion: s,
                outputs=msg,
            ).then(
                fn=submit, inputs=[msg, chatbot, session], outputs=[msg, chatbot, session]
            ).then(
                fn=stream_response, inputs=[chatbot, session], outputs=chatbot
            )

    return demo


if __name__ == "__main__":
    build_ui().launch(server_port=7860, css=CUSTOM_CSS)
