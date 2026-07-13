"""
WebSocket API and Chat Interface Backend for MVP v2.

Provides real-time communication between frontend and workflow engine.
"""

import logging
import asyncio
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task status values."""
    CREATED = "created"
    ANALYZING = "analyzing"
    WAITING_APPROVAL = "waiting_approval"
    IMPLEMENTING = "implementing"
    TESTING = "testing"
    DONE = "done"
    FAILED = "failed"


class MessageType(Enum):
    """WebSocket message types."""
    USER_MESSAGE = "user_message"
    AGENT_RESPONSE = "agent_response"
    TASK_UPDATE = "task_update"
    APPROVAL_REQUEST = "approval_request"
    STATUS_UPDATE = "status_update"
    ERROR = "error"
    STREAM_START = "stream_start"
    STREAM_END = "stream_end"
    STREAM_CHUNK = "stream_chunk"


@dataclass
class ChatMessage:
    """Represents a chat message."""
    id: str
    timestamp: str
    sender: str  # "user" or "agent"
    content: str
    message_type: MessageType = MessageType.USER_MESSAGE


@dataclass
class TaskUpdate:
    """Represents a task status update."""
    task_id: str
    status: TaskStatus
    message: str
    progress: int = 0  # 0-100
    timestamp: str = ""


@dataclass
class ApprovalRequest:
    """Request for user approval."""
    request_id: str
    title: str
    files_changed: List[str]
    functions_modified: List[str]
    risk_level: str  # "low", "medium", "high"
    diff_summary: str
    timestamp: str = ""


class ChatSession:
    """
    Represents a chat session with the agent.
    
    Manages conversation history and task tracking.
    """

    def __init__(self, session_id: str, project_root: str = "."):
        """
        Initialize chat session.
        
        Args:
            session_id: Unique session identifier
            project_root: Project root directory
        """
        self.session_id = session_id
        self.project_root = project_root
        self.created_at = datetime.now()
        
        self.messages: List[ChatMessage] = []
        self.active_tasks: Dict[str, TaskUpdate] = {}
        self.approval_requests: Dict[str, ApprovalRequest] = {}
        self.project_context = {}
        
        logger.info(f"Chat session created: {session_id}")

    def add_message(self, sender: str, content: str, message_type: MessageType = MessageType.USER_MESSAGE) -> ChatMessage:
        """
        Add a message to the session.
        
        Args:
            sender: "user" or "agent"
            content: Message content
            message_type: Type of message
            
        Returns:
            ChatMessage object
        """
        message = ChatMessage(
            id=f"{self.session_id}_msg_{len(self.messages)}",
            timestamp=datetime.now().isoformat(),
            sender=sender,
            content=content,
            message_type=message_type
        )
        
        self.messages.append(message)
        logger.info(f"Message added: {sender} - {len(content)} chars")
        
        return message

    def update_task(self, task_id: str, status: TaskStatus, message: str, progress: int = 0) -> TaskUpdate:
        """
        Update a task status.
        
        Args:
            task_id: Task identifier
            status: New status
            message: Status message
            progress: Progress percentage (0-100)
            
        Returns:
            TaskUpdate object
        """
        update = TaskUpdate(
            task_id=task_id,
            status=status,
            message=message,
            progress=progress,
            timestamp=datetime.now().isoformat()
        )
        
        self.active_tasks[task_id] = update
        logger.info(f"Task updated: {task_id} → {status.value}")
        
        return update

    def request_approval(self, request_id: str, title: str, files_changed: List[str],
                        functions_modified: List[str], risk_level: str, diff_summary: str) -> ApprovalRequest:
        """
        Request user approval for changes.
        
        Args:
            request_id: Request identifier
            title: Approval title
            files_changed: List of changed files
            functions_modified: List of modified functions
            risk_level: Risk level assessment
            diff_summary: Summary of changes
            
        Returns:
            ApprovalRequest object
        """
        approval = ApprovalRequest(
            request_id=request_id,
            title=title,
            files_changed=files_changed,
            functions_modified=functions_modified,
            risk_level=risk_level,
            diff_summary=diff_summary,
            timestamp=datetime.now().isoformat()
        )
        
        self.approval_requests[request_id] = approval
        logger.info(f"Approval request: {request_id}")
        
        return approval

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get chat history.
        
        Args:
            limit: Maximum number of messages
            
        Returns:
            List of message dicts
        """
        messages = self.messages[-limit:]
        return [
            {
                "id": msg.id,
                "timestamp": msg.timestamp,
                "sender": msg.sender,
                "content": msg.content,
                "type": msg.message_type.value
            }
            for msg in messages
        ]

    def get_status(self) -> Dict[str, Any]:
        """
        Get session status.
        
        Returns:
            Status dict
        """
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "messages_count": len(self.messages),
            "active_tasks": len(self.active_tasks),
            "pending_approvals": len(self.approval_requests),
            "uptime_seconds": (datetime.now() - self.created_at).total_seconds()
        }


