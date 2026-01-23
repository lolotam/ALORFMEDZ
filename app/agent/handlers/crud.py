"""
CRUD Operation Handlers
Handles Create, Read, Update, Delete operations and transfers
"""

import re
from datetime import datetime
from typing import Dict, Any
from .base import BaseHandler
from app.utils.database import (
    save_medicine, update_medicine, delete_medicine,
    save_patient, update_patient,
    save_supplier,
    save_department, get_medicine_stock,
    get_medicines, get_patients, get_suppliers, get_departments,
    log_activity
)


class CRUDHandler(BaseHandler):
    """Handler for CRUD operations and transfers"""

    SUPPORTED_QUERIES = [
        'add_medicine', 'add_patient', 'add_supplier', 'add_department',
        'update_patient',
        'delete_medicine',
        'transfer_inventory'
    ]

    def can_handle(self, query_type: str) -> bool:
        """Check if this handler can process the query"""
        return query_type in self.SUPPORTED_QUERIES

    def handle(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the query"""
        query_type = query_data.get('type')
        user_input = query_data.get('input', '')
        user_id = query_data.get('user_id', 'anonymous')

        handler_map = {
            'add_medicine': lambda: self._handle_add_medicine(user_input, user_id),
            'add_patient': lambda: self._handle_add_patient(user_input, user_id),
            'add_supplier': lambda: self._handle_add_supplier(user_input, user_id),
            'add_department': lambda: self._handle_add_department(user_input, user_id),
            'update_patient': lambda: self._handle_update_patient(user_input, user_id),
            'delete_medicine': lambda: self._handle_delete_medicine(user_input, user_id),
            'transfer_inventory': lambda: self._handle_transfer_inventory(user_input, user_id)
        }

        handler = handler_map.get(query_type)
        if handler:
            return handler()

        return self.format_error_response(f"Unknown CRUD query type: {query_type}")

    def get_supported_query_types(self) -> list[str]:
        """Get supported query types"""
        return self.SUPPORTED_QUERIES

    def _handle_add_medicine(self, user_input: str, user_id: str) -> Dict[str, Any]:
        """Handle adding new medicine"""
        try:
            name_match = re.search(r'called\s+([^,\s]+(?:\s+[^,\s]+)*)', user_input, re.IGNORECASE)

            if not name_match:
                return self.format_error_response(
                    "I couldn't extract the medicine name. "
                    "Please use format: 'Add a new medicine called [name] with supplier [supplier] and dosage [dosage]'"
                )

            medicine_name = name_match.group(1).strip()

            supplier_match = re.search(r'supplier\s+([^,\s]+(?:\s+[^,\s]+)*)', user_input, re.IGNORECASE)
            dosage_match = re.search(r'dosage\s+([^,\s]+(?:\s+[^,\s]+)*)', user_input, re.IGNORECASE)
            form_match = re.search(r'form\s+([^,\s]+)', user_input, re.IGNORECASE)
            notes_match = re.search(r'notes?\s+([^,]+)', user_input, re.IGNORECASE)

            suppliers = get_suppliers()
            default_supplier_id = suppliers[0]['id'] if suppliers else '01'

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
                'low_stock_limit': 10,
                'notes': notes_match.group(1).strip() if notes_match else f'Medicine added via AI assistant on {datetime.now().strftime("%Y-%m-%d")}'
            }

            medicine_id = save_medicine(medicine_data)

            log_activity('CREATE', 'medicine', user_id, {
                'medicine_id': medicine_id,
                'medicine_name': medicine_name,
                'via': 'AI_assistant'
            })

            supplier_name = next((s['name'] for s in suppliers if s['id'] == supplier_id), 'Unknown')

            response = f"✅ **Medicine Added Successfully!**\n\n"
            response += f"• **Name:** {medicine_name}\n"
            response += f"• **ID:** {medicine_id}\n"
            response += f"• **Supplier:** {supplier_name}\n"
            response += f"• **Form/Dosage:** {medicine_data['form_dosage']}\n"
            response += f"• **Low Stock Limit:** {medicine_data['low_stock_limit']}\n"
            response += f"• **Notes:** {medicine_data['notes']}\n\n"
            response += "The medicine has been added to the system and is ready for inventory management."

            return self.format_success_response(response, {'medicine_id': medicine_id, 'medicine_data': medicine_data})

        except Exception as e:
            return self.format_error_response(f"Error adding medicine: {str(e)}")

    def _handle_add_patient(self, user_input: str, user_id: str) -> Dict[str, Any]:
        """Handle adding new patient"""
        try:
            name_match = re.search(r'called\s+([^,\s]+(?:\s+[^,\s]+)*)', user_input, re.IGNORECASE)

            if not name_match:
                return self.format_error_response(
                    "I couldn't extract the patient name. "
                    "Please use format: 'Add a new patient called [name] with department [department] and medical history [history]'"
                )

            patient_name = name_match.group(1).strip()

            department_match = re.search(r'department\s+([^,\s]+(?:\s+[^,\s]+)*)', user_input, re.IGNORECASE)
            history_match = re.search(r'medical\s+history\s+([^,]+)', user_input, re.IGNORECASE)
            gender_match = re.search(r'gender\s+([^,\s]+)', user_input, re.IGNORECASE)
            age_match = re.search(r'age\s+(\d+)', user_input, re.IGNORECASE)

            departments = get_departments()
            default_department_id = departments[0]['id'] if departments else '01'

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

            log_activity('CREATE', 'patient', patient_id, {
                'name': patient_data['name'],
                'department_id': patient_data['department_id']
            })

            department_name = next((d['name'] for d in departments if d['id'] == department_id), 'Unknown')

            response = f"✅ **Patient Added Successfully!**\n\n"
            response += f"• **Name:** {patient_name}\n"
            response += f"• **ID:** {patient_id}\n"
            response += f"• **Department:** {department_name}\n"
            response += f"• **Gender:** {patient_data['gender']}\n"
            response += f"• **Age:** {patient_data['age']}\n"
            response += f"• **Medical History:** {patient_data['medical_history']}\n\n"
            response += "The patient has been added to the system and is ready for medical management."

            return self.format_success_response(response, {'patient_id': patient_id, 'patient_data': patient_data})

        except Exception as e:
            return self.format_error_response(f"Error adding patient: {str(e)}")

    def _handle_add_supplier(self, user_input: str, user_id: str) -> Dict[str, Any]:
        """Handle adding new supplier"""
        try:
            name_match = re.search(r'called\s+([^,\s]+(?:\s+[^,\s]+)*)', user_input, re.IGNORECASE)

            if not name_match:
                return self.format_error_response(
                    "I couldn't extract the supplier name. "
                    "Please use format: 'Add a new supplier called [name] with contact [contact] and phone [phone]'"
                )

            supplier_name = name_match.group(1).strip()

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

            return self.format_success_response(response, {'supplier_id': supplier_id, 'supplier_data': supplier_data})

        except Exception as e:
            return self.format_error_response(f"Error adding supplier: {str(e)}")

    def _handle_add_department(self, user_input: str, user_id: str) -> Dict[str, Any]:
        """Handle adding new department"""
        try:
            name_match = re.search(r'called\s+([^,\s]+(?:\s+[^,\s]+)*)', user_input, re.IGNORECASE)

            if not name_match:
                return self.format_error_response(
                    "I couldn't extract the department name. "
                    "Please use format: 'Add a new department called [name] with responsible person [person] and phone [phone]'"
                )

            department_name = name_match.group(1).strip()

            person_match = re.search(r'responsible\s+person\s+([^,\s]+(?:\s+[^,\s]+)*)', user_input, re.IGNORECASE)
            phone_match = re.search(r'phone\s+([^,\s]+)', user_input, re.IGNORECASE)

            department_data = {
                'name': department_name,
                'responsible_person': person_match.group(1).strip() if person_match else 'Not specified',
                'telephone': phone_match.group(1) if phone_match else '',
                'notes': f'Department added via AI assistant on {datetime.now().strftime("%Y-%m-%d")}'
            }

            department_id = save_department(department_data)

            from app.utils.database import create_store_for_department
            create_store_for_department(department_id, department_data['name'])

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

            return self.format_success_response(response, {'department_id': department_id, 'department_data': department_data})

        except Exception as e:
            return self.format_error_response(f"Error adding department: {str(e)}")

    def _handle_update_patient(self, user_input: str, user_id: str) -> Dict[str, Any]:
        """Handle updating patient information"""
        try:
            patient_match = re.search(r'patient\s+(\w+)', user_input, re.IGNORECASE)
            history_match = re.search(r'medical\s+history\s+to\s+(.+)', user_input, re.IGNORECASE)

            if not patient_match:
                return self.format_error_response(
                    "I couldn't extract the patient ID. "
                    "Please use format: 'Update patient [ID] to change their medical history to [new history]'"
                )

            patient_id = patient_match.group(1)

            patients = get_patients()
            patient = next((p for p in patients if p['id'] == patient_id), None)

            if not patient:
                return self.format_error_response(f"Patient with ID '{patient_id}' not found in the system.")

            if not history_match:
                return self.format_error_response("I couldn't extract the new medical history. Please specify what to update.")

            new_history = history_match.group(1).strip()

            update_data = {'medical_history': new_history}
            update_patient(patient_id, update_data)

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

            return self.format_success_response(response, {'patient_id': patient_id, 'updated_data': update_data})

        except Exception as e:
            return self.format_error_response(f"Error updating patient: {str(e)}")

    def _handle_delete_medicine(self, user_input: str, user_id: str) -> Dict[str, Any]:
        """Handle deleting medicine (requires confirmation)"""
        try:
            id_match = re.search(r'id\s+(\w+)', user_input, re.IGNORECASE)

            if not id_match:
                return self.format_error_response(
                    "I couldn't extract the medicine ID. "
                    "Please use format: 'Delete medicine with ID [ID]'"
                )

            medicine_id = id_match.group(1)

            medicines = get_medicines()
            medicine = next((m for m in medicines if m['id'] == medicine_id), None)

            if not medicine:
                return self.format_error_response(f"Medicine with ID '{medicine_id}' not found in the system.")

            current_stock = get_medicine_stock(medicine_id)

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
            return self.format_error_response(f"Error processing delete request: {str(e)}")

    def _handle_transfer_inventory(self, user_input: str, user_id: str) -> Dict[str, Any]:
        """Handle inventory transfer between departments"""
        try:
            quantity_match = re.search(r'transfer\s+(\d+)', user_input, re.IGNORECASE)
            medicine_match = re.search(r'of\s+([^,\s]+(?:\s+[^,\s]+)*)\s+from', user_input, re.IGNORECASE)
            source_match = re.search(r'from\s+([^,\s]+(?:\s+[^,\s]+)*)\s+to', user_input, re.IGNORECASE)
            dest_match = re.search(r'to\s+([^,\s]+(?:\s+[^,\s]+)*)', user_input, re.IGNORECASE)

            if not all([quantity_match, medicine_match, source_match, dest_match]):
                return self.format_error_response(
                    "I couldn't extract all transfer details. "
                    "Please use format: 'Transfer [quantity] units of [medicine] from [source department] to [destination department]'"
                )

            quantity = int(quantity_match.group(1))
            medicine_name = medicine_match.group(1).strip()
            source_dept = source_match.group(1).strip()
            dest_dept = dest_match.group(1).strip()

            medicines = get_medicines()
            medicine = next((m for m in medicines if m['name'].lower() == medicine_name.lower()), None)

            if not medicine:
                return self.format_error_response(f"Medicine '{medicine_name}' not found in the system.")

            departments = get_departments()
            source_department = next((d for d in departments if d['name'].lower() == source_dept.lower()), None)
            dest_department = next((d for d in departments if d['name'].lower() == dest_dept.lower()), None)

            if not source_department:
                return self.format_error_response(f"Source department '{source_dept}' not found.")

            if not dest_department:
                return self.format_error_response(f"Destination department '{dest_dept}' not found.")

            source_stock = get_medicine_stock(medicine['id'], source_department['id'])

            if source_stock < quantity:
                return self.format_error_response(
                    f"Insufficient stock in {source_dept}. "
                    f"Available: {source_stock} units, Requested: {quantity} units."
                )

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
            return self.format_error_response(f"Error processing transfer request: {str(e)}")
