"""
Interactive Confirmation System for Chatbot
Provides clarifying questions and confirmation before executing queries
"""

import json
import re
from typing import Dict, List, Optional, Any, Tuple
from app.patterns import entity_mappings, query_patterns

class ConfirmationSystem:
    """Interactive confirmation system for chatbot queries"""
    
    def __init__(self):
        self.pending_confirmations = {}  # Store pending confirmations by user_id
        self.entity_keywords = {
            'medicines': ['medicine', 'medication', 'drug', 'pill', 'tablet', 'med'],
            'patients': ['patient', 'person', 'individual', 'case', 'client'],
            'suppliers': ['supplier', 'vendor', 'provider', 'company'],
            'departments': ['department', 'dept', 'division', 'section', 'unit'],
            'stores': ['store', 'storage', 'warehouse', 'inventory'],
            'purchases': ['purchase', 'buy', 'order', 'procurement'],
            'consumption': ['consumption', 'usage', 'use', 'taken', 'consumed'],
            'transfers': ['transfer', 'move', 'shift', 'relocate']
        }
    
    def needs_confirmation(self, user_input: str, user_id: str) -> bool:
        """Check if the query needs confirmation/clarification"""
        # Correct spelling first
        corrected_input = entity_mappings.correct_spelling(user_input)

        # Check if query is ambiguous
        entity_mentions = self._count_entity_mentions(corrected_input)

        # If multiple entities mentioned or query is very general, need confirmation
        if len(entity_mentions) > 1 or self._is_general_query(corrected_input):
            return True

        # If single entity but no specific action, need confirmation
        if len(entity_mentions) == 1:
            entity_type = list(entity_mentions.keys())[0]
            if not self._has_specific_action(corrected_input):
                return True

        # If no clear entity or action detected, need confirmation
        if len(entity_mentions) == 0 and not self._has_clear_intent(corrected_input):
            return True

        return False
    
    def generate_confirmation_question(self, user_input: str, user_id: str) -> Dict[str, Any]:
        """Generate a confirmation question for ambiguous queries"""
        corrected_input = entity_mappings.correct_spelling(user_input)
        entity_mentions = self._count_entity_mentions(corrected_input)

        # Store the original query for later processing
        self.pending_confirmations[user_id] = {
            'original_query': user_input,
            'corrected_query': corrected_input,
            'timestamp': json.dumps({'timestamp': str(hash(user_input))})  # Simple timestamp
        }

        if len(entity_mentions) > 1:
            # Multiple entities mentioned
            return self._generate_multi_entity_question(entity_mentions, user_id)
        elif len(entity_mentions) == 1:
            # Single entity, need action clarification
            entity_type = list(entity_mentions.keys())[0]
            return self._generate_single_entity_question(entity_type, user_id)
        else:
            # No clear entity, ask what they want to know about
            return self._generate_general_question(user_id)
    
    def process_confirmation_response(self, response: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Process the user's confirmation response"""
        if user_id not in self.pending_confirmations:
            return None
        
        pending = self.pending_confirmations[user_id]
        response_lower = response.lower().strip()
        
        # Check if it's a letter choice (a, b, c, etc.)
        if len(response_lower) == 1 and response_lower.isalpha():
            return self._process_letter_choice(response_lower, pending, user_id)
        
        # Check if it's a number choice
        if response_lower.isdigit():
            return self._process_number_choice(int(response_lower), pending, user_id)
        
        # Check if it's a descriptive response
        return self._process_descriptive_response(response, pending, user_id)
    
    def _count_entity_mentions(self, text: str) -> Dict[str, int]:
        """Count mentions of different entity types in the text"""
        mentions = {}
        text_lower = text.lower()
        
        for entity_type, keywords in self.entity_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            if count > 0:
                mentions[entity_type] = count
        
        return mentions
    
    def _is_general_query(self, text: str) -> bool:
        """Check if the query is very general"""
        general_patterns = [
            r'show.*everything',
            r'tell.*me.*about',
            r'what.*can.*you.*do',
            r'help.*me',
            r'i.*want.*to.*know',
            r'give.*me.*information'
        ]
        
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in general_patterns)
    
    def _has_specific_action(self, text: str) -> bool:
        """Check if the query has a specific action"""
        action_patterns = [
            r'count', r'list', r'show', r'analyze', r'compare',
            r'find', r'search', r'get', r'display', r'total'
        ]
        
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in action_patterns)
    
    def _has_clear_intent(self, text: str) -> bool:
        """Check if the query has clear intent"""
        intent = intent_patterns.identify_intent(text)
        return intent is not None
    
    def _generate_multi_entity_question(self, entity_mentions: Dict[str, int], user_id: str) -> Dict[str, Any]:
        """Generate question for queries mentioning multiple entities"""
        entities = list(entity_mentions.keys())
        
        response = "I see you're asking about multiple things. Which would you like to focus on?\n\n"
        
        options = {}
        for i, entity in enumerate(entities, 1):
            letter = chr(ord('a') + i - 1)
            options[letter] = f"{entity.title()} information"
            response += f"**({letter})** {entity.title()} information\n"
        
        response += f"**({chr(ord('a') + len(entities))})** All of the above\n"
        response += f"**({chr(ord('a') + len(entities) + 1)})** Something else\n\n"
        response += "Please type the letter of your choice (a, b, c, etc.)"
        
        return {
            'success': True,
            'response': response,
            'awaiting_confirmation': True,
            'confirmation_type': 'multi_entity',
            'options': options
        }
    
    def _generate_single_entity_question(self, entity_type: str, user_id: str) -> Dict[str, Any]:
        """Generate question for single entity queries"""
        options = query_patterns.get_clarification_options(entity_type)

        if not options:
            return self._generate_general_question(user_id)

        response = f"I understand you want to know about {entity_type}. What specifically would you like to see?\n\n"

        for key, description in options.items():
            response += f"**({key})** {description}\n"

        response += "\nPlease type the letter of your choice (a, b, c, etc.)"

        return {
            'success': True,
            'response': response,
            'awaiting_confirmation': True,
            'confirmation_type': 'single_entity',
            'entity_type': entity_type,
            'options': options
        }

    def _generate_general_question(self, user_id: str) -> Dict[str, Any]:
        """Generate general question when no clear entity is detected"""
        response = "I'd be happy to help! What would you like to know about?\n\n"

        entity_types = query_patterns.get_all_entity_types()
        options = {}

        for i, entity_type in enumerate(entity_types, 1):
            letter = chr(ord('a') + i - 1)
            options[letter] = entity_type.title()
            response += f"**({letter})** {entity_type.title()}\n"

        response += f"**({chr(ord('a') + len(entity_types))})** General database overview\n"
        response += f"**({chr(ord('a') + len(entity_types) + 1)})** Something else\n\n"
        response += "Please type the letter of your choice (a, b, c, etc.)"

        return {
            'success': True,
            'response': response,
            'awaiting_confirmation': True,
            'confirmation_type': 'general',
            'options': options
        }
    
    def _process_letter_choice(self, choice: str, pending: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Process a letter choice response"""
        # Clear the pending confirmation
        del self.pending_confirmations[user_id]
        
        # Return the processed choice for the main agent to handle
        return {
            'success': True,
            'choice': choice,
            'original_query': pending['original_query'],
            'corrected_query': pending['corrected_query'],
            'confirmation_processed': True
        }
    
    def _process_number_choice(self, choice: int, pending: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Process a number choice response"""
        # Convert number to letter
        if 1 <= choice <= 26:
            letter_choice = chr(ord('a') + choice - 1)
            return self._process_letter_choice(letter_choice, pending, user_id)
        
        return {
            'success': False,
            'response': "Invalid choice. Please select a valid option (a, b, c, etc.)"
        }
    
    def _process_descriptive_response(self, response: str, pending: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Process a descriptive response"""
        # Try to match the response to available options
        corrected_response = entity_mappings.correct_spelling(response)

        # Clear the pending confirmation
        del self.pending_confirmations[user_id]

        # Return the new query for processing
        return {
            'success': True,
            'new_query': corrected_response,
            'original_query': pending['original_query'],
            'confirmation_processed': True
        }
    
    def has_pending_confirmation(self, user_id: str) -> bool:
        """Check if user has a pending confirmation"""
        return user_id in self.pending_confirmations
    
    def clear_pending_confirmation(self, user_id: str):
        """Clear pending confirmation for a user"""
        if user_id in self.pending_confirmations:
            del self.pending_confirmations[user_id]

# Global instance
confirmation_system = ConfirmationSystem()