class ChatSessionManager:
    """
    Manages multiple chat sessions.
    """

    def __init__(self):
        """Initialize session manager."""
        self.sessions: Dict[str, ChatSession] = {}
        logger.info("Chat session manager initialized")

    def create_session(self, session_id: str, project_root: str = ".") -> ChatSession:
        """
        Create a new chat session.
        
        Args:
            session_id: Unique session identifier
            project_root: Project root directory
            
        Returns:
            ChatSession object
        """
        session = ChatSession(session_id, project_root)
        self.sessions[session_id] = session
        logger.info(f"Session created: {session_id}")
        return session

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """
        Get an existing session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            ChatSession or None
        """
        return self.sessions.get(session_id)

    def close_session(self, session_id: str) -> bool:
        """
        Close a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Success status
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Session closed: {session_id}")
            return True
        return False

    def get_active_sessions(self) -> List[str]:
        """
        Get all active session IDs.
        
        Returns:
            List of session IDs
        """
        return list(self.sessions.keys())

    def get_sessions_count(self) -> int:
        """
        Get number of active sessions.
        
        Returns:
            Number of sessions
        """
        return len(self.sessions)


class WebSocketAPI:
    """
    WebSocket API for real-time communication.
    
    Handles messages, streaming, and updates.
    """

    def __init__(self):
        """Initialize WebSocket API."""
        self.session_manager = ChatSessionManager()
        self.message_queue: Dict[str, asyncio.Queue] = {}
        logger.info("WebSocket API initialized")

    async def handle_user_message(self, session_id: str, message: str) -> Dict[str, Any]:
        """
        Handle incoming user message.
        
        Args:
            session_id: Session identifier
            message: User message
            
        Returns:
            Response dict
        """
        session = self.session_manager.get_session(session_id)
        if not session:
            return {"error": f"Session not found: {session_id}"}

        # Add message to session
        session.add_message("user", message, MessageType.USER_MESSAGE)

        # Return acknowledgment
        return {
            "status": "received",
            "session_id": session_id,
            "message_count": len(session.messages)
        }

    async def stream_agent_response(self, session_id: str, response_generator) -> None:
        """
        Stream agent response chunks.
        
        Args:
            session_id: Session identifier
            response_generator: Generator yielding response chunks
        """
        session = self.session_manager.get_session(session_id)
        if not session:
            logger.warning(f"Session not found: {session_id}")
            return

        # Send stream start
        await self._queue_message(session_id, {
            "type": MessageType.STREAM_START.value,
            "timestamp": datetime.now().isoformat()
        })

        # Stream chunks
        full_response = ""
        async for chunk in response_generator:
            full_response += chunk
            await self._queue_message(session_id, {
                "type": MessageType.STREAM_CHUNK.value,
                "chunk": chunk,
                "timestamp": datetime.now().isoformat()
            })

        # Add full message to session
        session.add_message("agent", full_response, MessageType.AGENT_RESPONSE)

        # Send stream end
        await self._queue_message(session_id, {
            "type": MessageType.STREAM_END.value,
            "timestamp": datetime.now().isoformat()
        })

    async def request_approval(self, session_id: str, title: str, files_changed: List[str],
                             functions_modified: List[str], risk_level: str, diff_summary: str) -> str:
        """
        Request user approval.
        
        Args:
            session_id: Session identifier
            title: Approval title
            files_changed: Changed files
            functions_modified: Modified functions
            risk_level: Risk level
            diff_summary: Change summary
            
        Returns:
            Approval request ID
        """
        session = self.session_manager.get_session(session_id)
        if not session:
            return ""

        request_id = f"approval_{len(session.approval_requests)}"
        approval = session.request_approval(
            request_id, title, files_changed, functions_modified, risk_level, diff_summary
        )

        # Queue approval request
        await self._queue_message(session_id, {
            "type": MessageType.APPROVAL_REQUEST.value,
            "request": {
                "id": approval.request_id,
                "title": approval.title,
                "files": approval.files_changed,
                "functions": approval.functions_modified,
                "risk": approval.risk_level,
                "diff": approval.diff_summary
            },
            "timestamp": approval.timestamp
        })

        return request_id

    async def update_task_status(self, session_id: str, task_id: str, status: TaskStatus,
                                message: str, progress: int = 0) -> None:
        """
        Update task status.
        
        Args:
            session_id: Session identifier
            task_id: Task identifier
            status: New status
            message: Status message
            progress: Progress percentage
        """
        session = self.session_manager.get_session(session_id)
        if not session:
            return

        update = session.update_task(task_id, status, message, progress)

        # Queue update
        await self._queue_message(session_id, {
            "type": MessageType.TASK_UPDATE.value,
            "task": {
                "id": update.task_id,
                "status": update.status.value,
                "message": update.message,
                "progress": update.progress
            },
            "timestamp": update.timestamp
        })

    async def _queue_message(self, session_id: str, message: Dict[str, Any]) -> None:
        """
        Queue a message for delivery.
        
        Args:
            session_id: Session identifier
            message: Message dict
        """
        if session_id not in self.message_queue:
            self.message_queue[session_id] = asyncio.Queue()

        try:
            self.message_queue[session_id].put_nowait(message)
        except asyncio.QueueFull:
            logger.warning(f"Queue full for session {session_id}")

    async def get_messages(self, session_id: str, timeout: int = 30) -> List[Dict[str, Any]]:
        """
        Get queued messages for a session.
        
        Args:
            session_id: Session identifier
            timeout: Timeout in seconds
            
        Returns:
            List of messages
        """
        if session_id not in self.message_queue:
            self.message_queue[session_id] = asyncio.Queue()

        messages = []
        queue = self.message_queue[session_id]

        try:
            while True:
                message = queue.get_nowait()
                messages.append(message)
        except asyncio.QueueEmpty:
            pass

        return messages


def create_websocket_api() -> WebSocketAPI:
    """Factory function."""
    return WebSocketAPI()

