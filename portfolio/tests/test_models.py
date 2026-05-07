import pytest
from backend.models import ChatHistory, ChatMessage, RetrievedContext, SessionState


class TestChatHistoryFromGradio:
    def test_plain_string_content(self):
        raw = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
        ]
        history = ChatHistory.from_gradio(raw)
        assert len(history.messages) == 2
        assert history.messages[0].content == "Hello"
        assert history.messages[1].content == "Hi there"

    def test_gradio6_block_content(self):
        """Gradio 6 passes content as a list of blocks instead of a plain string."""
        raw = [{"role": "user", "content": [{"text": "What's his tech stack?", "type": "text"}]}]
        history = ChatHistory.from_gradio(raw)
        assert len(history.messages) == 1
        assert history.messages[0].content == "What's his tech stack?"

    def test_multiple_blocks_joined(self):
        raw = [{"role": "user", "content": [
            {"text": "Hello", "type": "text"},
            {"text": "world", "type": "text"},
        ]}]
        history = ChatHistory.from_gradio(raw)
        assert history.messages[0].content == "Hello world"

    def test_unknown_roles_filtered(self):
        raw = [
            {"role": "user", "content": "Hello"},
            {"role": "system", "content": "You are..."},
            {"role": "assistant", "content": "Hi"},
        ]
        history = ChatHistory.from_gradio(raw)
        assert len(history.messages) == 2
        assert all(m.role in ("user", "assistant") for m in history.messages)

    def test_none_content_filtered(self):
        raw = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": None},
        ]
        history = ChatHistory.from_gradio(raw)
        assert len(history.messages) == 1

    def test_empty_list_returns_empty_history(self):
        assert ChatHistory.from_gradio([]).messages == []


class TestChatHistoryToMessages:
    def test_empty_assistant_placeholder_excluded(self):
        history = ChatHistory.from_gradio([
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": ""},
        ])
        result = history.to_messages()
        assert len(result) == 1
        assert result[0]["role"] == "user"

    def test_whitespace_only_excluded(self):
        history = ChatHistory.from_gradio([
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "   "},
        ])
        assert len(history.to_messages()) == 1

    def test_real_content_included(self):
        history = ChatHistory.from_gradio([
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
        ])
        result = history.to_messages()
        assert len(result) == 2


class TestChatHistoryMutations:
    def test_append_is_immutable(self):
        original = ChatHistory()
        new = original.append("user", "Hello")
        assert len(original.messages) == 0
        assert len(new.messages) == 1

    def test_append_sequence(self):
        history = (
            ChatHistory()
            .append("user", "Hello")
            .append("assistant", "Hi")
            .append("user", "How are you?")
        )
        assert len(history.messages) == 3
        assert history.messages[-1].content == "How are you?"

    def test_with_last_content_is_immutable(self):
        history = ChatHistory().append("user", "Hello").append("assistant", "")
        updated = history.with_last_content("Hi there")
        assert history.messages[-1].content == ""
        assert updated.messages[-1].content == "Hi there"

    def test_with_last_content_only_changes_last(self):
        history = (
            ChatHistory()
            .append("user", "Hello")
            .append("assistant", "Hi")
            .append("user", "Again")
            .append("assistant", "")
        )
        updated = history.with_last_content("Streaming response")
        assert updated.messages[0].content == "Hello"
        assert updated.messages[1].content == "Hi"
        assert updated.messages[-1].content == "Streaming response"

    def test_with_last_content_on_empty_history(self):
        history = ChatHistory()
        assert history.with_last_content("anything").messages == []


class TestRetrievedContext:
    def test_as_text_joins_chunks(self):
        ctx = RetrievedContext(query="test", chunks=["chunk one", "chunk two", "chunk three"])
        text = ctx.as_text()
        assert "chunk one" in text
        assert "chunk two" in text
        assert text.count("---") == 2

    def test_as_text_single_chunk(self):
        ctx = RetrievedContext(query="test", chunks=["only chunk"])
        assert ctx.as_text() == "only chunk"

    def test_as_text_empty_chunks(self):
        ctx = RetrievedContext(query="test", chunks=[])
        assert ctx.as_text() == ""


class TestSessionState:
    def test_not_exhausted_by_default(self):
        assert not SessionState().is_exhausted

    def test_exhausted_at_limit(self):
        state = SessionState(message_count=30, limit=30)
        assert state.is_exhausted

    def test_increment_is_immutable(self):
        original = SessionState(message_count=5)
        incremented = original.increment()
        assert original.message_count == 5
        assert incremented.message_count == 6

    def test_remaining_counts_down(self):
        state = SessionState(message_count=25, limit=30)
        assert state.remaining == 5

    def test_remaining_floors_at_zero(self):
        state = SessionState(message_count=35, limit=30)
        assert state.remaining == 0
