"""Test per WebSocket API."""

import pytest
import asyncio
from core.websocket_api import (
    TaskStatus, MessageType, ChatMessage, TaskUpdate, ApprovalRequest,
    ChatSession, ChatSessionManager, WebSocketAPI, create_websocket_api
)


class TestChatSession:
    """Test ChatSession."""

    def test_session_creation(self):
        """Test creazione sessione."""
        session = ChatSession("session_1")
        assert session.session_id == "session_1"
        assert len(session.messages) == 0

    def test_add_message(self):
        """Test aggiunta messaggio."""
        session = ChatSession("session_1")
        msg = session.add_message("user", "Hello")
        
        assert len(session.messages) == 1
        assert msg.content == "Hello"
        assert msg.sender == "user"

    def test_update_task(self):
        """Test aggiornamento task."""
        session = ChatSession("session_1")
        update = session.update_task("task_1", TaskStatus.IMPLEMENTING, "Coding", 50)
        
        assert update.task_id == "task_1"
        assert update.status == TaskStatus.IMPLEMENTING
        assert update.progress == 50

    def test_request_approval(self):
        """Test richiesta approvazione."""
        session = ChatSession("session_1")
        approval = session.request_approval(
            "req_1", "Add auth", ["auth.py"], ["login()"], "medium", "Added JWT"
        )
        
        assert approval.request_id == "req_1"
        assert "auth.py" in approval.files_changed
        assert approval.risk_level == "medium"

    def test_get_history(self):
        """Test storico messaggi."""
        session = ChatSession("session_1")
        session.add_message("user", "msg1")
        session.add_message("agent", "msg2")
        
        history = session.get_history()
        
        assert len(history) == 2
        assert history[0]["sender"] == "user"
        assert history[1]["sender"] == "agent"

    def test_get_status(self):
        """Test status sessione."""
        session = ChatSession("session_1")
        session.add_message("user", "test")
        
        status = session.get_status()
        
        assert status["session_id"] == "session_1"
        assert status["messages_count"] == 1


class TestChatSessionManager:
    """Test ChatSessionManager."""

    def test_create_session(self):
        """Test creazione sessione."""
        manager = ChatSessionManager()
        session = manager.create_session("s1")
        
        assert session is not None
        assert manager.get_session("s1") is not None

    def test_get_session(self):
        """Test get sessione."""
        manager = ChatSessionManager()
        manager.create_session("s1")
        
        session = manager.get_session("s1")
        assert session is not None
        assert session.session_id == "s1"

    def test_close_session(self):
        """Test chiusura sessione."""
        manager = ChatSessionManager()
        manager.create_session("s1")
        
        result = manager.close_session("s1")
        
        assert result is True
        assert manager.get_session("s1") is None

    def test_get_active_sessions(self):
        """Test sessioni attive."""
        manager = ChatSessionManager()
        manager.create_session("s1")
        manager.create_session("s2")
        
        sessions = manager.get_active_sessions()
        
        assert len(sessions) == 2
        assert "s1" in sessions


class TestWebSocketAPI:
    """Test WebSocketAPI."""

    def test_api_creation(self):
        """Test creazione API."""
        api = create_websocket_api()
        assert api is not None
        assert isinstance(api, WebSocketAPI)

    @pytest.mark.asyncio
    async def test_handle_user_message(self):
        """Test gestione messaggio utente."""
        api = create_websocket_api()
        api.session_manager.create_session("s1")
        
        result = await api.handle_user_message("s1", "Hello")
        
        assert result["status"] == "received"
        assert result["session_id"] == "s1"

    @pytest.mark.asyncio
    async def test_update_task_status(self):
        """Test aggiornamento task."""
        api = create_websocket_api()
        api.session_manager.create_session("s1")
        
        await api.update_task_status("s1", "t1", TaskStatus.IMPLEMENTING, "Coding", 50)
        
        # Verify message was queued
        messages = await api.get_messages("s1")
        assert len(messages) > 0

    @pytest.mark.asyncio
    async def test_request_approval(self):
        """Test richiesta approvazione."""
        api = create_websocket_api()
        api.session_manager.create_session("s1")
        
        req_id = await api.request_approval(
            "s1", "Add auth", ["auth.py"], ["login()"], "medium", "JWT"
        )
        
        assert req_id != ""
        
        messages = await api.get_messages("s1")
        assert len(messages) > 0

    @pytest.mark.asyncio
    async def test_get_messages(self):
        """Test recupero messaggi."""
        api = create_websocket_api()
        api.session_manager.create_session("s1")
        
        await api.update_task_status("s1", "t1", TaskStatus.DONE, "Complete", 100)
        
        messages = await api.get_messages("s1")
        
        assert len(messages) > 0
        assert messages[0]["type"] == MessageType.TASK_UPDATE.value


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

