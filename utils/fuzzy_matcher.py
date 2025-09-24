"""
Fuzzy Matching and Spelling Correction for Chatbot
Provides intelligent spelling correction and context-aware query matching
"""

import re
import difflib
from typing import List, Dict, Tuple, Optional, Any
from collections import defaultdict

class FuzzyMatcher:
    """Intelligent fuzzy matching and spelling correction for chatbot queries"""
    
    def __init__(self):
        # Common medical/pharmacy terms and their variations
        self.medical_terms = {
            'medicine': ['medicine', 'medication', 'drug', 'pill', 'tablet', 'capsule', 'med', 'meds'],
            'patient': ['patient', 'person', 'individual', 'case', 'client'],
            'supplier': ['supplier', 'vendor', 'provider', 'company', 'distributor'],
            'department': ['department', 'dept', 'division', 'section', 'unit', 'ward'],
            'store': ['store', 'storage', 'warehouse', 'inventory', 'stock'],
            'purchase': ['purchase', 'buy', 'order', 'procurement', 'acquisition'],
            'consumption': ['consumption', 'usage', 'use', 'taken', 'consumed', 'dispensed'],
            'transfer': ['transfer', 'move', 'shift', 'relocate', 'transport'],
            'stock': ['stock', 'inventory', 'quantity', 'amount', 'level'],
            'analysis': ['analysis', 'report', 'summary', 'overview', 'breakdown'],
            'count': ['count', 'number', 'total', 'amount', 'quantity', 'how many'],
            'list': ['list', 'show', 'display', 'give', 'provide', 'get'],
            'all': ['all', 'every', 'complete', 'entire', 'full', 'total'],
            'highest': ['highest', 'maximum', 'most', 'top', 'largest', 'biggest'],
            'lowest': ['lowest', 'minimum', 'least', 'bottom', 'smallest'],
            'expired': ['expired', 'expiring', 'expiry', 'expire', 'outdated'],
            'low': ['low', 'running out', 'shortage', 'insufficient', 'depleted'],
            'high': ['high', 'abundant', 'plenty', 'sufficient', 'excess']
        }
        
        # Query intent patterns
        self.intent_patterns = {
            'count_query': ['how many', 'count', 'total number', 'number of'],
            'list_query': ['list', 'show me', 'give me', 'display', 'what are'],
            'analysis_query': ['analyze', 'analysis', 'breakdown', 'summary', 'overview'],
            'comparison_query': ['compare', 'versus', 'vs', 'difference between'],
            'search_query': ['find', 'search', 'look for', 'locate'],
            'status_query': ['status', 'condition', 'state', 'situation']
        }
        
        # Common abbreviations
        self.abbreviations = {
            'med': 'medicine',
            'meds': 'medicines',
            'pt': 'patient',
            'pts': 'patients',
            'dept': 'department',
            'depts': 'departments',
            'qty': 'quantity',
            'amt': 'amount',
            'inv': 'inventory',
            'exp': 'expired',
            'supp': 'supplier',
            'supps': 'suppliers'
        }
    
    def correct_spelling(self, text: str, threshold: float = 0.6) -> str:
        """Correct spelling errors in the input text"""
        words = text.lower().split()
        corrected_words = []
        
        for word in words:
            # Check abbreviations first
            if word in self.abbreviations:
                corrected_words.append(self.abbreviations[word])
                continue
            
            # Find best match among medical terms
            best_match = self._find_best_medical_term_match(word, threshold)
            if best_match:
                corrected_words.append(best_match)
            else:
                corrected_words.append(word)
        
        return ' '.join(corrected_words)
    
    def _find_best_medical_term_match(self, word: str, threshold: float) -> Optional[str]:
        """Find the best matching medical term for a word"""
        best_match = None
        best_score = 0
        
        for category, terms in self.medical_terms.items():
            for term in terms:
                # Calculate similarity
                similarity = difflib.SequenceMatcher(None, word, term).ratio()
                if similarity > best_score and similarity >= threshold:
                    best_score = similarity
                    best_match = term
        
        return best_match
    
    def suggest_corrections(self, text: str, max_suggestions: int = 3) -> List[str]:
        """Suggest possible corrections for the input text"""
        suggestions = []
        words = text.lower().split()
        
        # Generate variations by correcting individual words
        for i, word in enumerate(words):
            matches = self._get_word_matches(word)
            for match in matches[:2]:  # Top 2 matches per word
                corrected_words = words.copy()
                corrected_words[i] = match
                suggestion = ' '.join(corrected_words)
                if suggestion != text.lower() and suggestion not in suggestions:
                    suggestions.append(suggestion)
        
        return suggestions[:max_suggestions]
    
    def _get_word_matches(self, word: str) -> List[str]:
        """Get potential matches for a single word"""
        matches = []
        
        # Check abbreviations
        if word in self.abbreviations:
            matches.append(self.abbreviations[word])
        
        # Check medical terms
        for category, terms in self.medical_terms.items():
            for term in terms:
                similarity = difflib.SequenceMatcher(None, word, term).ratio()
                if similarity > 0.5:
                    matches.append((term, similarity))
        
        # Sort by similarity and return terms only
        matches.sort(key=lambda x: x[1] if isinstance(x, tuple) else 0, reverse=True)
        return [match[0] if isinstance(match, tuple) else match for match in matches]
    
    def identify_intent(self, text: str) -> Optional[str]:
        """Identify the intent of the query"""
        text_lower = text.lower()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return intent
        
        return None
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract entities (medicines, patients, etc.) from text"""
        entities = defaultdict(list)
        text_lower = text.lower()
        
        # Extract entity types mentioned
        for category, terms in self.medical_terms.items():
            for term in terms:
                if term in text_lower:
                    entities[category].append(term)
        
        return dict(entities)
    
    def fuzzy_match_command(self, user_input: str, command_patterns: Dict[str, List[str]], threshold: float = 0.7) -> Optional[str]:
        """Fuzzy match user input against command patterns"""
        corrected_input = self.correct_spelling(user_input)
        
        best_match = None
        best_score = 0
        
        for command_type, patterns in command_patterns.items():
            for pattern in patterns:
                # Convert regex pattern to plain text for comparison
                plain_pattern = re.sub(r'[.*+?^${}()|[\]\\]', ' ', pattern).strip()
                
                # Calculate similarity
                similarity = difflib.SequenceMatcher(None, corrected_input.lower(), plain_pattern.lower()).ratio()
                
                if similarity > best_score and similarity >= threshold:
                    best_score = similarity
                    best_match = command_type
        
        return best_match
    
    def generate_did_you_mean(self, user_input: str, command_patterns: Dict[str, List[str]]) -> List[str]:
        """Generate 'Did you mean...' suggestions"""
        suggestions = []
        corrected_input = self.correct_spelling(user_input)
        
        # Get spelling corrections
        spelling_suggestions = self.suggest_corrections(user_input)
        suggestions.extend(spelling_suggestions)
        
        # Get command pattern matches
        for command_type, patterns in command_patterns.items():
            for pattern in patterns:
                plain_pattern = re.sub(r'[.*+?^${}()|[\]\\]', ' ', pattern).strip()
                similarity = difflib.SequenceMatcher(None, corrected_input.lower(), plain_pattern.lower()).ratio()
                
                if 0.4 <= similarity < 0.7:  # Moderate similarity
                    # Convert pattern to readable suggestion
                    readable_suggestion = self._pattern_to_readable(plain_pattern)
                    if readable_suggestion not in suggestions:
                        suggestions.append(readable_suggestion)
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def _pattern_to_readable(self, pattern: str) -> str:
        """Convert a pattern to a readable suggestion"""
        # Simple conversion - replace common pattern elements
        readable = pattern.replace('.*', ' ')
        readable = re.sub(r'\s+', ' ', readable).strip()
        return readable
    
    def is_similar_query(self, query1: str, query2: str, threshold: float = 0.8) -> bool:
        """Check if two queries are similar"""
        corrected1 = self.correct_spelling(query1)
        corrected2 = self.correct_spelling(query2)
        
        similarity = difflib.SequenceMatcher(None, corrected1.lower(), corrected2.lower()).ratio()
        return similarity >= threshold

# Global instance
fuzzy_matcher = FuzzyMatcher()
