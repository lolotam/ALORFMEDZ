"""
Activity Logging Module
Logging and history functions
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from flask import session

from .base import load_data, save_data, generate_id


def log_activity(action: str, entity_type: str, entity_id: str = None, details: Dict = None):
    """Log user activity for audit trail"""
    try:
        history = load_data('history')

        log_entry = {
            'id': generate_id('history'),
            'timestamp': datetime.now().isoformat(),
            'user_id': session.get('user_id', 'system'),
            'username': session.get('username', 'system'),
            'role': session.get('role', 'system'),
            'department_id': session.get('department_id'),
            'action': action,  # CREATE, UPDATE, DELETE, LOGIN, LOGOUT, VIEW
            'entity_type': entity_type,  # medicine, patient, supplier, etc.
            'entity_id': entity_id,
            'details': details or {},
            'ip_address': 'localhost',  # Could be enhanced with real IP
            'user_agent': 'Flask App'   # Could be enhanced with real user agent
        }

        history.append(log_entry)
        save_data('history', history)

    except Exception as e:
        # Don't let logging errors break the main functionality
        print(f"Logging error: {e}")


def get_history(limit: int = 100, user_id: str = None, entity_type: str = None) -> List[Dict]:
    """Get activity history with optional filtering"""
    history = load_data('history')

    # Apply filters
    if user_id:
        history = [h for h in history if h.get('user_id') == user_id]

    if entity_type:
        history = [h for h in history if h.get('entity_type') == entity_type]

    # Sort by timestamp (newest first) and limit
    history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

    return history[:limit]


def get_user_activity_summary(user_id: str) -> Dict:
    """Get activity summary for a specific user"""
    history = load_data('history')
    user_history = [h for h in history if h.get('user_id') == user_id]

    if not user_history:
        return {
            'total_actions': 0,
            'last_login': None,
            'most_common_action': None,
            'entities_modified': 0
        }

    # Count actions
    action_counts = {}
    entities = set()
    last_login = None

    for entry in user_history:
        action = entry.get('action', 'UNKNOWN')
        action_counts[action] = action_counts.get(action, 0) + 1

        if entry.get('entity_id'):
            entities.add(f"{entry.get('entity_type', '')}:{entry.get('entity_id', '')}")

        if action == 'LOGIN':
            if not last_login or entry.get('timestamp', '') > last_login:
                last_login = entry.get('timestamp')

    most_common_action = max(action_counts.items(), key=lambda x: x[1])[0] if action_counts else None

    return {
        'total_actions': len(user_history),
        'last_login': last_login,
        'most_common_action': most_common_action,
        'entities_modified': len(entities),
        'action_breakdown': action_counts
    }


__all__ = [
    'log_activity', 'get_history', 'get_user_activity_summary', 'update_history_record'
]


def update_history_record(record_id: str, new_details: Dict) -> bool:
    """Update details of a history record (e.g. adding notes)"""
    try:
        history = load_data('history')
        for i, record in enumerate(history):
            # History IDs might be timestamps or generated IDs
            # We check both 'id' and 'timestamp' for backward compatibility
            if record.get('id') == record_id or record.get('timestamp') == record_id:
                # Merge new details
                if 'details' not in history[i]:
                    history[i]['details'] = {}
                
                # Update details
                history[i]['details'].update(new_details)
                
                save_data('history', history)
                return True
                
        return False
    except Exception as e:
        print(f"Error updating history: {e}")
        return False
