"""
Chat History Management System
Handles persistent storage and retrieval of chatbot conversations
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import uuid4

class ChatHistoryManager:
    """Manages chat history storage and retrieval"""
    
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = data_dir
        self.chat_history_file = os.path.join(data_dir, 'chat_history.json')
        self.chat_sessions_file = os.path.join(data_dir, 'chat_sessions.json')
        self._ensure_files_exist()
    
    def _ensure_files_exist(self):
        """Ensure chat history files exist"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        if not os.path.exists(self.chat_history_file):
            with open(self.chat_history_file, 'w') as f:
                json.dump({}, f, indent=2)
        
        if not os.path.exists(self.chat_sessions_file):
            with open(self.chat_sessions_file, 'w') as f:
                json.dump({}, f, indent=2)
    
    def _load_chat_history(self) -> Dict:
        """Load chat history from file"""
        try:
            with open(self.chat_history_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_chat_history(self, history: Dict):
        """Save chat history to file"""
        with open(self.chat_history_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def _load_chat_sessions(self) -> Dict:
        """Load chat sessions from file"""
        try:
            with open(self.chat_sessions_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_chat_sessions(self, sessions: Dict):
        """Save chat sessions to file"""
        with open(self.chat_sessions_file, 'w') as f:
            json.dump(sessions, f, indent=2)
    
    def create_new_session(self, user_id: str, title: str = None) -> str:
        """Create a new chat session"""
        session_id = str(uuid4())
        timestamp = datetime.now().isoformat()
        
        sessions = self._load_chat_sessions()
        if user_id not in sessions:
            sessions[user_id] = {}
        
        sessions[user_id][session_id] = {
            'id': session_id,
            'title': title or f"Chat Session {len(sessions[user_id]) + 1}",
            'created_at': timestamp,
            'updated_at': timestamp,
            'message_count': 0
        }
        
        self._save_chat_sessions(sessions)
        
        # Initialize empty history for this session
        history = self._load_chat_history()
        if session_id not in history:
            history[session_id] = []
            self._save_chat_history(history)
        
        return session_id
    
    def get_user_sessions(self, user_id: str) -> List[Dict]:
        """Get all chat sessions for a user"""
        sessions = self._load_chat_sessions()
        user_sessions = sessions.get(user_id, {})
        
        # Convert to list and sort by updated_at (most recent first)
        session_list = list(user_sessions.values())
        session_list.sort(key=lambda x: x['updated_at'], reverse=True)
        
        return session_list
    
    def get_session_messages(self, session_id: str) -> List[Dict]:
        """Get all messages for a specific session"""
        history = self._load_chat_history()
        return history.get(session_id, [])
    
    def add_message(self, session_id: str, user_id: str, message: str, sender: str, 
                   metadata: Dict = None) -> Dict:
        """Add a message to a chat session"""
        timestamp = datetime.now().isoformat()
        
        message_data = {
            'id': str(uuid4()),
            'session_id': session_id,
            'user_id': user_id,
            'message': message,
            'sender': sender,  # 'user' or 'ai'
            'timestamp': timestamp,
            'metadata': metadata or {}
        }
        
        # Add to history
        history = self._load_chat_history()
        if session_id not in history:
            history[session_id] = []
        
        history[session_id].append(message_data)
        self._save_chat_history(history)
        
        # Update session metadata
        self._update_session_metadata(session_id, user_id)
        
        return message_data
    
    def _update_session_metadata(self, session_id: str, user_id: str):
        """Update session metadata (last updated, message count)"""
        sessions = self._load_chat_sessions()
        
        if user_id in sessions and session_id in sessions[user_id]:
            sessions[user_id][session_id]['updated_at'] = datetime.now().isoformat()
            
            # Count messages in this session
            history = self._load_chat_history()
            message_count = len(history.get(session_id, []))
            sessions[user_id][session_id]['message_count'] = message_count
            
            # Auto-generate title from first user message if not set
            if sessions[user_id][session_id]['title'].startswith('Chat Session'):
                messages = history.get(session_id, [])
                first_user_message = next((m for m in messages if m['sender'] == 'user'), None)
                if first_user_message:
                    title = first_user_message['message'][:50]
                    if len(first_user_message['message']) > 50:
                        title += "..."
                    sessions[user_id][session_id]['title'] = title
            
            self._save_chat_sessions(sessions)
    
    def delete_session(self, session_id: str, user_id: str) -> bool:
        """Delete a chat session and its messages"""
        try:
            # Remove from sessions
            sessions = self._load_chat_sessions()
            if user_id in sessions and session_id in sessions[user_id]:
                del sessions[user_id][session_id]
                self._save_chat_sessions(sessions)
            
            # Remove from history
            history = self._load_chat_history()
            if session_id in history:
                del history[session_id]
                self._save_chat_history(history)
            
            return True
        except Exception:
            return False
    
    def update_session_title(self, session_id: str, user_id: str, new_title: str) -> bool:
        """Update the title of a chat session"""
        try:
            sessions = self._load_chat_sessions()
            if user_id in sessions and session_id in sessions[user_id]:
                sessions[user_id][session_id]['title'] = new_title
                sessions[user_id][session_id]['updated_at'] = datetime.now().isoformat()
                self._save_chat_sessions(sessions)
                return True
            return False
        except Exception:
            return False
    
    def get_session_context(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Get recent messages from a session for context"""
        messages = self.get_session_messages(session_id)
        return messages[-limit:] if messages else []
    
    def search_messages(self, user_id: str, query: str, limit: int = 50) -> List[Dict]:
        """Search messages across all user sessions"""
        results = []
        sessions = self.get_user_sessions(user_id)
        
        for session in sessions:
            messages = self.get_session_messages(session['id'])
            for message in messages:
                if query.lower() in message['message'].lower():
                    message['session_title'] = session['title']
                    results.append(message)
                    if len(results) >= limit:
                        return results
        
        return results
    
    def get_user_stats(self, user_id: str) -> Dict:
        """Get statistics about user's chat history"""
        sessions = self.get_user_sessions(user_id)
        total_messages = sum(session.get('message_count', 0) for session in sessions)
        
        return {
            'total_sessions': len(sessions),
            'total_messages': total_messages,
            'most_recent_session': sessions[0] if sessions else None,
            'oldest_session': sessions[-1] if sessions else None
        }

# Global instance
chat_history_manager = ChatHistoryManager()
