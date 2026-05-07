from typing import Literal
from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str

    def to_gradio(self) -> dict:
        return {"role": self.role, "content": self.content}


class ChatHistory(BaseModel):
    messages: list[ChatMessage] = []

    @classmethod
    def from_gradio(cls, history: list[dict]) -> "ChatHistory":
        messages = []
        for m in history:
            if m.get("role") not in ("user", "assistant"):
                continue
            content = m.get("content")
            if content is None:
                continue
            # Gradio 6 may pass content as a list of blocks: [{"text": "...", "type": "text"}]
            if isinstance(content, list):
                content = " ".join(
                    block.get("text", "") for block in content if isinstance(block, dict)
                )
            messages.append(ChatMessage(role=m["role"], content=str(content)))
        return cls(messages=messages)

    def to_gradio(self) -> list[dict]:
        return [m.to_gradio() for m in self.messages]

    def to_messages(self) -> list[dict]:
        return [
            m.to_gradio()
            for m in self.messages
            if m.content.strip()
        ]

    def append(self, role: Literal["user", "assistant"], content: str) -> "ChatHistory":
        return ChatHistory(messages=self.messages + [ChatMessage(role=role, content=content)])

    def with_last_content(self, content: str) -> "ChatHistory":
        """Return a new history with the last message's content replaced."""
        if not self.messages:
            return self
        updated = self.messages[:-1] + [
            ChatMessage(role=self.messages[-1].role, content=content)
        ]
        return ChatHistory(messages=updated)


class RetrievedContext(BaseModel):
    query: str
    chunks: list[str]

    def as_text(self) -> str:
        return "\n\n---\n\n".join(self.chunks)


class SessionState(BaseModel):
    message_count: int = 0
    limit: int = 30

    @property
    def is_exhausted(self) -> bool:
        return self.message_count >= self.limit

    @property
    def remaining(self) -> int:
        return max(0, self.limit - self.message_count)

    def increment(self) -> "SessionState":
        return SessionState(message_count=self.message_count + 1, limit=self.limit)
