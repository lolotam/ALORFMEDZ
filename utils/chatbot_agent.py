"""
Enhanced AI Agent System for Pharmacy Management
Handles natural language commands with comprehensive database query support,
interactive confirmation system, intelligent spelling correction, and
advanced natural language processing capabilities
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
from utils.chatbot_database import chatbot_db
from utils.ai_prompts import get_system_prompt, get_comprehensive_data_prompt, get_specific_table_prompts
from utils.fuzzy_matcher import fuzzy_matcher
from utils.confirmation_system import confirmation_system
from utils.comprehensive_patterns import comprehensive_patterns
from utils.comprehensive_handlers import comprehensive_handlers
from utils.database import (
    save_medicine, update_medicine, delete_medicine,
    save_patient, update_patient, delete_patient,
    save_supplier, update_supplier, delete_supplier,
    save_department, update_department, delete_department,
    save_purchase, update_purchase, delete_purchase,
    save_consumption, log_activity, update_store_inventory,
    get_medicine_stock, get_medicines, get_patients, get_suppliers,
    get_departments, get_stores, get_purchases, get_consumption, get_transfers
)

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
        # Load comprehensive patterns
        self.command_patterns = comprehensive_patterns.get_patterns()

        # Legacy patterns for backward compatibility
        self.legacy_patterns = {
            # Query patterns
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
            ],

            # Comprehensive Database Analysis patterns
            'comprehensive_overview': [
                r'show.*complete.*overview.*database',
                r'comprehensive.*database.*analysis',
                r'complete.*overview.*all.*tables',
                r'show.*all.*database.*tables',
                r'comprehensive.*analysis.*all.*data'
            ],
            'medicines_analysis': [
                r'complete.*analysis.*medicines.*table',
                r'comprehensive.*medicines.*analysis',
                r'show.*all.*medicines.*data',
                r'analyze.*medicines.*table',
                r'medicines.*with.*stock.*levels'
            ],
            'medicine_names_list': [
                r'give.*me.*names.*of.*all.*medicines',
                r'show.*me.*all.*medicine.*names',
                r'list.*all.*medicines.*in.*database',
                r'what.*are.*all.*the.*medicines',
                r'show.*complete.*list.*of.*medicines',
                r'all.*medicine.*names.*in.*database',
                r'names.*of.*medicines.*in.*database',
                r'list.*all.*medicines',
                r'show.*all.*medicines',
                r'what.*medicines.*do.*we.*have',
                r'all.*medicines.*in.*database',
                r'complete.*medicine.*list'
            ],
            'patients_analysis': [
                r'complete.*analysis.*patients.*table',
                r'comprehensive.*patients.*analysis',
                r'show.*all.*patients.*data',
                r'analyze.*patients.*table',
                r'patients.*consumption.*patterns'
            ],
            'suppliers_analysis': [
                r'comprehensive.*supplier.*analysis',
                r'complete.*analysis.*suppliers',
                r'show.*all.*suppliers.*data',
                r'analyze.*suppliers.*table',
                r'supplier.*performance.*metrics'
            ],
            'departments_analysis': [
                r'complete.*analysis.*departments',
                r'comprehensive.*departments.*analysis',
                r'show.*all.*departments.*data',
                r'analyze.*departments.*table',
                r'departments.*inventory.*levels'
            ],
            'stores_analysis': [
                r'complete.*analysis.*storage.*locations',
                r'comprehensive.*stores.*analysis',
                r'show.*all.*storage.*locations',
                r'analyze.*stores.*table',
                r'storage.*inventory.*status'
            ],
            'purchases_analysis': [
                r'complete.*analysis.*purchase.*records',
                r'comprehensive.*purchases.*analysis',
                r'show.*all.*purchase.*records',
                r'analyze.*purchases.*table',
                r'purchase.*costs.*supplier.*performance'
            ],
            'consumption_analysis': [
                r'complete.*analysis.*consumption.*records',
                r'comprehensive.*consumption.*analysis',
                r'show.*all.*consumption.*records',
                r'analyze.*consumption.*table',
                r'consumption.*patient.*medicine.*details'
            ],
            'transfers_analysis': [
                r'complete.*analysis.*transfer.*records',
                r'comprehensive.*transfers.*analysis',
                r'show.*all.*transfer.*records',
                r'analyze.*transfers.*table',
                r'transfer.*department.*routes.*quantities'
            ],
            'cross_table_inventory': [
                r'analyze.*inventory.*across.*all.*stores',
                r'comprehensive.*inventory.*analysis',
                r'inventory.*optimization.*recommendations',
                r'cross.*department.*inventory.*analysis'
            ],
            'cross_table_financial': [
                r'complete.*financial.*analysis',
                r'comprehensive.*financial.*analysis',
                r'financial.*analysis.*purchases.*consumption',
                r'cost.*analysis.*across.*all.*data'
            ],
            'cross_table_performance': [
                r'performance.*metrics.*suppliers.*departments',
                r'comprehensive.*performance.*analysis',
                r'performance.*analysis.*all.*categories',
                r'supplier.*department.*medicine.*performance'
            ],

            # CRUD patterns
            'add_medicine': [
                r'add.*new.*medicine.*called',
                r'create.*medicine.*name',
                r'add.*medicine.*with'
            ],
            'add_patient': [
                r'add.*new.*patient.*called',
                r'create.*patient.*name',
                r'add.*patient.*with'
            ],
            'add_supplier': [
                r'add.*new.*supplier.*called',
                r'create.*supplier.*name',
                r'add.*supplier.*with'
            ],
            'add_department': [
                r'add.*new.*department.*called',
                r'create.*department.*name',
                r'add.*department.*with'
            ],
            'update_patient': [
                r'update.*patient.*\w+.*medical.*history',
                r'change.*patient.*\w+.*history',
                r'modify.*patient.*\w+'
            ],
            'delete_medicine': [
                r'delete.*medicine.*id.*\w+',
                r'remove.*medicine.*\w+',
                r'delete.*medicine.*with.*id'
            ],
            'transfer_inventory': [
                r'transfer.*\d+.*unit.*from.*to',
                r'move.*\d+.*medicine.*from.*to',
                r'transfer.*inventory.*from.*to'
            ]
        }
        
        self.confirmation_required = [
            'delete_medicine', 'delete_patient', 'delete_supplier',
            'delete_department', 'transfer_inventory'
        ]
    
    def process_command(self, user_input: str, user_id: str = None) -> Dict[str, Any]:
        """Enhanced command processing with comprehensive capabilities"""
        try:
            # Set default user_id if not provided
            if user_id is None:
                user_id = 'anonymous'

            # Check if user has pending confirmation
            if confirmation_system.has_pending_confirmation(user_id):
                return self._handle_confirmation_response(user_input, user_id)

            # Apply spelling correction
            corrected_input = fuzzy_matcher.correct_spelling(user_input)

            # Check if query needs confirmation
            if confirmation_system.needs_confirmation(corrected_input, user_id):
                return confirmation_system.generate_confirmation_question(corrected_input, user_id)

            # Identify command type with fuzzy matching
            command_type = self._identify_command_type_enhanced(corrected_input)

            if command_type:
                # Log the command attempt
                log_activity('AI_COMMAND', 'chatbot', user_id, {
                    'command': user_input,
                    'corrected_command': corrected_input,
                    'command_type': command_type
                })

                # Execute the command using comprehensive handlers
                return self._execute_command_enhanced(command_type, corrected_input, user_id)
            else:
                # Generate "Did you mean..." suggestions
                suggestions = fuzzy_matcher.generate_did_you_mean(user_input, self.command_patterns)
                return self._handle_unknown_query(user_input, suggestions)

        except Exception as e:
            return {
                'success': False,
                'response': f"I encountered an error processing your command: {str(e)}",
                'error': str(e)
            }
    
    def _identify_command_type(self, user_input: str) -> Optional[str]:
        """Legacy command type identification (for backward compatibility)"""
        for command_type, patterns in self.legacy_patterns.items():
            for pattern in patterns:
                if re.search(pattern, user_input):
                    return command_type
        return None

    def _identify_command_type_enhanced(self, user_input: str) -> Optional[str]:
        """Enhanced command type identification with fuzzy matching"""
        user_input_lower = user_input.lower().strip()

        # First try exact pattern matching
        for command_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                if re.search(pattern, user_input_lower):
                    return command_type

        # If no exact match, try fuzzy matching
        fuzzy_match = fuzzy_matcher.fuzzy_match_command(user_input, self.command_patterns)
        if fuzzy_match:
            return fuzzy_match

        return None

    def _handle_confirmation_response(self, user_input: str, user_id: str) -> Dict[str, Any]:
        """Handle user's response to confirmation questions"""
        result = confirmation_system.process_confirmation_response(user_input, user_id)

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
                # Handle letter choice
                return self._process_confirmation_choice(result['choice'], result, user_id)
            elif 'new_query' in result:
                # Handle new query from descriptive response
                return self.process_command(result['new_query'], user_id)

        return result

    def _process_confirmation_choice(self, choice: str, result: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Process a confirmation choice (a, b, c, etc.)"""
        # This would need to be implemented based on the specific confirmation context
        # For now, return a generic response
        return {
            'success': True,
            'response': f"You selected option '{choice}'. Processing your request...",
            'choice_processed': True
        }

    def _execute_command_enhanced(self, command_type: str, user_input: str, user_id: str) -> Dict[str, Any]:
        """Execute command using comprehensive handlers"""
        # Try comprehensive handlers first
        if command_type in comprehensive_handlers.get_available_handlers():
            return comprehensive_handlers.handle_query(command_type, user_input)

        # Fall back to legacy execution
        return self._execute_command(command_type, user_input, user_id)

    def _handle_unknown_query(self, user_input: str, suggestions: List[str]) -> Dict[str, Any]:
        """Handle unknown queries with suggestions"""
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
    
    def _execute_command(self, command_type: str, user_input: str, user_id: str) -> Dict[str, Any]:
        """Execute the identified command"""
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
            # Comprehensive Database Analysis handlers
            elif command_type == 'comprehensive_overview':
                return self._handle_comprehensive_overview()
            elif command_type == 'medicines_analysis':
                return self._handle_medicines_analysis()
            elif command_type == 'medicine_names_list':
                return self._handle_medicine_names_list()
            elif command_type == 'patients_analysis':
                return self._handle_patients_analysis()
            elif command_type == 'suppliers_analysis':
                return self._handle_suppliers_analysis()
            elif command_type == 'departments_analysis':
                return self._handle_departments_analysis()
            elif command_type == 'stores_analysis':
                return self._handle_stores_analysis()
            elif command_type == 'purchases_analysis':
                return self._handle_purchases_analysis()
            elif command_type == 'consumption_analysis':
                return self._handle_consumption_analysis()
            elif command_type == 'transfers_analysis':
                return self._handle_transfers_analysis()
            elif command_type == 'cross_table_inventory':
                return self._handle_cross_table_inventory()
            elif command_type == 'cross_table_financial':
                return self._handle_cross_table_financial()
            elif command_type == 'cross_table_performance':
                return self._handle_cross_table_performance()
            # CRUD handlers
            elif command_type == 'add_medicine':
                return self._handle_add_medicine(user_input, user_id)
            elif command_type == 'add_patient':
                return self._handle_add_patient(user_input, user_id)
            elif command_type == 'add_supplier':
                return self._handle_add_supplier(user_input, user_id)
            elif command_type == 'add_department':
                return self._handle_add_department(user_input, user_id)
            elif command_type == 'update_patient':
                return self._handle_update_patient(user_input, user_id)
            elif command_type == 'delete_medicine':
                return self._handle_delete_medicine(user_input, user_id)
            elif command_type == 'transfer_inventory':
                return self._handle_transfer_inventory(user_input, user_id)
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
    
    def _handle_highest_stock_query(self) -> Dict[str, Any]:
        """Handle highest stock medicine query"""
        try:
            result = chatbot_db.get_advanced_analytics('highest_stock')
            
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
            # Extract time period if mentioned
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
            
            result = chatbot_db.get_advanced_analytics('top_consuming_patients', period_days=period_days)
            
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
            # Extract number and time period
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
            
            result = chatbot_db.get_advanced_analytics('expensive_purchases', limit=limit, period_days=period_days)
            
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
            result = chatbot_db.get_advanced_analytics('department_stock_analysis')
            
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
            # Extract number of days
            days_match = re.search(r'(\d+).*day', user_input.lower())
            days_ahead = int(days_match.group(1)) if days_match else 30
            
            result = chatbot_db.get_advanced_analytics('expiry_analysis', days_ahead=days_ahead)
            
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
    
    def _handle_add_medicine(self, user_input: str, user_id: str) -> Dict[str, Any]:
        """Handle adding new medicine"""
        try:
            # Extract medicine details from natural language
            # Pattern: "Add a new medicine called [name] with [details]"
            name_match = re.search(r'called\s+([^,\s]+(?:\s+[^,\s]+)*)', user_input, re.IGNORECASE)

            if not name_match:
                return {
                    'success': False,
                    'response': "I couldn't extract the medicine name. Please use format: 'Add a new medicine called [name] with supplier [supplier] and dosage [dosage]'"
                }

            medicine_name = name_match.group(1).strip()

            # Extract additional details
            supplier_match = re.search(r'supplier\s+([^,\s]+(?:\s+[^,\s]+)*)', user_input, re.IGNORECASE)
            dosage_match = re.search(r'dosage\s+([^,\s]+(?:\s+[^,\s]+)*)', user_input, re.IGNORECASE)
            form_match = re.search(r'form\s+([^,\s]+)', user_input, re.IGNORECASE)
            notes_match = re.search(r'notes?\s+([^,]+)', user_input, re.IGNORECASE)

            # Get available suppliers to find a default one
            suppliers = get_suppliers()
            default_supplier_id = suppliers[0]['id'] if suppliers else '01'

            # Try to match supplier by name if provided
            supplier_id = default_supplier_id
            if supplier_match:
                supplier_name = supplier_match.group(1).strip().lower()
                for supplier in suppliers:
                    if supplier_name in supplier['name'].lower():
                        supplier_id = supplier['id']
                        break

            medicine_data = {
                'name': medicine_name,
                'supplier_id': supplier_id,
                'form_dosage': f"{form_match.group(1) if form_match else 'Tablet'} {dosage_match.group(1) if dosage_match else '1 unit'}",
                'low_stock_limit': 10,  # default
                'notes': notes_match.group(1).strip() if notes_match else f'Medicine added via AI assistant on {datetime.now().strftime("%Y-%m-%d")}'
            }

            # Save the medicine
            medicine_id = save_medicine(medicine_data)

            # Log the action
            log_activity('CREATE', 'medicine', user_id, {
                'medicine_id': medicine_id,
                'medicine_name': medicine_name,
                'via': 'AI_assistant'
            })

            # Get supplier name for response
            supplier_name = next((s['name'] for s in suppliers if s['id'] == supplier_id), 'Unknown')

            response = f"✅ **Medicine Added Successfully!**\n\n"
            response += f"• **Name:** {medicine_name}\n"
            response += f"• **ID:** {medicine_id}\n"
            response += f"• **Supplier:** {supplier_name}\n"
            response += f"• **Form/Dosage:** {medicine_data['form_dosage']}\n"
            response += f"• **Low Stock Limit:** {medicine_data['low_stock_limit']}\n"
            response += f"• **Notes:** {medicine_data['notes']}\n\n"
            response += "The medicine has been added to the system and is ready for inventory management."

            return {
                'success': True,
                'response': response,
                'data': {'medicine_id': medicine_id, 'medicine_data': medicine_data}
            }
        except Exception as e:
            return {
                'success': False,
                'response': f"Error adding medicine: {str(e)}"
            }

    def _handle_add_patient(self, user_input: str, user_id: str) -> Dict[str, Any]:
        """Handle adding new patient"""
        try:
            # Extract patient details from natural language
            # Pattern: "Add a new patient called [name] with [details]"
            name_match = re.search(r'called\s+([^,\s]+(?:\s+[^,\s]+)*)', user_input, re.IGNORECASE)

            if not name_match:
                return {
                    'success': False,
                    'response': "I couldn't extract the patient name. Please use format: 'Add a new patient called [name] with department [department] and medical history [history]'"
                }

            patient_name = name_match.group(1).strip()

            # Extract additional details
            department_match = re.search(r'department\s+([^,\s]+(?:\s+[^,\s]+)*)', user_input, re.IGNORECASE)
            history_match = re.search(r'medical\s+history\s+([^,]+)', user_input, re.IGNORECASE)
            gender_match = re.search(r'gender\s+([^,\s]+)', user_input, re.IGNORECASE)
            age_match = re.search(r'age\s+(\d+)', user_input, re.IGNORECASE)

            # Get available departments to find a default one
            departments = get_departments()
            default_department_id = departments[0]['id'] if departments else '01'

            # Try to match department by name if provided
            department_id = default_department_id
            if department_match:
                department_name = department_match.group(1).strip().lower()
                for department in departments:
                    if department_name in department['name'].lower():
                        department_id = department['id']
                        break

            patient_data = {
                'name': patient_name,
                'department_id': department_id,
                'gender': gender_match.group(1) if gender_match else 'Not specified',
                'age': int(age_match.group(1)) if age_match else 0,
                'medical_history': history_match.group(1).strip() if history_match else f'Patient added via AI assistant on {datetime.now().strftime("%Y-%m-%d")}',
                'allergies': '',
                'phone': '',
                'address': '',
                'file_no': '',
                'date_of_entry': datetime.now().strftime('%Y-%m-%d'),
                'notes': f'Patient added via AI assistant on {datetime.now().strftime("%Y-%m-%d")}'
            }

            patient_id = save_patient(patient_data)

            # Log activity
            log_activity('CREATE', 'patient', patient_id, {
                'name': patient_data['name'],
                'department_id': patient_data['department_id']
            })

            # Get department name for response
            department_name = next((d['name'] for d in departments if d['id'] == department_id), 'Unknown')

            response = f"✅ **Patient Added Successfully!**\n\n"
            response += f"• **Name:** {patient_name}\n"
            response += f"• **ID:** {patient_id}\n"
            response += f"• **Department:** {department_name}\n"
            response += f"• **Gender:** {patient_data['gender']}\n"
            response += f"• **Age:** {patient_data['age']}\n"
            response += f"• **Medical History:** {patient_data['medical_history']}\n\n"
            response += "The patient has been added to the system and is ready for medical management."

            return {
                'success': True,
                'response': response,
                'data': {'patient_id': patient_id, 'patient_data': patient_data}
            }
        except Exception as e:
            return {
                'success': False,
                'response': f"Error adding patient: {str(e)}"
            }

    def _handle_add_supplier(self, user_input: str, user_id: str) -> Dict[str, Any]:
        """Handle adding new supplier"""
        try:
            # Extract supplier details from natural language
            # Pattern: "Add a new supplier called [name] with [details]"
            name_match = re.search(r'called\s+([^,\s]+(?:\s+[^,\s]+)*)', user_input, re.IGNORECASE)

            if not name_match:
                return {
                    'success': False,
                    'response': "I couldn't extract the supplier name. Please use format: 'Add a new supplier called [name] with contact [contact] and phone [phone]'"
                }

            supplier_name = name_match.group(1).strip()

            # Extract additional details
            contact_match = re.search(r'contact\s+([^,\s]+(?:\s+[^,\s]+)*)', user_input, re.IGNORECASE)
            phone_match = re.search(r'phone\s+([^,\s]+)', user_input, re.IGNORECASE)
            email_match = re.search(r'email\s+([^,\s]+)', user_input, re.IGNORECASE)
            type_match = re.search(r'type\s+([^,\s]+)', user_input, re.IGNORECASE)

            supplier_data = {
                'name': supplier_name,
                'contact_person': contact_match.group(1).strip() if contact_match else 'Not specified',
                'phone': phone_match.group(1) if phone_match else '',
                'email': email_match.group(1) if email_match else '',
                'type': type_match.group(1) if type_match else 'Medicine',
                'address': '',
                'notes': f'Supplier added via AI assistant on {datetime.now().strftime("%Y-%m-%d")}'
            }

            supplier_id = save_supplier(supplier_data)

            # Log activity
            log_activity('CREATE', 'supplier', supplier_id, {
                'name': supplier_data['name'],
                'contact_person': supplier_data['contact_person']
            })

            response = f"✅ **Supplier Added Successfully!**\n\n"
            response += f"• **Name:** {supplier_name}\n"
            response += f"• **ID:** {supplier_id}\n"
            response += f"• **Contact Person:** {supplier_data['contact_person']}\n"
            response += f"• **Phone:** {supplier_data['phone']}\n"
            response += f"• **Email:** {supplier_data['email']}\n"
            response += f"• **Type:** {supplier_data['type']}\n\n"
            response += "The supplier has been added to the system and is ready for procurement management."

            return {
                'success': True,
                'response': response,
                'data': {'supplier_id': supplier_id, 'supplier_data': supplier_data}
            }
        except Exception as e:
            return {
                'success': False,
                'response': f"Error adding supplier: {str(e)}"
            }

    def _handle_add_department(self, user_input: str, user_id: str) -> Dict[str, Any]:
        """Handle adding new department"""
        try:
            # Extract department details from natural language
            # Pattern: "Add a new department called [name] with [details]"
            name_match = re.search(r'called\s+([^,\s]+(?:\s+[^,\s]+)*)', user_input, re.IGNORECASE)

            if not name_match:
                return {
                    'success': False,
                    'response': "I couldn't extract the department name. Please use format: 'Add a new department called [name] with responsible person [person] and phone [phone]'"
                }

            department_name = name_match.group(1).strip()

            # Extract additional details
            person_match = re.search(r'responsible\s+person\s+([^,\s]+(?:\s+[^,\s]+)*)', user_input, re.IGNORECASE)
            phone_match = re.search(r'phone\s+([^,\s]+)', user_input, re.IGNORECASE)

            department_data = {
                'name': department_name,
                'responsible_person': person_match.group(1).strip() if person_match else 'Not specified',
                'telephone': phone_match.group(1) if phone_match else '',
                'notes': f'Department added via AI assistant on {datetime.now().strftime("%Y-%m-%d")}'
            }

            department_id = save_department(department_data)

            # Auto-create corresponding store (importing the function)
            from utils.database import create_store_for_department
            create_store_for_department(department_id, department_data['name'])

            # Log activity
            log_activity('CREATE', 'department', department_id, {
                'name': department_data['name'],
                'responsible_person': department_data['responsible_person']
            })

            response = f"✅ **Department Added Successfully!**\n\n"
            response += f"• **Name:** {department_name}\n"
            response += f"• **ID:** {department_id}\n"
            response += f"• **Responsible Person:** {department_data['responsible_person']}\n"
            response += f"• **Phone:** {department_data['telephone']}\n\n"
            response += "The department has been added to the system with an associated store for inventory management."

            return {
                'success': True,
                'response': response,
                'data': {'department_id': department_id, 'department_data': department_data}
            }
        except Exception as e:
            return {
                'success': False,
                'response': f"Error adding department: {str(e)}"
            }

    def _handle_update_patient(self, user_input: str, user_id: str) -> Dict[str, Any]:
        """Handle updating patient information"""
        try:
            # Extract patient ID and new medical history
            # Pattern: "Update patient [ID] to change their medical history to [new history]"
            patient_match = re.search(r'patient\s+(\w+)', user_input, re.IGNORECASE)
            history_match = re.search(r'medical\s+history\s+to\s+(.+)', user_input, re.IGNORECASE)

            if not patient_match:
                return {
                    'success': False,
                    'response': "I couldn't extract the patient ID. Please use format: 'Update patient [ID] to change their medical history to [new history]'"
                }

            patient_id = patient_match.group(1)

            # Check if patient exists
            patients = get_patients()
            patient = next((p for p in patients if p['id'] == patient_id), None)

            if not patient:
                return {
                    'success': False,
                    'response': f"Patient with ID '{patient_id}' not found in the system."
                }

            if not history_match:
                return {
                    'success': False,
                    'response': "I couldn't extract the new medical history. Please specify what to update."
                }

            new_history = history_match.group(1).strip()

            # Update patient data
            update_data = {
                'medical_history': new_history
            }

            update_patient(patient_id, update_data)

            # Log the action
            log_activity('UPDATE', 'patient', user_id, {
                'patient_id': patient_id,
                'patient_name': patient.get('name', 'Unknown'),
                'field_updated': 'medical_history',
                'via': 'AI_assistant'
            })

            response = f"✅ **Patient Updated Successfully!**\n\n"
            response += f"• **Patient:** {patient.get('name', 'Unknown')} (ID: {patient_id})\n"
            response += f"• **Updated Field:** Medical History\n"
            response += f"• **New Medical History:** {new_history}\n\n"
            response += "The patient's medical history has been updated in the system."

            return {
                'success': True,
                'response': response,
                'data': {'patient_id': patient_id, 'updated_data': update_data}
            }
        except Exception as e:
            return {
                'success': False,
                'response': f"Error updating patient: {str(e)}"
            }

    def _handle_delete_medicine(self, user_input: str, user_id: str) -> Dict[str, Any]:
        """Handle deleting medicine (requires confirmation)"""
        try:
            # Extract medicine ID
            # Pattern: "Delete medicine with ID [ID]"
            id_match = re.search(r'id\s+(\w+)', user_input, re.IGNORECASE)

            if not id_match:
                return {
                    'success': False,
                    'response': "I couldn't extract the medicine ID. Please use format: 'Delete medicine with ID [ID]'"
                }

            medicine_id = id_match.group(1)

            # Check if medicine exists
            medicines = get_medicines()
            medicine = next((m for m in medicines if m['id'] == medicine_id), None)

            if not medicine:
                return {
                    'success': False,
                    'response': f"Medicine with ID '{medicine_id}' not found in the system."
                }

            # Check current stock
            current_stock = get_medicine_stock(medicine_id)

            # Require confirmation for deletion
            response = f"⚠️ **Deletion Confirmation Required**\n\n"
            response += f"You are about to delete:\n"
            response += f"• **Medicine:** {medicine.get('name', 'Unknown')}\n"
            response += f"• **ID:** {medicine_id}\n"
            response += f"• **Category:** {medicine.get('category', 'Unknown')}\n"
            response += f"• **Current Stock:** {current_stock} units\n\n"

            if current_stock > 0:
                response += f"⚠️ **Warning:** This medicine has {current_stock} units in stock. "
                response += "Deleting it will remove all inventory records.\n\n"

            response += "To confirm deletion, please type: **'CONFIRM DELETE MEDICINE " + medicine_id + "'**\n"
            response += "To cancel, type anything else."

            return {
                'success': True,
                'response': response,
                'requires_confirmation': True,
                'confirmation_data': {
                    'action': 'delete_medicine',
                    'medicine_id': medicine_id,
                    'medicine_name': medicine.get('name', 'Unknown'),
                    'current_stock': current_stock
                }
            }
        except Exception as e:
            return {
                'success': False,
                'response': f"Error processing delete request: {str(e)}"
            }

    def _handle_transfer_inventory(self, user_input: str, user_id: str) -> Dict[str, Any]:
        """Handle inventory transfer between departments"""
        try:
            # Extract transfer details
            # Pattern: "Transfer [quantity] units of [medicine] from [source] to [destination]"
            quantity_match = re.search(r'transfer\s+(\d+)', user_input, re.IGNORECASE)
            medicine_match = re.search(r'of\s+([^,\s]+(?:\s+[^,\s]+)*)\s+from', user_input, re.IGNORECASE)
            source_match = re.search(r'from\s+([^,\s]+(?:\s+[^,\s]+)*)\s+to', user_input, re.IGNORECASE)
            dest_match = re.search(r'to\s+([^,\s]+(?:\s+[^,\s]+)*)', user_input, re.IGNORECASE)

            if not all([quantity_match, medicine_match, source_match, dest_match]):
                return {
                    'success': False,
                    'response': "I couldn't extract all transfer details. Please use format: 'Transfer [quantity] units of [medicine] from [source department] to [destination department]'"
                }

            quantity = int(quantity_match.group(1))
            medicine_name = medicine_match.group(1).strip()
            source_dept = source_match.group(1).strip()
            dest_dept = dest_match.group(1).strip()

            # Find medicine ID
            medicines = get_medicines()
            medicine = next((m for m in medicines if m['name'].lower() == medicine_name.lower()), None)

            if not medicine:
                return {
                    'success': False,
                    'response': f"Medicine '{medicine_name}' not found in the system."
                }

            # Find department IDs
            departments = get_departments()
            source_department = next((d for d in departments if d['name'].lower() == source_dept.lower()), None)
            dest_department = next((d for d in departments if d['name'].lower() == dest_dept.lower()), None)

            if not source_department:
                return {
                    'success': False,
                    'response': f"Source department '{source_dept}' not found."
                }

            if not dest_department:
                return {
                    'success': False,
                    'response': f"Destination department '{dest_dept}' not found."
                }

            # Check source stock
            source_stock = get_medicine_stock(medicine['id'], source_department['id'])

            if source_stock < quantity:
                return {
                    'success': False,
                    'response': f"Insufficient stock in {source_dept}. Available: {source_stock} units, Requested: {quantity} units."
                }

            # Require confirmation for transfer
            response = f"🔄 **Transfer Confirmation Required**\n\n"
            response += f"Transfer Details:\n"
            response += f"• **Medicine:** {medicine['name']}\n"
            response += f"• **Quantity:** {quantity} units\n"
            response += f"• **From:** {source_department['name']} (Current stock: {source_stock})\n"
            response += f"• **To:** {dest_department['name']}\n\n"
            response += f"To confirm transfer, please type: **'CONFIRM TRANSFER {medicine['id']} {quantity} {source_department['id']} {dest_department['id']}'**\n"
            response += "To cancel, type anything else."

            return {
                'success': True,
                'response': response,
                'requires_confirmation': True,
                'confirmation_data': {
                    'action': 'transfer_inventory',
                    'medicine_id': medicine['id'],
                    'medicine_name': medicine['name'],
                    'quantity': quantity,
                    'source_dept_id': source_department['id'],
                    'source_dept_name': source_department['name'],
                    'dest_dept_id': dest_department['id'],
                    'dest_dept_name': dest_department['name']
                }
            }
        except Exception as e:
            return {
                'success': False,
                'response': f"Error processing transfer request: {str(e)}"
            }

    def _get_pharmacy_context(self) -> Dict[str, Any]:
        """Get comprehensive pharmacy context for AI prompts"""
        try:
            # Get all data
            medicines = get_medicines()
            patients = get_patients()
            suppliers = get_suppliers()
            departments = get_departments()
            stores = get_stores()
            purchases = get_purchases()
            consumption_records = get_consumption()
            transfers = get_transfers()

            # Calculate metrics
            total_counts = {
                'medicines': len(medicines),
                'patients': len(patients),
                'suppliers': len(suppliers),
                'departments': len(departments),
                'stores': len(stores),
                'purchases': len(purchases),
                'consumption_records': len(consumption_records),
                'transfers': len(transfers)
            }

            # Calculate inventory metrics
            total_medicines_in_stock = 0
            out_of_stock_count = 0
            low_stock_medicines = []

            for medicine in medicines:
                stock = get_medicine_stock(medicine['id'])
                if stock > 0:
                    total_medicines_in_stock += 1
                else:
                    out_of_stock_count += 1

                if stock <= medicine.get('low_stock_limit', 0):
                    low_stock_medicines.append({
                        'name': medicine['name'],
                        'stock': stock,
                        'limit': medicine.get('low_stock_limit', 0)
                    })

            return {
                'total_counts': total_counts,
                'total_medicines_in_stock': total_medicines_in_stock,
                'out_of_stock_count': out_of_stock_count,
                'low_stock_medicines': low_stock_medicines
            }
        except Exception as e:
            return {
                'total_counts': {},
                'total_medicines_in_stock': 0,
                'out_of_stock_count': 0,
                'low_stock_medicines': []
            }

    def _handle_comprehensive_overview(self) -> Dict[str, Any]:
        """Handle comprehensive database overview request"""
        try:
            # Get pharmacy context
            pharmacy_context = self._get_pharmacy_context()

            # Get comprehensive data
            data = chatbot_db.get_comprehensive_data()

            # Use AI prompt for structured response
            prompt = get_comprehensive_data_prompt()

            # Generate comprehensive response using the AI prompt structure
            response = f"# 🏥 **ALORF HOSPITAL - COMPREHENSIVE DATABASE OVERVIEW**\n\n"

            # Executive Summary
            response += f"## 📊 **EXECUTIVE SUMMARY**\n"
            response += f"• **Total Medicines:** {pharmacy_context['total_counts']['medicines']} records\n"
            response += f"• **Total Patients:** {pharmacy_context['total_counts']['patients']} records\n"
            response += f"• **Total Suppliers:** {pharmacy_context['total_counts']['suppliers']} records\n"
            response += f"• **Total Departments:** {pharmacy_context['total_counts']['departments']} records\n"
            response += f"• **Total Stores:** {pharmacy_context['total_counts']['stores']} locations\n"
            response += f"• **Purchase Records:** {pharmacy_context['total_counts']['purchases']} transactions\n"
            response += f"• **Consumption Records:** {pharmacy_context['total_counts']['consumption_records']} entries\n"
            response += f"• **Transfer Records:** {pharmacy_context['total_counts']['transfers']} transfers\n\n"

            # Inventory Status
            response += f"## 📦 **INVENTORY STATUS**\n"
            response += f"• **Medicines in Stock:** {pharmacy_context['total_medicines_in_stock']} items\n"
            response += f"• **Out of Stock:** {pharmacy_context['out_of_stock_count']} items\n"
            response += f"• **Low Stock Alerts:** {len(pharmacy_context['low_stock_medicines'])} items\n\n"

            if pharmacy_context['low_stock_medicines']:
                response += f"**🚨 LOW STOCK ALERTS:**\n"
                for item in pharmacy_context['low_stock_medicines'][:5]:
                    response += f"• {item['name']}: {item['stock']} units (limit: {item['limit']})\n"
                response += "\n"

            # Table-by-table analysis
            medicines = get_medicines()
            if medicines:
                response += f"## 💊 **MEDICINES TABLE** ({len(medicines)} records)\n"
                # Group by supplier
                supplier_counts = {}
                suppliers = get_suppliers()
                for medicine in medicines:
                    supplier_id = medicine.get('supplier_id', 'Unknown')
                    supplier_name = next((s['name'] for s in suppliers if s['id'] == supplier_id), f'Supplier {supplier_id}')
                    supplier_counts[supplier_name] = supplier_counts.get(supplier_name, 0) + 1

                response += "**Medicines by Supplier:**\n"
                for supplier, count in sorted(supplier_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                    response += f"• {supplier}: {count} medicines\n"
                response += "\n"

            # Continue with other tables...
            patients = get_patients()
            if patients:
                response += f"## 👥 **PATIENTS TABLE** ({len(patients)} records)\n"
                # Group by department
                dept_patients = {}
                departments = get_departments()
                for patient in patients:
                    dept_id = patient.get('department_id', 'Unknown')
                    # Get department name from department_id
                    dept_name = 'Unknown'
                    if dept_id != 'Unknown':
                        dept = next((d for d in departments if d['id'] == dept_id), None)
                        dept_name = dept.get('name', f'Department {dept_id}') if dept else f'Department {dept_id}'
                    dept_patients[dept_name] = dept_patients.get(dept_name, 0) + 1

                response += "**Patients by Department:**\n"
                for dept, count in dept_patients.items():
                    response += f"• {dept}: {count} patients\n"
                response += "\n"

            # Add recommendations
            response += f"## 🎯 **KEY RECOMMENDATIONS**\n"
            if pharmacy_context['out_of_stock_count'] > 0:
                response += f"• **URGENT:** Restock {pharmacy_context['out_of_stock_count']} out-of-stock medicines\n"
            if len(pharmacy_context['low_stock_medicines']) > 0:
                response += f"• **PRIORITY:** Review {len(pharmacy_context['low_stock_medicines'])} low-stock items\n"
            response += f"• **OPTIMIZATION:** Consider supplier performance analysis\n"
            response += f"• **EFFICIENCY:** Review department inventory distribution\n"

            return {
                'success': True,
                'response': response,
                'data': data
            }
        except Exception as e:
            return {
                'success': False,
                'response': f"Error generating comprehensive overview: {str(e)}"
            }

    def _handle_medicines_analysis(self) -> Dict[str, Any]:
        """Handle comprehensive medicines table analysis"""
        try:
            medicines = get_medicines()
            suppliers = get_suppliers()

            # Use specific table prompt
            table_prompts = get_specific_table_prompts()
            medicines_prompt = table_prompts.get('medicines', '')

            response = f"# 💊 **COMPREHENSIVE MEDICINES ANALYSIS**\n\n"
            response += f"## 📊 **OVERVIEW**\n"
            response += f"• **Total Medicines:** {len(medicines)} records\n"
            response += f"• **Active Suppliers:** {len(suppliers)} suppliers\n\n"

            # Stock analysis
            in_stock = 0
            out_of_stock = 0
            low_stock = 0

            response += f"## 📦 **STOCK ANALYSIS**\n"
            for medicine in medicines:
                stock = get_medicine_stock(medicine['id'])
                if stock > 0:
                    in_stock += 1
                else:
                    out_of_stock += 1

                if stock <= medicine.get('low_stock_limit', 0):
                    low_stock += 1

            response += f"• **In Stock:** {in_stock} medicines\n"
            response += f"• **Out of Stock:** {out_of_stock} medicines\n"
            response += f"• **Low Stock:** {low_stock} medicines\n\n"

            # Supplier breakdown
            response += f"## 🏢 **SUPPLIER BREAKDOWN**\n"
            supplier_counts = {}
            for medicine in medicines:
                supplier_id = medicine.get('supplier_id', 'Unknown')
                supplier_name = next((s['name'] for s in suppliers if s['id'] == supplier_id), f'Supplier {supplier_id}')
                supplier_counts[supplier_name] = supplier_counts.get(supplier_name, 0) + 1

            for supplier, count in sorted(supplier_counts.items(), key=lambda x: x[1], reverse=True):
                response += f"• **{supplier}:** {count} medicines\n"

            response += f"\n## 🎯 **RECOMMENDATIONS**\n"
            if out_of_stock > 0:
                response += f"• **URGENT:** Restock {out_of_stock} out-of-stock medicines\n"
            if low_stock > 0:
                response += f"• **PRIORITY:** Review {low_stock} low-stock medicines\n"
            response += f"• **OPTIMIZATION:** Consider supplier diversification\n"

            return {
                'success': True,
                'response': response,
                'data': {'medicines': medicines, 'suppliers': suppliers}
            }
        except Exception as e:
            return {
                'success': False,
                'response': f"Error generating medicines analysis: {str(e)}"
            }

    def _handle_medicine_names_list(self) -> Dict[str, Any]:
        """Handle request for complete list of medicine names"""
        try:
            medicines = get_medicines()

            if not medicines:
                return {
                    'success': True,
                    'response': "No medicines found in the database."
                }

            response = f"# 💊 **ALL MEDICINES IN DATABASE**\n\n"
            response += f"**Total Medicines:** {len(medicines)}\n\n"
            response += f"## 📋 **Complete Medicine List:**\n"

            # Sort medicines alphabetically by name
            sorted_medicines = sorted(medicines, key=lambda x: x.get('name', '').lower())

            for i, medicine in enumerate(sorted_medicines, 1):
                medicine_name = medicine.get('name', 'Unknown')
                form_dosage = medicine.get('form_dosage', 'N/A')
                response += f"{i}. **{medicine_name}** ({form_dosage})\n"

            return {
                'success': True,
                'response': response,
                'data': {'medicines': medicines, 'total_count': len(medicines)}
            }
        except Exception as e:
            return {
                'success': False,
                'response': f"Error retrieving medicine names: {str(e)}"
            }

    def _handle_patients_analysis(self) -> Dict[str, Any]:
        """Handle comprehensive patients table analysis"""
        try:
            patients = get_patients()
            departments = get_departments()

            response = f"# 👥 **COMPREHENSIVE PATIENTS ANALYSIS**\n\n"
            response += f"## 📊 **OVERVIEW**\n"
            response += f"• **Total Patients:** {len(patients)} records\n"
            response += f"• **Active Departments:** {len(departments)} departments\n\n"

            # Department distribution
            response += f"## 🏥 **DEPARTMENT DISTRIBUTION**\n"
            dept_patients = {}
            for patient in patients:
                dept_id = patient.get('department_id', 'Unknown')
                dept_name = 'Unknown'
                if dept_id != 'Unknown':
                    dept = next((d for d in departments if d['id'] == dept_id), None)
                    dept_name = dept.get('name', f'Department {dept_id}') if dept else f'Department {dept_id}'
                dept_patients[dept_name] = dept_patients.get(dept_name, 0) + 1

            for dept, count in sorted(dept_patients.items(), key=lambda x: x[1], reverse=True):
                response += f"• **{dept}:** {count} patients\n"

            # Demographics analysis
            response += f"\n## 👤 **DEMOGRAPHICS**\n"
            gender_counts = {'Male': 0, 'Female': 0, 'Not specified': 0}
            age_groups = {'0-18': 0, '19-35': 0, '36-60': 0, '60+': 0, 'Unknown': 0}

            for patient in patients:
                gender = patient.get('gender', 'Not specified')
                if gender.lower() in ['male', 'm']:
                    gender_counts['Male'] += 1
                elif gender.lower() in ['female', 'f']:
                    gender_counts['Female'] += 1
                else:
                    gender_counts['Not specified'] += 1

                age = patient.get('age', 0)
                try:
                    age = int(age) if age else 0
                except (ValueError, TypeError):
                    age = 0

                if age == 0:
                    age_groups['Unknown'] += 1
                elif age <= 18:
                    age_groups['0-18'] += 1
                elif age <= 35:
                    age_groups['19-35'] += 1
                elif age <= 60:
                    age_groups['36-60'] += 1
                else:
                    age_groups['60+'] += 1

            response += f"**Gender Distribution:**\n"
            for gender, count in gender_counts.items():
                response += f"• {gender}: {count} patients\n"

            response += f"\n**Age Groups:**\n"
            for age_group, count in age_groups.items():
                response += f"• {age_group}: {count} patients\n"

            response += f"\n## 🎯 **RECOMMENDATIONS**\n"
            response += f"• **DATA QUALITY:** Ensure complete demographic information\n"
            response += f"• **DEPARTMENT BALANCE:** Review patient distribution across departments\n"
            response += f"• **CARE OPTIMIZATION:** Analyze consumption patterns by demographics\n"

            return {
                'success': True,
                'response': response,
                'data': {'patients': patients, 'departments': departments}
            }
        except Exception as e:
            return {
                'success': False,
                'response': f"Error generating patients analysis: {str(e)}"
            }

    def _handle_suppliers_analysis(self) -> Dict[str, Any]:
        """Handle comprehensive suppliers table analysis"""
        try:
            suppliers = get_suppliers()
            medicines = get_medicines()

            response = f"# 🏢 **COMPREHENSIVE SUPPLIERS ANALYSIS**\n\n"
            response += f"## 📊 **OVERVIEW**\n"
            response += f"• **Total Suppliers:** {len(suppliers)} records\n"
            response += f"• **Total Medicines:** {len(medicines)} supplied\n\n"

            # Supplier performance
            response += f"## 📈 **SUPPLIER PERFORMANCE**\n"
            supplier_medicine_counts = {}
            for medicine in medicines:
                supplier_id = medicine.get('supplier_id', 'Unknown')
                supplier_name = next((s['name'] for s in suppliers if s['id'] == supplier_id), f'Supplier {supplier_id}')
                supplier_medicine_counts[supplier_name] = supplier_medicine_counts.get(supplier_name, 0) + 1

            for supplier, count in sorted(supplier_medicine_counts.items(), key=lambda x: x[1], reverse=True):
                response += f"• **{supplier}:** {count} medicines supplied\n"

            # Contact information summary
            response += f"\n## 📞 **CONTACT SUMMARY**\n"
            contact_complete = 0
            for supplier in suppliers:
                if supplier.get('contact') and supplier.get('email'):
                    contact_complete += 1

            response += f"• **Complete Contact Info:** {contact_complete}/{len(suppliers)} suppliers\n"
            response += f"• **Missing Contacts:** {len(suppliers) - contact_complete} suppliers\n"

            response += f"\n## 🎯 **RECOMMENDATIONS**\n"
            response += f"• **DIVERSIFICATION:** Consider adding more suppliers for critical medicines\n"
            response += f"• **CONTACT UPDATE:** Ensure all supplier contact information is complete\n"
            response += f"• **PERFORMANCE TRACKING:** Implement supplier performance metrics\n"

            return {
                'success': True,
                'response': response,
                'data': {'suppliers': suppliers, 'medicines': medicines}
            }
        except Exception as e:
            return {
                'success': False,
                'response': f"Error generating suppliers analysis: {str(e)}"
            }

    def _handle_departments_analysis(self) -> Dict[str, Any]:
        """Handle comprehensive departments table analysis"""
        try:
            departments = get_departments()
            patients = get_patients()

            response = f"# 🏥 **COMPREHENSIVE DEPARTMENTS ANALYSIS**\n\n"
            response += f"## 📊 **OVERVIEW**\n"
            response += f"• **Total Departments:** {len(departments)} departments\n"
            response += f"• **Total Patients:** {len(patients)} across all departments\n\n"

            # Department patient distribution
            response += f"## 👥 **PATIENT DISTRIBUTION**\n"
            dept_patients = {}
            for patient in patients:
                dept_id = patient.get('department_id', 'Unknown')
                dept_name = 'Unassigned'
                if dept_id != 'Unknown':
                    dept = next((d for d in departments if d['id'] == dept_id), None)
                    dept_name = dept.get('name', f'Department {dept_id}') if dept else f'Department {dept_id}'
                dept_patients[dept_name] = dept_patients.get(dept_name, 0) + 1

            for dept, count in sorted(dept_patients.items(), key=lambda x: x[1], reverse=True):
                response += f"• **{dept}:** {count} patients\n"

            # Department details
            response += f"\n## 🏢 **DEPARTMENT DETAILS**\n"
            for dept in departments:
                response += f"• **{dept.get('name', 'Unknown')}**\n"
                response += f"  - Responsible Person: {dept.get('responsible_person', 'Not assigned')}\n"
                response += f"  - Contact: {dept.get('contact', 'Not provided')}\n"
                response += f"  - Patients: {dept_patients.get(dept.get('name', 'Unknown'), 0)}\n"

            response += f"\n## 🎯 **RECOMMENDATIONS**\n"
            response += f"• **WORKLOAD BALANCE:** Review patient distribution across departments\n"
            response += f"• **CONTACT UPDATE:** Ensure all department contacts are current\n"
            response += f"• **RESOURCE ALLOCATION:** Align resources with patient loads\n"

            return {
                'success': True,
                'response': response,
                'data': {'departments': departments, 'patients': patients}
            }
        except Exception as e:
            return {
                'success': False,
                'response': f"Error generating departments analysis: {str(e)}"
            }

    def _handle_stores_analysis(self) -> Dict[str, Any]:
        """Handle comprehensive stores table analysis"""
        try:
            stores = get_stores()
            departments = get_departments()

            response = f"# 🏪 **COMPREHENSIVE STORES ANALYSIS**\n\n"
            response += f"## 📊 **OVERVIEW**\n"
            response += f"• **Total Storage Locations:** {len(stores)} stores\n"
            response += f"• **Total Departments:** {len(departments)} departments\n\n"

            # Store details
            response += f"## 📦 **STORAGE LOCATIONS**\n"
            for store in stores:
                dept_name = 'Unknown Department'
                if store.get('department_id'):
                    dept = next((d for d in departments if d['id'] == store['department_id']), None)
                    dept_name = dept.get('name', f"Department {store['department_id']}") if dept else f"Department {store['department_id']}"

                response += f"• **{store.get('name', 'Unnamed Store')}**\n"
                response += f"  - Department: {dept_name}\n"
                response += f"  - Location: {store.get('location', 'Not specified')}\n"
                response += f"  - Capacity: {store.get('capacity', 'Not specified')}\n"

            response += f"\n## 🎯 **RECOMMENDATIONS**\n"
            response += f"• **CAPACITY OPTIMIZATION:** Review storage capacity utilization\n"
            response += f"• **LOCATION MAPPING:** Ensure all store locations are properly documented\n"
            response += f"• **DEPARTMENT ALIGNMENT:** Verify store-department assignments\n"

            return {
                'success': True,
                'response': response,
                'data': {'stores': stores, 'departments': departments}
            }
        except Exception as e:
            return {
                'success': False,
                'response': f"Error generating stores analysis: {str(e)}"
            }

    def _handle_purchases_analysis(self) -> Dict[str, Any]:
        """Handle comprehensive purchases table analysis"""
        try:
            purchases = get_purchases()
            suppliers = get_suppliers()

            response = f"# 💰 **COMPREHENSIVE PURCHASES ANALYSIS**\n\n"
            response += f"## 📊 **OVERVIEW**\n"
            response += f"• **Total Purchase Records:** {len(purchases)} transactions\n"
            response += f"• **Active Suppliers:** {len(suppliers)} suppliers\n\n"

            if purchases:
                # Cost analysis
                total_cost = sum(float(p.get('total_cost', 0)) for p in purchases)
                avg_cost = total_cost / len(purchases) if purchases else 0

                response += f"## 💵 **FINANCIAL SUMMARY**\n"
                response += f"• **Total Purchase Value:** ${total_cost:,.2f}\n"
                response += f"• **Average Purchase Value:** ${avg_cost:,.2f}\n"
                response += f"• **Number of Transactions:** {len(purchases)}\n\n"

                # Supplier spending
                response += f"## 🏢 **SUPPLIER SPENDING**\n"
                supplier_spending = {}
                for purchase in purchases:
                    supplier_id = purchase.get('supplier_id', 'Unknown')
                    supplier_name = next((s['name'] for s in suppliers if s['id'] == supplier_id), f'Supplier {supplier_id}')
                    cost = float(purchase.get('total_cost', 0))
                    supplier_spending[supplier_name] = supplier_spending.get(supplier_name, 0) + cost

                for supplier, cost in sorted(supplier_spending.items(), key=lambda x: x[1], reverse=True):
                    response += f"• **{supplier}:** ${cost:,.2f}\n"
            else:
                response += f"## ⚠️ **NO PURCHASE DATA**\n"
                response += f"• No purchase records found in the system\n"

            response += f"\n## 🎯 **RECOMMENDATIONS**\n"
            response += f"• **COST TRACKING:** Monitor purchase trends and seasonal variations\n"
            response += f"• **SUPPLIER NEGOTIATION:** Review high-spending supplier contracts\n"
            response += f"• **BUDGET PLANNING:** Use historical data for future budget allocation\n"

            return {
                'success': True,
                'response': response,
                'data': {'purchases': purchases, 'suppliers': suppliers}
            }
        except Exception as e:
            return {
                'success': False,
                'response': f"Error generating purchases analysis: {str(e)}"
            }

    def _handle_consumption_analysis(self) -> Dict[str, Any]:
        """Handle comprehensive consumption table analysis"""
        try:
            consumption_records = get_consumption()
            patients = get_patients()
            medicines = get_medicines()

            response = f"# 📊 **COMPREHENSIVE CONSUMPTION ANALYSIS**\n\n"
            response += f"## 📊 **OVERVIEW**\n"
            response += f"• **Total Consumption Records:** {len(consumption_records)} entries\n"
            response += f"• **Active Patients:** {len(patients)} patients\n"
            response += f"• **Available Medicines:** {len(medicines)} medicines\n\n"

            if consumption_records:
                # Patient consumption patterns
                response += f"## 👥 **PATIENT CONSUMPTION PATTERNS**\n"
                patient_consumption = {}
                for record in consumption_records:
                    patient_id = record.get('patient_id', 'Unknown')
                    patient_name = next((p['name'] for p in patients if p['id'] == patient_id), f'Patient {patient_id}')
                    quantity = int(record.get('quantity', 0))
                    patient_consumption[patient_name] = patient_consumption.get(patient_name, 0) + quantity

                top_consumers = sorted(patient_consumption.items(), key=lambda x: x[1], reverse=True)[:5]
                for patient, quantity in top_consumers:
                    response += f"• **{patient}:** {quantity} units consumed\n"

                # Medicine consumption
                response += f"\n## 💊 **MEDICINE CONSUMPTION**\n"
                medicine_consumption = {}
                for record in consumption_records:
                    medicine_id = record.get('medicine_id', 'Unknown')
                    medicine_name = next((m['name'] for m in medicines if m['id'] == medicine_id), f'Medicine {medicine_id}')
                    quantity = int(record.get('quantity', 0))
                    medicine_consumption[medicine_name] = medicine_consumption.get(medicine_name, 0) + quantity

                top_medicines = sorted(medicine_consumption.items(), key=lambda x: x[1], reverse=True)[:5]
                for medicine, quantity in top_medicines:
                    response += f"• **{medicine}:** {quantity} units consumed\n"
            else:
                response += f"## ⚠️ **NO CONSUMPTION DATA**\n"
                response += f"• No consumption records found in the system\n"

            response += f"\n## 🎯 **RECOMMENDATIONS**\n"
            response += f"• **USAGE TRACKING:** Monitor consumption patterns for inventory planning\n"
            response += f"• **PATIENT CARE:** Review high-consumption patients for care optimization\n"
            response += f"• **STOCK PLANNING:** Use consumption data for reorder point calculations\n"

            return {
                'success': True,
                'response': response,
                'data': {'consumption_records': consumption_records, 'patients': patients, 'medicines': medicines}
            }
        except Exception as e:
            return {
                'success': False,
                'response': f"Error generating consumption analysis: {str(e)}"
            }

    def _handle_transfers_analysis(self) -> Dict[str, Any]:
        """Handle comprehensive transfers table analysis"""
        try:
            transfers = get_transfers()
            departments = get_departments()

            response = f"# 🔄 **COMPREHENSIVE TRANSFERS ANALYSIS**\n\n"
            response += f"## 📊 **OVERVIEW**\n"
            response += f"• **Total Transfer Records:** {len(transfers)} transfers\n"
            response += f"• **Active Departments:** {len(departments)} departments\n\n"

            if transfers:
                # Department transfer patterns
                response += f"## 🏥 **DEPARTMENT TRANSFER PATTERNS**\n"
                source_transfers = {}
                dest_transfers = {}

                for transfer in transfers:
                    source_id = transfer.get('source_department_id', 'Unknown')
                    dest_id = transfer.get('destination_department_id', 'Unknown')

                    source_name = next((d['name'] for d in departments if d['id'] == source_id), f'Department {source_id}')
                    dest_name = next((d['name'] for d in departments if d['id'] == dest_id), f'Department {dest_id}')

                    quantity = int(transfer.get('quantity', 0))
                    source_transfers[source_name] = source_transfers.get(source_name, 0) + quantity
                    dest_transfers[dest_name] = dest_transfers.get(dest_name, 0) + quantity

                response += f"**Top Source Departments:**\n"
                for dept, quantity in sorted(source_transfers.items(), key=lambda x: x[1], reverse=True)[:5]:
                    response += f"• **{dept}:** {quantity} units transferred out\n"

                response += f"\n**Top Destination Departments:**\n"
                for dept, quantity in sorted(dest_transfers.items(), key=lambda x: x[1], reverse=True)[:5]:
                    response += f"• **{dept}:** {quantity} units received\n"
            else:
                response += f"## ⚠️ **NO TRANSFER DATA**\n"
                response += f"• No transfer records found in the system\n"

            response += f"\n## 🎯 **RECOMMENDATIONS**\n"
            response += f"• **TRANSFER OPTIMIZATION:** Review frequent transfer routes for efficiency\n"
            response += f"• **INVENTORY BALANCE:** Ensure balanced distribution across departments\n"
            response += f"• **APPROVAL TRACKING:** Monitor transfer approval processes\n"

            return {
                'success': True,
                'response': response,
                'data': {'transfers': transfers, 'departments': departments}
            }
        except Exception as e:
            return {
                'success': False,
                'response': f"Error generating transfers analysis: {str(e)}"
            }

    def _handle_cross_table_inventory(self) -> Dict[str, Any]:
        """Handle cross-table inventory analysis with optimization recommendations"""
        try:
            medicines = get_medicines()
            stores = get_stores()
            departments = get_departments()
            transfers = get_transfers()

            response = f"# 📦 **CROSS-TABLE INVENTORY ANALYSIS**\n\n"
            response += f"## 📊 **INVENTORY OVERVIEW**\n"
            response += f"• **Total Medicines:** {len(medicines)} items\n"
            response += f"• **Storage Locations:** {len(stores)} stores\n"
            response += f"• **Departments:** {len(departments)} departments\n"
            response += f"• **Transfer Records:** {len(transfers)} transfers\n\n"

            # Stock distribution analysis
            response += f"## 📈 **STOCK DISTRIBUTION ANALYSIS**\n"
            total_stock = 0
            in_stock_count = 0
            out_of_stock_count = 0
            low_stock_count = 0

            for medicine in medicines:
                stock = get_medicine_stock(medicine['id'])
                total_stock += stock
                if stock > 0:
                    in_stock_count += 1
                else:
                    out_of_stock_count += 1

                if stock <= medicine.get('low_stock_limit', 0):
                    low_stock_count += 1

            response += f"• **Total Stock Units:** {total_stock:,} units\n"
            response += f"• **Items in Stock:** {in_stock_count}/{len(medicines)} ({(in_stock_count/len(medicines)*100):.1f}%)\n"
            response += f"• **Out of Stock:** {out_of_stock_count} items\n"
            response += f"• **Low Stock Alerts:** {low_stock_count} items\n\n"

            # Department inventory distribution
            response += f"## 🏥 **DEPARTMENT INVENTORY DISTRIBUTION**\n"
            if transfers:
                dept_inventory = {}
                for transfer in transfers:
                    dest_id = transfer.get('destination_department_id', 'Unknown')
                    dest_name = next((d['name'] for d in departments if d['id'] == dest_id), f'Department {dest_id}')
                    quantity = int(transfer.get('quantity', 0))
                    dept_inventory[dest_name] = dept_inventory.get(dest_name, 0) + quantity

                for dept, quantity in sorted(dept_inventory.items(), key=lambda x: x[1], reverse=True):
                    response += f"• **{dept}:** {quantity} units received\n"
            else:
                response += f"• No transfer data available for department distribution analysis\n"

            response += f"\n## 🎯 **OPTIMIZATION RECOMMENDATIONS**\n"
            if out_of_stock_count > 0:
                response += f"• **CRITICAL:** Immediate restocking needed for {out_of_stock_count} out-of-stock items\n"
            if low_stock_count > 0:
                response += f"• **HIGH PRIORITY:** Review {low_stock_count} low-stock items for reorder\n"

            response += f"• **EFFICIENCY:** Implement automated reorder points based on consumption patterns\n"
            response += f"• **DISTRIBUTION:** Balance inventory across departments based on usage patterns\n"
            response += f"• **STORAGE:** Optimize storage allocation across {len(stores)} locations\n"
            response += f"• **MONITORING:** Set up real-time inventory tracking dashboards\n"

            return {
                'success': True,
                'response': response,
                'data': {
                    'medicines': medicines,
                    'stores': stores,
                    'departments': departments,
                    'transfers': transfers,
                    'metrics': {
                        'total_stock': total_stock,
                        'in_stock_count': in_stock_count,
                        'out_of_stock_count': out_of_stock_count,
                        'low_stock_count': low_stock_count
                    }
                }
            }
        except Exception as e:
            return {
                'success': False,
                'response': f"Error generating cross-table inventory analysis: {str(e)}"
            }

    def _handle_cross_table_financial(self) -> Dict[str, Any]:
        """Handle cross-table financial analysis"""
        try:
            purchases = get_purchases()
            consumption_records = get_consumption()
            suppliers = get_suppliers()
            medicines = get_medicines()

            response = f"# 💰 **CROSS-TABLE FINANCIAL ANALYSIS**\n\n"
            response += f"## 📊 **FINANCIAL OVERVIEW**\n"
            response += f"• **Purchase Records:** {len(purchases)} transactions\n"
            response += f"• **Consumption Records:** {len(consumption_records)} entries\n"
            response += f"• **Active Suppliers:** {len(suppliers)} suppliers\n"
            response += f"• **Medicine Catalog:** {len(medicines)} items\n\n"

            # Purchase analysis
            if purchases:
                total_purchase_cost = sum(float(p.get('total_cost', 0)) for p in purchases)
                avg_purchase_cost = total_purchase_cost / len(purchases) if purchases else 0

                response += f"## 💵 **PURCHASE FINANCIAL SUMMARY**\n"
                response += f"• **Total Purchase Value:** ${total_purchase_cost:,.2f}\n"
                response += f"• **Average Purchase Value:** ${avg_purchase_cost:,.2f}\n"
                response += f"• **Purchase Transactions:** {len(purchases)}\n\n"

                # Supplier cost analysis
                response += f"## 🏢 **SUPPLIER COST ANALYSIS**\n"
                supplier_costs = {}
                for purchase in purchases:
                    supplier_id = purchase.get('supplier_id', 'Unknown')
                    supplier_name = next((s['name'] for s in suppliers if s['id'] == supplier_id), f'Supplier {supplier_id}')
                    cost = float(purchase.get('total_cost', 0))
                    supplier_costs[supplier_name] = supplier_costs.get(supplier_name, 0) + cost

                for supplier, cost in sorted(supplier_costs.items(), key=lambda x: x[1], reverse=True)[:5]:
                    percentage = (cost / total_purchase_cost * 100) if total_purchase_cost > 0 else 0
                    response += f"• **{supplier}:** ${cost:,.2f} ({percentage:.1f}%)\n"
            else:
                response += f"## ⚠️ **NO PURCHASE DATA**\n"
                response += f"• No purchase records available for financial analysis\n"

            # Consumption value analysis
            if consumption_records:
                response += f"\n## 📊 **CONSUMPTION VALUE ANALYSIS**\n"
                total_consumption_units = sum(int(c.get('quantity', 0)) for c in consumption_records)
                response += f"• **Total Units Consumed:** {total_consumption_units:,} units\n"

                # Estimate consumption value (simplified)
                if purchases and total_consumption_units > 0:
                    avg_unit_cost = total_purchase_cost / total_consumption_units if total_consumption_units > 0 else 0
                    estimated_consumption_value = total_consumption_units * avg_unit_cost
                    response += f"• **Estimated Consumption Value:** ${estimated_consumption_value:,.2f}\n"

            response += f"\n## 🎯 **FINANCIAL OPTIMIZATION RECOMMENDATIONS**\n"
            response += f"• **COST CONTROL:** Monitor supplier pricing trends and negotiate better rates\n"
            response += f"• **BUDGET PLANNING:** Use historical data for accurate budget forecasting\n"
            response += f"• **WASTE REDUCTION:** Analyze consumption vs. purchase patterns to minimize waste\n"
            response += f"• **SUPPLIER DIVERSIFICATION:** Reduce dependency on high-cost suppliers\n"
            response += f"• **ROI TRACKING:** Implement cost-per-patient metrics for better resource allocation\n"

            return {
                'success': True,
                'response': response,
                'data': {
                    'purchases': purchases,
                    'consumption_records': consumption_records,
                    'suppliers': suppliers,
                    'medicines': medicines
                }
            }
        except Exception as e:
            return {
                'success': False,
                'response': f"Error generating cross-table financial analysis: {str(e)}"
            }

    def _handle_cross_table_performance(self) -> Dict[str, Any]:
        """Handle cross-table performance analysis"""
        try:
            suppliers = get_suppliers()
            departments = get_departments()
            medicines = get_medicines()
            patients = get_patients()
            purchases = get_purchases()
            consumption_records = get_consumption()

            response = f"# 📈 **CROSS-TABLE PERFORMANCE ANALYSIS**\n\n"
            response += f"## 📊 **PERFORMANCE OVERVIEW**\n"
            response += f"• **Suppliers:** {len(suppliers)} active\n"
            response += f"• **Departments:** {len(departments)} operational\n"
            response += f"• **Medicine Categories:** {len(medicines)} items\n"
            response += f"• **Patient Base:** {len(patients)} patients\n\n"

            # Supplier performance
            response += f"## 🏢 **SUPPLIER PERFORMANCE METRICS**\n"
            supplier_performance = {}
            for medicine in medicines:
                supplier_id = medicine.get('supplier_id', 'Unknown')
                supplier_name = next((s['name'] for s in suppliers if s['id'] == supplier_id), f'Supplier {supplier_id}')
                supplier_performance[supplier_name] = supplier_performance.get(supplier_name, 0) + 1

            # Calculate supplier purchase volume
            supplier_purchase_volume = {}
            if purchases:
                for purchase in purchases:
                    supplier_id = purchase.get('supplier_id', 'Unknown')
                    supplier_name = next((s['name'] for s in suppliers if s['id'] == supplier_id), f'Supplier {supplier_id}')
                    cost = float(purchase.get('total_cost', 0))
                    supplier_purchase_volume[supplier_name] = supplier_purchase_volume.get(supplier_name, 0) + cost

            response += f"**Top Performing Suppliers:**\n"
            for supplier, medicine_count in sorted(supplier_performance.items(), key=lambda x: x[1], reverse=True)[:5]:
                purchase_volume = supplier_purchase_volume.get(supplier, 0)
                response += f"• **{supplier}:** {medicine_count} medicines, ${purchase_volume:,.2f} volume\n"

            # Department performance
            response += f"\n## 🏥 **DEPARTMENT PERFORMANCE METRICS**\n"
            dept_patient_counts = {}
            for patient in patients:
                dept_id = patient.get('department_id', 'Unknown')
                dept_name = 'Unassigned'
                if dept_id != 'Unknown':
                    dept = next((d for d in departments if d['id'] == dept_id), None)
                    dept_name = dept.get('name', f'Department {dept_id}') if dept else f'Department {dept_id}'
                dept_patient_counts[dept_name] = dept_patient_counts.get(dept_name, 0) + 1

            # Calculate department consumption
            dept_consumption = {}
            if consumption_records:
                for record in consumption_records:
                    patient_id = record.get('patient_id', 'Unknown')
                    patient = next((p for p in patients if p['id'] == patient_id), None)
                    if patient:
                        dept_id = patient.get('department_id', 'Unknown')
                        dept_name = 'Unassigned'
                        if dept_id != 'Unknown':
                            dept = next((d for d in departments if d['id'] == dept_id), None)
                            dept_name = dept.get('name', f'Department {dept_id}') if dept else f'Department {dept_id}'
                        quantity = int(record.get('quantity', 0))
                        dept_consumption[dept_name] = dept_consumption.get(dept_name, 0) + quantity

            response += f"**Department Efficiency Metrics:**\n"
            for dept, patient_count in sorted(dept_patient_counts.items(), key=lambda x: x[1], reverse=True):
                consumption = dept_consumption.get(dept, 0)
                efficiency = consumption / patient_count if patient_count > 0 else 0
                response += f"• **{dept}:** {patient_count} patients, {consumption} units consumed, {efficiency:.1f} units/patient\n"

            # Medicine category performance
            response += f"\n## 💊 **MEDICINE CATEGORY PERFORMANCE**\n"
            medicine_consumption = {}
            if consumption_records:
                for record in consumption_records:
                    medicine_id = record.get('medicine_id', 'Unknown')
                    medicine_name = next((m['name'] for m in medicines if m['id'] == medicine_id), f'Medicine {medicine_id}')
                    quantity = int(record.get('quantity', 0))
                    medicine_consumption[medicine_name] = medicine_consumption.get(medicine_name, 0) + quantity

            response += f"**Top Consumed Medicines:**\n"
            for medicine, quantity in sorted(medicine_consumption.items(), key=lambda x: x[1], reverse=True)[:5]:
                response += f"• **{medicine}:** {quantity} units consumed\n"

            response += f"\n## 🎯 **PERFORMANCE OPTIMIZATION RECOMMENDATIONS**\n"
            response += f"• **SUPPLIER OPTIMIZATION:** Focus on top-performing suppliers for strategic partnerships\n"
            response += f"• **DEPARTMENT EFFICIENCY:** Review departments with high consumption-per-patient ratios\n"
            response += f"• **MEDICINE MANAGEMENT:** Ensure adequate stock for high-consumption medicines\n"
            response += f"• **RESOURCE ALLOCATION:** Align resources with department patient loads and consumption patterns\n"
            response += f"• **PERFORMANCE TRACKING:** Implement KPIs for suppliers, departments, and medicine categories\n"
            response += f"• **COST-EFFECTIVENESS:** Analyze cost-per-patient metrics across departments\n"

            return {
                'success': True,
                'response': response,
                'data': {
                    'suppliers': suppliers,
                    'departments': departments,
                    'medicines': medicines,
                    'patients': patients,
                    'performance_metrics': {
                        'supplier_performance': supplier_performance,
                        'dept_patient_counts': dept_patient_counts,
                        'medicine_consumption': medicine_consumption
                    }
                }
            }
        except Exception as e:
            return {
                'success': False,
                'response': f"Error generating cross-table performance analysis: {str(e)}"
            }

    def _handle_general_query(self, user_input: str) -> Dict[str, Any]:
        """Handle general queries that don't match specific patterns"""
        try:
            # Get comprehensive data for context
            data = chatbot_db.get_comprehensive_data()

            # Simple keyword-based responses for specific inventory queries only
            user_input_lower = user_input.lower()

            # Only provide inventory status for specific stock/inventory queries
            if any(phrase in user_input_lower for phrase in ['current stock', 'inventory status', 'stock levels']):
                inventory_summary = data.get('inventory_summary', {})
                highest_stock = inventory_summary.get('highest_stock_medicines', [])

                if highest_stock:
                    response = f"**Current Inventory Status:**\n"
                    response += f"• Total medicines in stock: {inventory_summary.get('total_medicines_in_stock', 0)}\n"
                    response += f"• Out of stock medicines: {inventory_summary.get('out_of_stock_medicines', 0)}\n"
                    response += f"• Highest stock: {highest_stock[0].get('name', 'Unknown')} ({highest_stock[0].get('stock', 0)} units)\n"
                    return {'success': True, 'response': response}

            # Default response with available capabilities
            response = """I'm your AI pharmacy assistant! I can help you with:

**📊 Analytics & Reports:**
• "What is the highest stock medicine?"
• "Give me names of all the medicines in the database"
• "Which patient has consumed the most medicines this month?"
• "Show me the top 5 most expensive purchases this year"
• "Which department has the lowest average stock levels?"
• "Show me medicines expiring within 30 days"

**🔧 Administrative Operations:**
• "Add a new medicine called [name] with supplier [supplier] and dosage [dosage]"
• "Add a new patient called [name] with department [department] and medical history [history]"
• "Add a new supplier called [name] with contact [contact] and phone [phone]"
• "Add a new department called [name] with responsible person [person] and phone [phone]"
• "Update patient [ID] to change their medical history to [new history]"
• "Delete medicine with ID [ID]"
• "Transfer [quantity] units of [medicine] from [source] to [destination]"

**🔍 Search & Query:**
• Ask about any aspect of your pharmacy data
• Get real-time inventory status
• Analyze consumption patterns

What would you like to know or do?"""

            return {
                'success': True,
                'response': response,
                'data': data.get('analytics', {})
            }
        except Exception as e:
            return {
                'success': False,
                'response': f"Error processing query: {str(e)}"
            }

    def get_all_database_tables(self) -> Dict[str, Any]:
        """Get comprehensive data from all database tables"""
        try:
            # Get all data using the comprehensive database manager
            all_data = chatbot_db.get_comprehensive_data()
            
            # Format for detailed analysis
            formatted_response = {
                'success': True,
                'response': self._format_comprehensive_database_overview(all_data),
                'raw_data': all_data,
                'table_summaries': self._generate_table_summaries(all_data)
            }
            
            return formatted_response
            
        except Exception as e:
            return {
                'success': False,
                'response': f"Error retrieving comprehensive database: {str(e)}"
            }

    def _format_comprehensive_database_overview(self, data: Dict) -> str:
        """Format comprehensive database overview"""
        try:
            response = "🏥 **ALORF HOSPITAL PHARMACY - COMPLETE DATABASE OVERVIEW**\n\n"
            
            # Analytics summary
            analytics = data.get('analytics', {})
            total_counts = analytics.get('total_counts', {})
            
            response += "## 📊 **DATABASE SUMMARY**\n"
            for table, count in total_counts.items():
                response += f"• **{table.title()}**: {count} records\n"
            
            # Medicines analysis
            medicines = data.get('medicines', [])
            response += f"\n## 💊 **MEDICINES TABLE** ({len(medicines)} records)\n"
            if medicines:
                categories = analytics.get('medicine_categories', {})
                response += "**Categories:**\n"
                for cat, count in categories.items():
                    response += f"• {cat}: {count} medicines\n"
                
                # Top stock medicines
                inventory_summary = data.get('inventory_summary', {})
                highest_stock = inventory_summary.get('highest_stock_medicines', [])[:5]
                if highest_stock:
                    response += "\n**Top 5 Highest Stock:**\n"
                    for med in highest_stock:
                        response += f"• {med.get('name', 'Unknown')}: {med.get('stock', 0)} units\n"
            
            # Patients analysis
            patients = data.get('patients', [])
            response += f"\n## 👥 **PATIENTS TABLE** ({len(patients)} records)\n"
            if patients:
                # Group by department
                dept_patients = {}
                departments = data.get('departments', [])
                for patient in patients:
                    dept_id = patient.get('department_id', 'Unknown')
                    # Get department name from department_id
                    dept_name = 'Unknown'
                    if dept_id != 'Unknown':
                        dept = next((d for d in departments if d['id'] == dept_id), None)
                        dept_name = dept.get('name', f'Department {dept_id}') if dept else f'Department {dept_id}'
                    dept_patients[dept_name] = dept_patients.get(dept_name, 0) + 1

                response += "**Patients by Department:**\n"
                for dept, count in dept_patients.items():
                    response += f"• {dept}: {count} patients\n"
            
            # Suppliers analysis
            suppliers = data.get('suppliers', [])
            response += f"\n## 🏢 **SUPPLIERS TABLE** ({len(suppliers)} records)\n"
            if suppliers:
                response += "**Recent Suppliers:**\n"
                for supplier in suppliers[:5]:
                    response += f"• {supplier.get('name', 'Unknown')} - {supplier.get('contact_person', 'N/A')}\n"
            
            # Departments analysis
            departments = data.get('departments', [])
            response += f"\n## 🏬 **DEPARTMENTS TABLE** ({len(departments)} records)\n"
            if departments:
                for dept in departments:
                    response += f"• **{dept.get('name', 'Unknown')}** - {dept.get('responsible_person', 'N/A')}\n"
            
            # Stores analysis
            stores = data.get('stores', [])
            response += f"\n## 🏪 **STORES TABLE** ({len(stores)} records)\n"
            if stores:
                for store in stores:
                    inventory_count = len(store.get('inventory', {}))
                    response += f"• **{store.get('name', 'Unknown')}** - {inventory_count} different medicines\n"
            
            # Purchases analysis
            purchases = data.get('purchases', [])
            response += f"\n## 💰 **PURCHASES TABLE** ({len(purchases)} records)\n"
            if purchases:
                total_cost = sum(float(p.get('total_cost', 0)) for p in purchases)
                response += f"• **Total Purchase Value**: ${total_cost:,.2f}\n"
                response += f"• **Recent Purchase Cost (30 days)**: ${analytics.get('recent_purchase_cost', 0):,.2f}\n"
            
            # Consumption analysis
            consumption = data.get('consumption', [])
            response += f"\n## 📊 **CONSUMPTION TABLE** ({len(consumption)} records)\n"
            if consumption:
                response += f"• **Recent Consumption Records (30 days)**: {analytics.get('recent_consumption_count', 0)}\n"
                
                # Top consuming patients
                top_patients = analytics.get('top_consuming_patients', [])[:3]
                if top_patients:
                    response += "**Top Consuming Patients:**\n"
                    for patient in top_patients:
                        response += f"• {patient.get('patient_name', 'Unknown')}: {patient.get('consumption_count', 0)} medicines\n"
            
            # Transfers analysis
            transfers = data.get('transfers', [])
            response += f"\n## 🔄 **TRANSFERS TABLE** ({len(transfers)} records)\n"
            if transfers:
                recent_transfers = [t for t in transfers if self._is_recent(t.get('date', ''))]
                response += f"• **Recent Transfers (30 days)**: {len(recent_transfers)}\n"
            
            # Critical alerts
            low_stock = data.get('low_stock_alerts', [])
            if low_stock:
                response += f"\n## 🚨 **CRITICAL ALERTS**\n"
                response += f"• **Low Stock Medicines**: {len(low_stock)}\n"
                for item in low_stock[:3]:
                    response += f"  - {item.get('name', 'Unknown')}: {item.get('current_stock', 0)} units (limit: {item.get('low_stock_limit', 0)})\n"
            
            return response
            
        except Exception as e:
            return f"Error formatting database overview: {str(e)}"

# Global instance for easy access
pharmacy_agent = PharmacyAIAgent()

