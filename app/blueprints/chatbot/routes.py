"""
Chatbot Blueprint Routes - Main Chat Interface

Chat interface routes for the AI chatbot.
Configuration routes are in config_routes.py.
"""

from flask import Blueprint, render_template, request, jsonify, session
from app.utils.decorators import admin_required
from app.utils.database import (
    get_medicines, log_activity
)
from app.utils.chatbot_database import chatbot_db
from app.agent import pharmacy_agent
from app.utils.chat_history import chat_history_manager
from .config import load_chatbot_config
from app.llm import create_llm_provider
from app.utils.ai_prompts import get_system_prompt
import re

chatbot_bp = Blueprint('chatbot', __name__)


@chatbot_bp.route('/')
@admin_required
def index():
    """AI Chatbot interface"""
    config = load_chatbot_config()
    user_id = session.get('user_id', 'admin')

    # Get or create current session
    current_session_id = session.get('current_chat_session')
    if not current_session_id:
        current_session_id = chat_history_manager.create_new_session(user_id)
        session['current_chat_session'] = current_session_id

    # Get user's chat sessions
    user_sessions = chat_history_manager.get_user_sessions(user_id)

    # Get current session messages
    current_messages = chat_history_manager.get_session_messages(current_session_id)

    return render_template('chatbot/index.html',
                         config=config,
                         user_sessions=user_sessions,
                         current_session_id=current_session_id,
                         current_messages=current_messages)


@chatbot_bp.route('/sessions/new', methods=['POST'])
@admin_required
def new_session():
    """Create a new chat session"""
    try:
        user_id = session.get('user_id', 'admin')
        title = request.json.get('title', None)

        session_id = chat_history_manager.create_new_session(user_id, title)
        session['current_chat_session'] = session_id

        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'New chat session created'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error creating session: {str(e)}'})


@chatbot_bp.route('/sessions/<session_id>/switch', methods=['POST'])
@admin_required
def switch_session(session_id):
    """Switch to a different chat session"""
    try:
        user_id = session.get('user_id', 'admin')

        # Verify session belongs to user
        user_sessions = chat_history_manager.get_user_sessions(user_id)
        if not any(s['id'] == session_id for s in user_sessions):
            return jsonify({'success': False, 'message': 'Session not found'})

        session['current_chat_session'] = session_id
        messages = chat_history_manager.get_session_messages(session_id)

        return jsonify({
            'success': True,
            'session_id': session_id,
            'messages': messages,
            'message': 'Session switched successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error switching session: {str(e)}'})


