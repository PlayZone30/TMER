from collections import defaultdict
from media_handler import MediaHandler
import asyncio
import uuid

class SessionManager:
    def __init__(self):
        self.active_sessions = {}
        self.session_locks = defaultdict(asyncio.Lock)
        self.max_concurrent_sessions = 100

    async def create_session(self):
        """Create a new session if under the concurrent limit."""
        if len(self.active_sessions) >= self.max_concurrent_sessions:
            return None, "Maximum concurrent sessions reached"

        session_id = str(uuid.uuid4())
        self.active_sessions[session_id] = MediaHandler(session_id)
        return session_id, "Session created successfully"

    async def get_session(self, session_id):
        """Get an existing session."""
        return self.active_sessions.get(session_id)

    async def end_session(self, session_id):
        """End a session and save all data."""
        if session_id in self.active_sessions:
            async with self.session_locks[session_id]:
                session = self.active_sessions[session_id]
                session.save_session()
                del self.active_sessions[session_id]
                del self.session_locks[session_id] 