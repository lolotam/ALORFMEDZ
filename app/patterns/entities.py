"""
Entity Keyword Mappings
Defines entity type keywords and variations for matching
"""

from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import difflib


class EntityMappings:
    """Entity keyword mappings for chatbot queries"""

    # Common medical/pharmacy terms and their variations
    MEDICAL_TERMS = {
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

    # Common abbreviations
    ABBREVIATIONS = {
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

    # Entity type to keyword mappings for query classification
    ENTITY_KEYWORDS = {
        'medicines': ['medicine', 'medication', 'drug', 'pill', 'tablet', 'capsule', 'med', 'meds'],
        'patients': ['patient', 'person', 'individual', 'case', 'client'],
        'suppliers': ['supplier', 'vendor', 'provider', 'company', 'distributor'],
        'departments': ['department', 'dept', 'division', 'section', 'unit', 'ward'],
        'stores': ['store', 'storage', 'warehouse', 'inventory', 'stock'],
        'purchases': ['purchase', 'buy', 'order', 'procurement', 'acquisition'],
        'consumption': ['consumption', 'usage', 'use', 'taken', 'consumed', 'dispensed'],
        'transfers': ['transfer', 'move', 'shift', 'relocate', 'transport']
    }

    def __init__(self):
        """Initialize entity mappings"""
        self._build_reverse_mappings()

    def _build_reverse_mappings(self) -> None:
        """Build reverse mappings for efficient lookup"""
        self._term_to_category = {}
        self._abbreviation_to_term = {}

        for category, terms in self.MEDICAL_TERMS.items():
            for term in terms:
                self._term_to_category[term] = category

        for abbrev, full in self.ABBREVIATIONS.items():
            self._abbreviation_to_term[abbrev] = full

    def correct_spelling(self, text: str, threshold: float = 0.6) -> str:
        """Correct spelling errors in the input text

        Args:
            text: Input text
            threshold: Similarity threshold for corrections

        Returns:
            str: Corrected text
        """
        words = text.lower().split()
        corrected_words = []

        for word in words:
            # Check abbreviations first
            if word in self.ABBREVIATIONS:
                corrected_words.append(self.ABBREVIATIONS[word])
                continue

            # Find best match among medical terms
            best_match = self._find_best_term_match(word, threshold)
            if best_match:
                corrected_words.append(best_match)
            else:
                corrected_words.append(word)

        return ' '.join(corrected_words)

    def _find_best_term_match(self, word: str, threshold: float) -> Optional[str]:
        """Find the best matching term for a word

        Args:
            word: Word to match
            threshold: Minimum similarity threshold

        Returns:
            str or None: Best matching term
        """
        best_match = None
        best_score = 0

        for category, terms in self.MEDICAL_TERMS.items():
            for term in terms:
                similarity = difflib.SequenceMatcher(None, word, term).ratio()
                if similarity > best_score and similarity >= threshold:
                    best_score = similarity
                    best_match = term

        return best_match

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract entities (medicines, patients, etc.) from text

        Args:
            text: Input text

        Returns:
            dict: Entity type to list of matched terms
        """
        entities = defaultdict(list)
        text_lower = text.lower()

        # Extract entity types mentioned
        for entity_type, keywords in self.ENTITY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    entities[entity_type].append(keyword)

        return dict(entities)

    def get_entity_keywords(self, entity_type: str) -> List[str]:
        """Get keywords for a specific entity type

        Args:
            entity_type: Entity type name

        Returns:
            list: List of keywords
        """
        return self.ENTITY_KEYWORDS.get(entity_type, [])

    def get_all_entity_types(self) -> List[str]:
        """Get all available entity types

        Returns:
            list: List of entity types
        """
        return list(self.ENTITY_KEYWORDS.keys())

    def suggest_corrections(self, text: str, max_suggestions: int = 3) -> List[str]:
        """Suggest possible corrections for the input text

        Args:
            text: Input text
            max_suggestions: Maximum number of suggestions

        Returns:
            list: List of suggested corrections
        """
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
        """Get potential matches for a single word

        Args:
            word: Word to match

        Returns:
            list: List of matching terms
        """
        matches = []

        # Check abbreviations
        if word in self.ABBREVIATIONS:
            matches.append(self.ABBREVIATIONS[word])

        # Check medical terms
        for category, terms in self.MEDICAL_TERMS.items():
            for term in terms:
                similarity = difflib.SequenceMatcher(None, word, term).ratio()
                if similarity > 0.5:
                    matches.append(term)

        # Return unique matches
        return list(set(matches))


# Global instance
entity_mappings = EntityMappings()
