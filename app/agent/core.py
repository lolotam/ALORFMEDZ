"""
Core Agent Module
Main PharmacyAIAgent class for processing natural language commands
"""

import re
from typing import Dict, List, Any, Optional
from app.patterns import query_patterns, intent_patterns, entity_mappings
from app.utils.confirmation_system import ConfirmationSystem
from app.utils.chatbot_database import ChatbotDatabaseManager
from app.utils.database import log_activity
from .handlers import handler_registry


class PharmacyAIAgent:
    """Enhanced AI Agent for handling natural language pharmacy management commands

    Features:
    - Comprehensive database query support for all tables
    - Interactive confirmation system with clarifying questions
    - Intelligent spelling and grammar correction
    - Advanced natural language processing
    - Fuzzy matching for error tolerance
    """

    def __init__(self):
        """Initialize the agent"""
        # Load comprehensive patterns
        self.command_patterns = query_patterns.get_patterns()
        self.clarification_options = query_patterns.get_clarification_options

        # Initialize subsystems
        self.confirmation_system = ConfirmationSystem()
        self.chatbot_db = ChatbotDatabaseManager()

        # Legacy patterns for backward compatibility
        self.legacy_patterns = self._build_legacy_patterns()

        self.confirmation_required = [
            'delete_medicine', 'delete_patient', 'delete_supplier',
            'delete_department', 'transfer_inventory'
        ]

    def _build_legacy_patterns(self) -> Dict[str, List[str]]:
        """Build legacy patterns for backward compatibility"""
        return {
            'highest_stock': [
                r'what.*highest.*stock',
                r'which.*medicine.*most.*stock',
                r'highest.*stock.*medicine'
            ],
            'top_patients': [
                r'which.*patient.*consumed.*most',
                r'top.*consuming.*patient',
                r'patient.*most.*medicine'
            ],
            'expensive_purchases': [
                r'most.*expensive.*purchase',
                r'top.*expensive.*purchase',
                r'highest.*cost.*purchase'
            ],
            'department_analysis': [
                r'department.*lowest.*stock',
                r'which.*department.*low.*stock',
                r'department.*stock.*level'
            ],
            'expiry_analysis': [
                r'medicine.*expir.*\d+.*day',
                r'expir.*within.*\d+',
                r'medicine.*expir.*soon'
            ]
        }

    def process_command(self, user_input: str, user_id: str = None) -> Dict[str, Any]:
        """Enhanced command processing with comprehensive capabilities

        Args:
            user_input: User's natural language input
            user_id: Optional user ID for logging

        Returns:
            dict: Response with success, response, and optional data
        """
        try:
            if user_id is None:
                user_id = 'anonymous'

            # Check if user has pending confirmation
            if self.confirmation_system.has_pending_confirmation(user_id):
                return self._handle_confirmation_response(user_input, user_id)

            # Apply spelling correction
            corrected_input = entity_mappings.correct_spelling(user_input)

            # Check if query needs confirmation
            if self.confirmation_system.needs_confirmation(corrected_input, user_id):
                return self.confirmation_system.generate_confirmation_question(corrected_input, user_id)

            # Identify command type with fuzzy matching
            command_type = self._identify_command_type_enhanced(corrected_input)

            if command_type:
                # Log the command attempt
                log_activity('AI_COMMAND', 'chatbot', user_id, {
                    'command': user_input,
                    'corrected_command': corrected_input,
                    'command_type': command_type
                })

                # Execute the command using handler registry
                return self._execute_command_enhanced(command_type, corrected_input, user_id)
            else:
                # Generate "Did you mean..." suggestions
                suggestions = entity_mappings.suggest_corrections(user_input)
                return self._handle_unknown_query(user_input, suggestions)

        except Exception as e:
            return {
                'success': False,
                'response': f"I encountered an error processing your command: {str(e)}",
                'error': str(e)
            }

    def _identify_command_type_enhanced(self, user_input: str) -> Optional[str]:
        """Enhanced command type identification with fuzzy matching

        Args:
            user_input: User's input text

        Returns:
            str or None: Identified command type
        """
        user_input_lower = user_input.lower().strip()

        # First try exact pattern matching
        for command_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                if re.search(pattern, user_input_lower):
                    return command_type

        # If no exact match, try legacy patterns
        for command_type, patterns in self.legacy_patterns.items():
            for pattern in patterns:
                if re.search(pattern, user_input_lower):
                    return command_type

        # Try fuzzy matching as last resort
        fuzzy_match = entity_mappings.fuzzy_match_command(user_input, self.command_patterns)
        if fuzzy_match:
            return fuzzy_match

        return None

    def _execute_command_enhanced(self, command_type: str, user_input: str, user_id: str) -> Dict[str, Any]:
        """Execute command using handler registry

        Args:
            command_type: Type of command to execute
            user_input: Original user input
            user_id: User ID for logging

        Returns:
            dict: Command execution result
        """
        # Try handler registry first
        if handler_registry.can_handle(command_type):
            return handler_registry.handle({
                'type': command_type,
                'input': user_input,
                'user_id': user_id
            })

        # Fall back to legacy execution for advanced analytics
        return self._execute_legacy_command(command_type, user_input, user_id)

    def _execute_legacy_command(self, command_type: str, user_input: str, user_id: str) -> Dict[str, Any]:
        """Execute legacy command types that aren't in handlers yet

        Args:
            command_type: Type of command
            user_input: User input
            user_id: User ID

        Returns:
            dict: Command result
        """
        try:
            if command_type == 'highest_stock':
                return self._handle_highest_stock_query()
            elif command_type == 'top_patients':
                return self._handle_top_patients_query(user_input)
            elif command_type == 'expensive_purchases':
                return self._handle_expensive_purchases_query(user_input)
            elif command_type == 'department_analysis':
                return self._handle_department_analysis()
            elif command_type == 'expiry_analysis':
                return self._handle_expiry_analysis(user_input)
            else:
                return {
                    'success': False,
                    'response': f"Command type '{command_type}' is not yet implemented."
                }
        except Exception as e:
            return {
                'success': False,
                'response': f"Error executing command: {str(e)}",
                'error': str(e)
            }

    def _handle_confirmation_response(self, user_input: str, user_id: str) -> Dict[str, Any]:
        """Handle user's response to confirmation questions

        Args:
            user_input: User's response
            user_id: User ID

        Returns:
            dict: Response
        """
        result = self.confirmation_system.process_confirmation_response(user_input, user_id)

        if not result:
            return {
                'success': False,
                'response': "I couldn't process your response. Please try again."
            }

        if not result.get('success', False):
            return result

        # If confirmation was processed successfully, handle the choice
        if result.get('confirmation_processed'):
            if 'choice' in result:
                return self._process_confirmation_choice(result['choice'], result, user_id)
            elif 'new_query' in result:
                return self.process_command(result['new_query'], user_id)

        return result

    def _process_confirmation_choice(self, choice: str, result: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Process a confirmation choice (a, b, c, etc.)

        Args:
            choice: Selected choice letter
            result: Confirmation result data
            user_id: User ID

        Returns:
            dict: Response
        """
        return {
            'success': True,
            'response': f"You selected option '{choice}'. Processing your request...",
            'choice_processed': True
        }

    def _handle_unknown_query(self, user_input: str, suggestions: List[str]) -> Dict[str, Any]:
        """Handle unknown queries with suggestions

        Args:
            user_input: User's input
            suggestions: Suggested corrections

        Returns:
            dict: Response with suggestions
        """
        response = "I'm not sure what you're looking for. Here are some suggestions:\n\n"

        if suggestions:
            response += "**Did you mean:**\n"
            for i, suggestion in enumerate(suggestions, 1):
                response += f"{i}. {suggestion}\n"
            response += "\n"

        response += "**Or try asking about:**\n"
        response += "• Medicine information (count, list, stock levels, categories)\n"
        response += "• Patient data (list, demographics, consumption patterns)\n"
        response += "• Supplier details (list, contact info, performance)\n"
        response += "• Department information (list, staff, inventory)\n"
        response += "• Purchase records (recent, costs, by supplier)\n"
        response += "• Consumption analysis (by patient, medicine, department)\n"
        response += "• Transfer records (recent, routes, pending)\n\n"
        response += "Type 'help' to see all available commands."

        return {
            'success': True,
            'response': response,
            'suggestions': suggestions
        }

    # Legacy query handlers for advanced analytics
    def _handle_highest_stock_query(self) -> Dict[str, Any]:
        """Handle highest stock medicine query"""
        try:
            result = self.chatbot_db.get_advanced_analytics('highest_stock')

            if 'error' in result:
                return {
                    'success': False,
                    'response': f"Error getting stock data: {result['error']}"
                }

            highest_stock = result.get('highest_stock_medicine', {})
            top_10 = result.get('top_10_highest_stock', [])

            response = f"**Highest Stock Medicine:**\n"
            response += f"• **{highest_stock.get('name', 'Unknown')}** has the highest stock with **{highest_stock.get('stock', 0)} units**\n"
            response += f"• Category: {highest_stock.get('category', 'Unknown')}\n"
            response += f"• Low Stock Limit: {highest_stock.get('low_stock_limit', 0)}\n\n"

            if len(top_10) > 1:
                response += "**Top 5 Highest Stock Medicines:**\n"
                for i, med in enumerate(top_10[:5], 1):
                    response += f"{i}. {med.get('name', 'Unknown')}: {med.get('stock', 0)} units\n"

            return {
                'success': True,
                'response': response,
                'data': result
            }
        except Exception as e:
            return {
                'success': False,
                'response': f"Error analyzing stock data: {str(e)}"
            }

    def _handle_top_patients_query(self, user_input: str) -> Dict[str, Any]:
        """Handle top consuming patients query"""
        try:
            period_match = re.search(r'(\d+).*(?:day|week|month)', user_input.lower())
            period_days = 30  # default

            if period_match:
                number = int(period_match.group(1))
                if 'week' in user_input.lower():
                    period_days = number * 7
                elif 'month' in user_input.lower():
                    period_days = number * 30
                else:
                    period_days = number

            result = self.chatbot_db.get_advanced_analytics('top_consuming_patients', period_days=period_days)

            if 'error' in result:
                return {
                    'success': False,
                    'response': f"Error getting patient data: {result['error']}"
                }

            top_patients = result.get('top_consuming_patients', [])

            if not top_patients:
                return {
                    'success': True,
                    'response': f"No patient consumption data found for the last {period_days} days."
                }

            response = f"**Top Consuming Patients (Last {period_days} days):**\n\n"
            for i, patient in enumerate(top_patients[:5], 1):
                response += f"{i}. **{patient.get('patient_name', 'Unknown')}**\n"
                response += f"   • Patient ID: {patient.get('patient_id', 'Unknown')}\n"
                response += f"   • Medicines Consumed: {patient.get('consumption_count', 0)}\n"
                response += f"   • Department: {patient.get('department', 'Unknown')}\n\n"

            response += f"Total patients analyzed: {result.get('total_patients_analyzed', 0)}"

            return {
                'success': True,
                'response': response,
                'data': result
            }
        except Exception as e:
            return {
                'success': False,
                'response': f"Error analyzing patient consumption: {str(e)}"
            }

    def _handle_expensive_purchases_query(self, user_input: str) -> Dict[str, Any]:
        """Handle expensive purchases query"""
        try:
            number_match = re.search(r'top\s*(\d+)', user_input.lower())
            limit = int(number_match.group(1)) if number_match else 5

            period_match = re.search(r'(\d+).*(?:day|week|month|year)', user_input.lower())
            period_days = 365  # default to 1 year

            if period_match:
                number = int(period_match.group(1))
                if 'week' in user_input.lower():
                    period_days = number * 7
                elif 'month' in user_input.lower():
                    period_days = number * 30
                elif 'year' in user_input.lower():
                    period_days = number * 365
                else:
                    period_days = number

            result = self.chatbot_db.get_advanced_analytics('expensive_purchases', limit=limit, period_days=period_days)

            if 'error' in result:
                return {
                    'success': False,
                    'response': f"Error getting purchase data: {result['error']}"
                }

            expensive_purchases = result.get('top_expensive_purchases', [])

            if not expensive_purchases:
                return {
                    'success': True,
                    'response': f"No purchase data found for the last {period_days} days."
                }

            response = f"**Top {limit} Most Expensive Purchases (Last {period_days} days):**\n\n"
            for i, purchase in enumerate(expensive_purchases, 1):
                response += f"{i}. **Purchase ID: {purchase.get('id', 'Unknown')}**\n"
                response += f"   • Total Cost: ${float(purchase.get('total_cost', 0)):,.2f}\n"
                response += f"   • Date: {purchase.get('date', 'Unknown')}\n"
                response += f"   • Supplier: {purchase.get('supplier_name', 'Unknown')}\n"
                response += f"   • Items: {len(purchase.get('medicines', []))} medicines\n\n"

            total_cost = result.get('total_cost_analyzed', 0)
            response += f"Total cost analyzed: ${float(total_cost):,.2f}"

            return {
                'success': True,
                'response': response,
                'data': result
            }
        except Exception as e:
            return {
                'success': False,
                'response': f"Error analyzing expensive purchases: {str(e)}"
            }

    def _handle_department_analysis(self) -> Dict[str, Any]:
        """Handle department stock analysis"""
        try:
            result = self.chatbot_db.get_advanced_analytics('department_stock_analysis')

            if 'error' in result:
                return {
                    'success': False,
                    'response': f"Error getting department data: {result['error']}"
                }

            lowest_dept = result.get('lowest_average_stock_department')
            highest_dept = result.get('highest_average_stock_department')
            dept_analysis = result.get('department_stock_analysis', {})

            response = "**Department Stock Analysis:**\n\n"

            if lowest_dept:
                dept_name, dept_data = lowest_dept
                response += f"**Lowest Average Stock Department:**\n"
                response += f"• **{dept_name}**\n"
                response += f"  - Total Stock: {dept_data.get('total_stock', 0)} units\n"
                response += f"  - Unique Medicines: {dept_data.get('unique_medicines', 0)}\n"
                response += f"  - Average Stock per Medicine: {dept_data.get('average_stock_per_medicine', 0):.1f}\n\n"

            if highest_dept:
                dept_name, dept_data = highest_dept
                response += f"**Highest Average Stock Department:**\n"
                response += f"• **{dept_name}**\n"
                response += f"  - Total Stock: {dept_data.get('total_stock', 0)} units\n"
                response += f"  - Unique Medicines: {dept_data.get('unique_medicines', 0)}\n"
                response += f"  - Average Stock per Medicine: {dept_data.get('average_stock_per_medicine', 0):.1f}\n\n"

            response += "**All Departments:**\n"
            for dept_name, dept_data in sorted(dept_analysis.items(), key=lambda x: x[1]['average_stock_per_medicine']):
                response += f"• {dept_name}: {dept_data.get('average_stock_per_medicine', 0):.1f} avg stock\n"

            return {
                'success': True,
                'response': response,
                'data': result
            }
        except Exception as e:
            return {
                'success': False,
                'response': f"Error analyzing department stocks: {str(e)}"
            }

    def _handle_expiry_analysis(self, user_input: str) -> Dict[str, Any]:
        """Handle medicine expiry analysis"""
        try:
            days_match = re.search(r'(\d+).*day', user_input.lower())
            days_ahead = int(days_match.group(1)) if days_match else 30

            result = self.chatbot_db.get_advanced_analytics('expiry_analysis', days_ahead=days_ahead)

            if 'error' in result:
                return {
                    'success': False,
                    'response': f"Error getting expiry data: {result['error']}"
                }

            expiring_medicines = result.get('expiring_medicines', [])
            total_expiring = result.get('total_expiring', 0)
            total_stock = result.get('total_expiring_stock', 0)

            if not expiring_medicines:
                return {
                    'success': True,
                    'response': f"Good news! No medicines are expiring within the next {days_ahead} days."
                }

            response = f"**Medicines Expiring Within {days_ahead} Days:**\n\n"
            response += f"⚠️ **{total_expiring} medicines** with **{total_stock} total units** are expiring soon!\n\n"

            for i, medicine in enumerate(expiring_medicines[:10], 1):
                response += f"{i}. **{medicine.get('name', 'Unknown')}**\n"
                response += f"   • Expiry Date: {medicine.get('expiry_date', 'Unknown')}\n"
                response += f"   • Current Stock: {medicine.get('current_stock', 0)} units\n"
                response += f"   • Category: {medicine.get('category', 'Unknown')}\n\n"

            if len(expiring_medicines) > 10:
                response += f"...and {len(expiring_medicines) - 10} more medicines.\n\n"

            response += "**Recommendation:** Consider using these medicines soon or contact suppliers for fresh stock."

            return {
                'success': True,
                'response': response,
                'data': result
            }
        except Exception as e:
            return {
                'success': False,
                'response': f"Error analyzing expiry dates: {str(e)}"
            }


# Global instance for backward compatibility
pharmacy_agent = PharmacyAIAgent()