@chatbot_bp.route('/sessions/<session_id>/delete', methods=['DELETE'])
@admin_required
def delete_session(session_id):
    """Delete a chat session"""
    try:
        user_id = session.get('user_id', 'admin')

        success = chat_history_manager.delete_session(session_id, user_id)
        if success:
            # If deleting current session, create a new one
            if session.get('current_chat_session') == session_id:
                new_session_id = chat_history_manager.create_new_session(user_id)
                session['current_chat_session'] = new_session_id

            return jsonify({'success': True, 'message': 'Session deleted successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to delete session'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error deleting session: {str(e)}'})


@chatbot_bp.route('/sessions/<session_id>/rename', methods=['POST'])
@admin_required
def rename_session(session_id):
    """Rename a chat session"""
    try:
        user_id = session.get('user_id', 'admin')
        new_title = request.json.get('title', '').strip()

        if not new_title:
            return jsonify({'success': False, 'message': 'Title cannot be empty'})

        success = chat_history_manager.update_session_title(session_id, user_id, new_title)
        if success:
            return jsonify({'success': True, 'message': 'Session renamed successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to rename session'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error renaming session: {str(e)}'})


@chatbot_bp.route('/query', methods=['POST'])
@admin_required
def query():
    """Handle chatbot queries with enhanced AI agent and LLM integration"""
    try:
        user_query = request.json.get('query', '')
        user_id = session.get('user_id', 'admin')

        # Get current session
        current_session_id = session.get('current_chat_session')
        if not current_session_id:
            current_session_id = chat_history_manager.create_new_session(user_id)
            session['current_chat_session'] = current_session_id

        # Save user message to chat history
        chat_history_manager.add_message(current_session_id, user_id, user_query, 'user')

        # Log the query
        log_activity('QUERY', 'chatbot', user_id, {'query': user_query})

        # Load configuration to check preferences
        config = load_chatbot_config()
        force_llm = config.get('force_llm', False)

        # First, try to handle with AI agent for administrative operations (unless forced to use LLM)
        if not force_llm:
            agent_result = pharmacy_agent.process_command(user_query, user_id)

            # If agent handled it successfully, return the result
            if agent_result.get('success'):
                # Save AI response to chat history
                chat_history_manager.add_message(
                    current_session_id, user_id, agent_result['response'], 'ai',
                    {'agent_handled': True, 'data': agent_result.get('data', {})}
                )

                return jsonify({
                    'response': agent_result['response'],
                    'status': 'success',
                    'agent_handled': True,
                    'requires_confirmation': agent_result.get('requires_confirmation', False),
                    'confirmation_data': agent_result.get('confirmation_data', {}),
                    'data': agent_result.get('data', {})
                })

        # Check if LLM is enabled and configured
        if not config.get('enabled', False):
            return enhanced_fallback_response(user_query, current_session_id, user_id)

        # Get enhanced pharmacy context
        pharmacy_context = chatbot_db.get_comprehensive_data()

        # Calculate context metrics
        analytics = pharmacy_context.get('analytics', {})
        inventory_summary = pharmacy_context.get('inventory_summary', {})

        context = {
            'total_counts': analytics.get('total_counts', {}),
            'total_medicines_in_stock': inventory_summary.get('total_medicines_in_stock', 0),
            'out_of_stock_count': inventory_summary.get('out_of_stock_medicines', 0),
            'low_stock_medicines': pharmacy_context.get('low_stock_alerts', [])[:3],
            'highest_stock_medicines': inventory_summary.get('highest_stock_medicines', [])[:3],
            'recent_consumption_count': analytics.get('recent_consumption_count', 0),
            'recent_purchase_cost': analytics.get('recent_purchase_cost', 0),
            'medicine_categories': analytics.get('medicine_categories', {})
        }

        # Create enhanced system prompt with comprehensive data
        system_prompt = get_system_prompt(context)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]

        # Call LLM API using new llm package
        provider = create_llm_provider(config)
        response = provider.call(messages, max_tokens=config.get('max_tokens', 1000), temperature=config.get('temperature', 0.7))

        # Save AI response to chat history
        chat_history_manager.add_message(
            current_session_id, user_id, response, 'ai',
            {'llm_handled': True, 'provider': config.get('provider', 'openai')}
        )

        return jsonify({
            'response': response,
            'status': 'success',
            'llm_handled': True,
            'context_data': pharmacy_context
        })

    except Exception as e:
        print(f"Enhanced query error: {e}")
        # Fallback to enhanced responses
        return enhanced_fallback_response(user_query, current_session_id, user_id)


@chatbot_bp.route('/confirm', methods=['POST'])
@admin_required
def confirm_action():
    """Handle confirmation for administrative actions"""
    try:
        user_input = request.json.get('confirmation', '')
        user_id = session.get('user_id', 'admin')

        # Check for deletion confirmation
        delete_match = re.search(r'CONFIRM DELETE MEDICINE (\w+)', user_input, re.IGNORECASE)
        if delete_match:
            medicine_id = delete_match.group(1)

            # Verify medicine exists
            from app.utils.database import get_medicines, delete_medicine
            medicines = get_medicines()
            medicine = next((m for m in medicines if m['id'] == medicine_id), None)

            if not medicine:
                return jsonify({
                    'response': f"Medicine with ID '{medicine_id}' not found.",
                    'status': 'error'
                })

            # Perform deletion
            delete_medicine(medicine_id)

            # Log the action
            log_activity('DELETE', 'medicine', user_id, {
                'medicine_id': medicine_id,
                'medicine_name': medicine.get('name', 'Unknown'),
                'via': 'AI_assistant_confirmed'
            })

            response = f"✅ **Medicine Deleted Successfully!**\n\n"
            response += f"• **Medicine:** {medicine.get('name', 'Unknown')}\n"
            response += f"• **ID:** {medicine_id}\n\n"
            response += "The medicine and all its inventory records have been removed from the system."

            return jsonify({
                'response': response,
                'status': 'success',
                'action_completed': 'delete_medicine'
            })

        # Check for transfer confirmation
        transfer_match = re.search(r'CONFIRM TRANSFER (\w+) (\d+) (\w+) (\w+)', user_input, re.IGNORECASE)
        if transfer_match:
            from app.utils.database import update_store_inventory
            medicine_id, quantity, source_dept_id, dest_dept_id = transfer_match.groups()
            quantity = int(quantity)

            try:
                # Perform the transfer
                # Subtract from source
                update_store_inventory(source_dept_id, [{'medicine_id': medicine_id, 'quantity': quantity}], 'subtract')
                # Add to destination
                update_store_inventory(dest_dept_id, [{'medicine_id': medicine_id, 'quantity': quantity}], 'add')

                # Log the action
                log_activity('TRANSFER', 'inventory', user_id, {
                    'medicine_id': medicine_id,
                    'quantity': quantity,
                    'source_dept_id': source_dept_id,
                    'dest_dept_id': dest_dept_id,
                    'via': 'AI_assistant_confirmed'
                })

                response = f"✅ **Transfer Completed Successfully!**\n\n"
                response += f"• **Medicine ID:** {medicine_id}\n"
                response += f"• **Quantity:** {quantity} units\n"
                response += f"• **From:** Department {source_dept_id}\n"
                response += f"• **To:** Department {dest_dept_id}\n\n"
                response += "The inventory has been updated in both departments."

                return jsonify({
                    'response': response,
                    'status': 'success',
                    'action_completed': 'transfer_inventory'
                })
            except Exception as e:
                return jsonify({
                    'response': f"Transfer failed: {str(e)}",
                    'status': 'error'
                })

        # If no confirmation pattern matched
        return jsonify({
            'response': "Confirmation not recognized. Please use the exact confirmation format provided.",
            'status': 'error'
        })

    except Exception as e:
        return jsonify({
            'response': f"Error processing confirmation: {str(e)}",
            'status': 'error'
        })


def enhanced_fallback_response(user_query, session_id, user_id):
    """Enhanced fallback response system with comprehensive data access"""
    try:
        # Use the AI agent for fallback as well
        agent_result = pharmacy_agent.process_command(user_query)

        if agent_result.get('success'):
            # Save AI response to chat history
            chat_history_manager.add_message(
                session_id, user_id, agent_result['response'], 'ai',
                {'fallback_handled': True, 'data': agent_result.get('data', {})}
            )

            return jsonify({
                'response': agent_result['response'],
                'status': 'success',
                'fallback_handled': True
            })

        # If agent couldn't handle it, provide enhanced fallback
        user_query_lower = user_query.lower()

        # Get comprehensive data for better responses
        comprehensive_data = chatbot_db.get_comprehensive_data()

        if 'highest stock' in user_query_lower:
            inventory_summary = comprehensive_data.get('inventory_summary', {})
            highest_stock = inventory_summary.get('highest_stock_medicines', [])

            if highest_stock:
                top_medicine = highest_stock[0]
                response = f"**Highest Stock Medicine:**\n"
                response += f"• {top_medicine.get('name', 'Unknown')}: {top_medicine.get('stock', 0)} units\n"
                response += f"• Category: {top_medicine.get('category', 'Unknown')}"
            else:
                response = "No stock data available."

        elif any(word in user_query_lower for word in ['low stock', 'running low']):
            low_stock = comprehensive_data.get('low_stock_alerts', [])

            if low_stock:
                response = f"**Low Stock Medicines ({len(low_stock)} total):**\n\n"
                for item in low_stock[:5]:
                    response += f"• {item.get('name', 'Unknown')}: {item.get('current_stock', 0)} units (limit: {item.get('low_stock_limit', 0)})\n"
                if len(low_stock) > 5:
                    response += f"\n...and {len(low_stock) - 5} more medicines."
            else:
                response = "Great news! All medicines are currently well-stocked above their low stock limits."

        elif 'analytics' in user_query_lower or 'summary' in user_query_lower:
            analytics = comprehensive_data.get('analytics', {})
            total_counts = analytics.get('total_counts', {})

            response = f"**Pharmacy Analytics Summary:**\n\n"
            response += f"📊 **Total Counts:**\n"
            for entity, count in total_counts.items():
                response += f"• {entity.title()}: {count}\n"

            response += f"\n💰 **Financial:**\n"
            response += f"• Recent Purchase Cost (30 days): ${analytics.get('recent_purchase_cost', 0):,.2f}\n"

            response += f"\n📈 **Activity:**\n"
            response += f"• Recent Consumption Records: {analytics.get('recent_consumption_count', 0)}\n"

        else:
            # Default enhanced response
            response = """🤖 **Enhanced AI Pharmacy Assistant**

I can help you with comprehensive pharmacy management:

**📊 Advanced Analytics:**
• "What is the highest stock medicine and its current level?"
• "Which patient has consumed the most medicines this month?"
• "Show me the top 5 most expensive purchases this year"
• "Which department has the lowest average stock levels?"
• "Show me medicines expiring within 30 days"

**🔧 Administrative Operations:**
• "Add a new medicine called [name] with category [category]"
• "Update patient [ID] medical history to [new history]"
• "Delete medicine with ID [ID]" (with confirmation)
• "Transfer [quantity] units of [medicine] from [source] to [destination]"

**🔍 Real-time Data Access:**
• Complete access to all pharmacy data
• Cross-module operations and analytics
• Intelligent search and filtering

Try asking me anything about your pharmacy operations!"""

        # Save AI response to chat history
        chat_history_manager.add_message(
            session_id, user_id, response, 'ai',
            {'enhanced_fallback': True}
        )

        return jsonify({'response': response, 'status': 'success', 'enhanced_fallback': True})

    except Exception as e:
        error_response = f'Sorry, I encountered an error: {str(e)}'
        # Save error response to chat history
        chat_history_manager.add_message(
            session_id, user_id, error_response, 'ai',
            {'error': True, 'enhanced_fallback': True}
        )
        return jsonify({'response': error_response, 'status': 'error'}), 500
