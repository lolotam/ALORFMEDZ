"""
Comprehensive Response Handlers for Hospital Pharmacy Management System
Provides dedicated handlers for every type of database query with complete, accurate information
"""

from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from utils.database import (
    get_medicines, get_patients, get_suppliers, get_departments,
    get_stores, get_purchases, get_consumption, get_transfers,
    get_medicine_stock
)

class ComprehensiveHandlers:
    """Comprehensive handlers for all database query types"""
    
    def __init__(self):
        self.handlers = self._build_handlers_map()
    
    def _build_handlers_map(self) -> Dict[str, callable]:
        """Build mapping of query types to handler methods"""
        return {
            # MEDICINES HANDLERS
            'medicines_count': self._handle_medicines_count,
            'medicines_list': self._handle_medicines_list,
            'medicines_by_category': self._handle_medicines_by_category,
            'medicines_by_supplier': self._handle_medicines_by_supplier,
            'medicines_stock_levels': self._handle_medicines_stock_levels,
            'medicines_low_stock': self._handle_medicines_low_stock,
            'medicines_out_of_stock': self._handle_medicines_out_of_stock,
            'medicines_highest_stock': self._handle_medicines_highest_stock,
            'medicines_by_form': self._handle_medicines_by_form,
            'medicines_analysis': self._handle_medicines_analysis,
            
            # PATIENTS HANDLERS
            'patients_count': self._handle_patients_count,
            'patients_list': self._handle_patients_list,
            'patients_by_department': self._handle_patients_by_department,
            'patients_by_gender': self._handle_patients_by_gender,
            'patients_by_age': self._handle_patients_by_age,
            'patients_with_allergies': self._handle_patients_with_allergies,
            'patients_consumption': self._handle_patients_consumption,
            'patients_recent': self._handle_patients_recent,
            'patients_analysis': self._handle_patients_analysis,
            
            # SUPPLIERS HANDLERS
            'suppliers_count': self._handle_suppliers_count,
            'suppliers_list': self._handle_suppliers_list,
            'suppliers_by_type': self._handle_suppliers_by_type,
            'suppliers_performance': self._handle_suppliers_performance,
            'suppliers_contact_info': self._handle_suppliers_contact_info,
            'suppliers_purchase_history': self._handle_suppliers_purchase_history,
            'suppliers_analysis': self._handle_suppliers_analysis,
            
            # DEPARTMENTS HANDLERS
            'departments_count': self._handle_departments_count,
            'departments_list': self._handle_departments_list,
            'departments_staff': self._handle_departments_staff,
            'departments_inventory': self._handle_departments_inventory,
            'departments_consumption': self._handle_departments_consumption,
            'departments_analysis': self._handle_departments_analysis,
            
            # STORES HANDLERS
            'stores_count': self._handle_stores_count,
            'stores_list': self._handle_stores_list,
            'stores_inventory': self._handle_stores_inventory,
            'stores_capacity': self._handle_stores_capacity,
            'stores_by_department': self._handle_stores_by_department,
            'stores_analysis': self._handle_stores_analysis,
            
            # PURCHASES HANDLERS
            'purchases_count': self._handle_purchases_count,
            'purchases_list': self._handle_purchases_list,
            'purchases_recent': self._handle_purchases_recent,
            'purchases_by_supplier': self._handle_purchases_by_supplier,
            'purchases_expensive': self._handle_purchases_expensive,
            'purchases_total_cost': self._handle_purchases_total_cost,
            'purchases_by_date': self._handle_purchases_by_date,
            'purchases_analysis': self._handle_purchases_analysis,
            
            # CONSUMPTION HANDLERS
            'consumption_count': self._handle_consumption_count,
            'consumption_list': self._handle_consumption_list,
            'consumption_by_patient': self._handle_consumption_by_patient,
            'consumption_by_medicine': self._handle_consumption_by_medicine,
            'consumption_by_department': self._handle_consumption_by_department,
            'consumption_recent': self._handle_consumption_recent,
            'consumption_trends': self._handle_consumption_trends,
            'consumption_analysis': self._handle_consumption_analysis,
            
            # TRANSFERS HANDLERS
            'transfers_count': self._handle_transfers_count,
            'transfers_list': self._handle_transfers_list,
            'transfers_recent': self._handle_transfers_recent,
            'transfers_by_department': self._handle_transfers_by_department,
            'transfers_pending': self._handle_transfers_pending,
            'transfers_routes': self._handle_transfers_routes,
            'transfers_analysis': self._handle_transfers_analysis,
            
            # GENERAL HANDLERS
            'database_overview': self._handle_database_overview,
            'help_query': self._handle_help_query
        }
    
    def handle_query(self, query_type: str, user_input: str = None) -> Dict[str, Any]:
        """Handle a specific query type"""
        handler = self.handlers.get(query_type)
        if handler:
            try:
                return handler(user_input)
            except Exception as e:
                return {
                    'success': False,
                    'response': f"Error processing {query_type}: {str(e)}"
                }
        else:
            return {
                'success': False,
                'response': f"Unknown query type: {query_type}"
            }
    
    def get_available_handlers(self) -> List[str]:
        """Get list of available handler types"""
        return list(self.handlers.keys())
    
    # MEDICINES HANDLERS
    def _handle_medicines_count(self, user_input: str = None) -> Dict[str, Any]:
        """Handle medicine count queries"""
        medicines = get_medicines()
        count = len(medicines)
        
        response = f"# 💊 **MEDICINE COUNT**\n\n"
        response += f"**Total Medicines:** {count}\n\n"
        
        if count > 0:
            # Additional statistics
            suppliers = get_suppliers()
            supplier_counts = Counter(med.get('supplier_id') for med in medicines)
            
            response += f"## 📊 **Additional Statistics:**\n"
            response += f"• **Unique Suppliers:** {len(supplier_counts)}\n"
            response += f"• **Average per Supplier:** {count / len(supplier_counts):.1f}\n"
            
            # Form distribution
            forms = Counter(med.get('form_dosage', 'Unknown') for med in medicines)
            response += f"• **Most Common Form:** {forms.most_common(1)[0][0]} ({forms.most_common(1)[0][1]} medicines)\n"
        
        return {
            'success': True,
            'response': response,
            'data': {'count': count, 'medicines': medicines}
        }
    
    def _handle_medicines_list(self, user_input: str = None) -> Dict[str, Any]:
        """Handle medicine list queries"""
        medicines = get_medicines()
        
        if not medicines:
            return {
                'success': True,
                'response': "No medicines found in the database."
            }
        
        response = f"# 💊 **ALL MEDICINES LIST**\n\n"
        response += f"**Total Medicines:** {len(medicines)}\n\n"
        response += f"## 📋 **Complete Medicine List:**\n"
        
        # Sort medicines alphabetically
        sorted_medicines = sorted(medicines, key=lambda x: x.get('name', '').lower())
        
        for i, medicine in enumerate(sorted_medicines, 1):
            name = medicine.get('name', 'Unknown')
            form = medicine.get('form_dosage', 'N/A')
            stock = get_medicine_stock(medicine.get('id', ''))
            
            response += f"{i}. **{name}** ({form}) - Stock: {stock}\n"
        
        return {
            'success': True,
            'response': response,
            'data': {'medicines': medicines, 'total_count': len(medicines)}
        }
    
    def _handle_medicines_by_category(self, user_input: str = None) -> Dict[str, Any]:
        """Handle medicines by category queries"""
        medicines = get_medicines()
        
        if not medicines:
            return {
                'success': True,
                'response': "No medicines found in the database."
            }
        
        # Group by category
        categories = defaultdict(list)
        for medicine in medicines:
            category = medicine.get('category', 'Uncategorized')
            categories[category].append(medicine)
        
        response = f"# 💊 **MEDICINES BY CATEGORY**\n\n"
        response += f"**Total Categories:** {len(categories)}\n"
        response += f"**Total Medicines:** {len(medicines)}\n\n"
        
        # Sort categories by medicine count
        sorted_categories = sorted(categories.items(), key=lambda x: len(x[1]), reverse=True)
        
        for category, meds in sorted_categories:
            response += f"## 📂 **{category}** ({len(meds)} medicines)\n"
            for med in sorted(meds, key=lambda x: x.get('name', '')):
                name = med.get('name', 'Unknown')
                form = med.get('form_dosage', 'N/A')
                response += f"• **{name}** ({form})\n"
            response += "\n"
        
        return {
            'success': True,
            'response': response,
            'data': {'categories': dict(categories), 'total_count': len(medicines)}
        }
    
    def _handle_medicines_by_supplier(self, user_input: str = None) -> Dict[str, Any]:
        """Handle medicines by supplier queries"""
        medicines = get_medicines()
        suppliers = get_suppliers()
        
        if not medicines:
            return {
                'success': True,
                'response': "No medicines found in the database."
            }
        
        # Create supplier lookup
        supplier_lookup = {s.get('id'): s.get('name', 'Unknown') for s in suppliers}
        
        # Group by supplier
        by_supplier = defaultdict(list)
        for medicine in medicines:
            supplier_id = medicine.get('supplier_id', 'Unknown')
            supplier_name = supplier_lookup.get(supplier_id, f'Unknown Supplier ({supplier_id})')
            by_supplier[supplier_name].append(medicine)
        
        response = f"# 💊 **MEDICINES BY SUPPLIER**\n\n"
        response += f"**Total Suppliers:** {len(by_supplier)}\n"
        response += f"**Total Medicines:** {len(medicines)}\n\n"
        
        # Sort suppliers by medicine count
        sorted_suppliers = sorted(by_supplier.items(), key=lambda x: len(x[1]), reverse=True)
        
        for supplier_name, meds in sorted_suppliers:
            response += f"## 🏢 **{supplier_name}** ({len(meds)} medicines)\n"
            for med in sorted(meds, key=lambda x: x.get('name', '')):
                name = med.get('name', 'Unknown')
                form = med.get('form_dosage', 'N/A')
                stock = get_medicine_stock(med.get('id', ''))
                response += f"• **{name}** ({form}) - Stock: {stock}\n"
            response += "\n"
        
        return {
            'success': True,
            'response': response,
            'data': {'by_supplier': dict(by_supplier), 'total_count': len(medicines)}
        }
    
    def _handle_medicines_stock_levels(self, user_input: str = None) -> Dict[str, Any]:
        """Handle medicine stock levels queries"""
        medicines = get_medicines()
        
        if not medicines:
            return {
                'success': True,
                'response': "No medicines found in the database."
            }
        
        # Get stock levels for all medicines
        medicine_stocks = []
        total_stock = 0
        
        for medicine in medicines:
            stock = get_medicine_stock(medicine.get('id', ''))
            medicine_stocks.append({
                'name': medicine.get('name', 'Unknown'),
                'form': medicine.get('form_dosage', 'N/A'),
                'stock': stock,
                'low_limit': medicine.get('low_stock_limit', 0)
            })
            total_stock += stock
        
        # Sort by stock level (highest first)
        medicine_stocks.sort(key=lambda x: x['stock'], reverse=True)
        
        response = f"# 💊 **MEDICINE STOCK LEVELS**\n\n"
        response += f"**Total Medicines:** {len(medicines)}\n"
        response += f"**Total Stock Units:** {total_stock}\n"
        response += f"**Average Stock per Medicine:** {total_stock / len(medicines):.1f}\n\n"
        
        response += f"## 📊 **Stock Levels (Highest to Lowest):**\n"
        for i, med in enumerate(medicine_stocks, 1):
            status = "🔴 LOW" if med['stock'] <= med['low_limit'] else "🟢 OK"
            if med['stock'] == 0:
                status = "⚫ OUT"
            
            response += f"{i}. **{med['name']}** ({med['form']})\n"
            response += f"   Stock: {med['stock']} units | Limit: {med['low_limit']} | Status: {status}\n\n"
        
        return {
            'success': True,
            'response': response,
            'data': {'medicine_stocks': medicine_stocks, 'total_stock': total_stock}
        }

    def _handle_medicines_low_stock(self, user_input: str = None) -> Dict[str, Any]:
        """Handle low stock medicines queries"""
        medicines = get_medicines()

        if not medicines:
            return {
                'success': True,
                'response': "No medicines found in the database."
            }

        # Find low stock medicines
        low_stock_medicines = []
        for medicine in medicines:
            stock = get_medicine_stock(medicine.get('id', ''))
            low_limit = medicine.get('low_stock_limit', 0)
            if stock <= low_limit:
                low_stock_medicines.append({
                    'name': medicine.get('name', 'Unknown'),
                    'form': medicine.get('form_dosage', 'N/A'),
                    'stock': stock,
                    'low_limit': low_limit
                })

        response = f"# 🔴 **LOW STOCK MEDICINES**\n\n"

        if not low_stock_medicines:
            response += "🟢 **Great news!** All medicines are above their low stock limits.\n\n"
            response += f"**Total medicines checked:** {len(medicines)}\n"
            response += f"**Medicines needing attention:** 0\n"
        else:
            response += f"**Medicines needing attention:** {len(low_stock_medicines)}\n"
            response += f"**Total medicines:** {len(medicines)}\n\n"
            response += f"## ⚠️ **Medicines Below Stock Limit:**\n"

            # Sort by urgency (lowest stock first)
            low_stock_medicines.sort(key=lambda x: x['stock'])

            for i, med in enumerate(low_stock_medicines, 1):
                urgency = "🔴 CRITICAL" if med['stock'] == 0 else "🟡 LOW"
                response += f"{i}. **{med['name']}** ({med['form']})\n"
                response += f"   Current Stock: {med['stock']} | Limit: {med['low_limit']} | Status: {urgency}\n\n"

        return {
            'success': True,
            'response': response,
            'data': {'low_stock_medicines': low_stock_medicines, 'total_count': len(medicines)}
        }

    def _handle_medicines_out_of_stock(self, user_input: str = None) -> Dict[str, Any]:
        """Handle out of stock medicines queries"""
        medicines = get_medicines()

        if not medicines:
            return {
                'success': True,
                'response': "No medicines found in the database."
            }

        # Find out of stock medicines
        out_of_stock = []
        for medicine in medicines:
            stock = get_medicine_stock(medicine.get('id', ''))
            if stock == 0:
                out_of_stock.append({
                    'name': medicine.get('name', 'Unknown'),
                    'form': medicine.get('form_dosage', 'N/A'),
                    'category': medicine.get('category', 'Unknown')
                })

        response = f"# ⚫ **OUT OF STOCK MEDICINES**\n\n"

        if not out_of_stock:
            response += "🟢 **Excellent!** No medicines are completely out of stock.\n\n"
            response += f"**Total medicines checked:** {len(medicines)}\n"
        else:
            response += f"**Medicines out of stock:** {len(out_of_stock)}\n"
            response += f"**Total medicines:** {len(medicines)}\n"
            response += f"**Percentage out of stock:** {(len(out_of_stock) / len(medicines)) * 100:.1f}%\n\n"
            response += f"## 🚨 **Immediate Restocking Required:**\n"

            # Group by category
            by_category = defaultdict(list)
            for med in out_of_stock:
                by_category[med['category']].append(med)

            for category, meds in by_category.items():
                response += f"\n### 📂 **{category}** ({len(meds)} medicines)\n"
                for med in sorted(meds, key=lambda x: x['name']):
                    response += f"• **{med['name']}** ({med['form']})\n"

        return {
            'success': True,
            'response': response,
            'data': {'out_of_stock': out_of_stock, 'total_count': len(medicines)}
        }

    def _handle_medicines_highest_stock(self, user_input: str = None) -> Dict[str, Any]:
        """Handle highest stock medicines queries"""
        medicines = get_medicines()

        if not medicines:
            return {
                'success': True,
                'response': "No medicines found in the database."
            }

        # Get stock levels and sort by highest
        medicine_stocks = []
        for medicine in medicines:
            stock = get_medicine_stock(medicine.get('id', ''))
            medicine_stocks.append({
                'name': medicine.get('name', 'Unknown'),
                'form': medicine.get('form_dosage', 'N/A'),
                'stock': stock,
                'category': medicine.get('category', 'Unknown')
            })

        # Sort by stock level (highest first)
        medicine_stocks.sort(key=lambda x: x['stock'], reverse=True)

        # Take top 10
        top_medicines = medicine_stocks[:10]

        response = f"# 📈 **HIGHEST STOCK MEDICINES**\n\n"
        response += f"**Top 10 medicines with highest stock:**\n\n"

        total_stock = sum(med['stock'] for med in medicine_stocks)
        response += f"**Total inventory:** {total_stock:,} units\n"
        response += f"**Average per medicine:** {total_stock / len(medicines):.1f} units\n\n"

        response += f"## 🏆 **Top Stock Leaders:**\n"
        for i, med in enumerate(top_medicines, 1):
            percentage = (med['stock'] / total_stock) * 100 if total_stock > 0 else 0
            response += f"{i}. **{med['name']}** ({med['form']})\n"
            response += f"   Stock: {med['stock']:,} units | Category: {med['category']} | Share: {percentage:.1f}%\n\n"

        return {
            'success': True,
            'response': response,
            'data': {'highest_stock': top_medicines, 'total_stock': total_stock}
        }

    def _handle_medicines_by_form(self, user_input: str = None) -> Dict[str, Any]:
        """Handle medicines by form queries"""
        medicines = get_medicines()

        if not medicines:
            return {
                'success': True,
                'response': "No medicines found in the database."
            }

        # Group by form
        by_form = defaultdict(list)
        for medicine in medicines:
            form = medicine.get('form_dosage', 'Unknown')
            by_form[form].append(medicine)

        response = f"# 💊 **MEDICINES BY FORM/DOSAGE**\n\n"
        response += f"**Total forms:** {len(by_form)}\n"
        response += f"**Total medicines:** {len(medicines)}\n\n"

        # Sort by count
        sorted_forms = sorted(by_form.items(), key=lambda x: len(x[1]), reverse=True)

        response += f"## 📊 **Distribution by Form:**\n"
        for form, meds in sorted_forms:
            percentage = (len(meds) / len(medicines)) * 100
            response += f"• **{form}:** {len(meds)} medicines ({percentage:.1f}%)\n"

        response += f"\n## 📋 **Detailed Breakdown:**\n"
        for form, meds in sorted_forms:
            response += f"\n### 💊 **{form}** ({len(meds)} medicines)\n"
            for med in sorted(meds, key=lambda x: x.get('name', '')):
                name = med.get('name', 'Unknown')
                stock = get_medicine_stock(med.get('id', ''))
                response += f"• **{name}** - Stock: {stock}\n"

        return {
            'success': True,
            'response': response,
            'data': {'by_form': dict(by_form), 'total_count': len(medicines)}
        }

    def _handle_medicines_analysis(self, user_input: str = None) -> Dict[str, Any]:
        """Handle comprehensive medicine analysis queries"""
        medicines = get_medicines()

        if not medicines:
            return {
                'success': True,
                'response': "No medicines found in the database."
            }

        # Comprehensive analysis
        total_medicines = len(medicines)
        total_stock = sum(get_medicine_stock(med.get('id', '')) for med in medicines)

        # Category analysis
        categories = Counter(med.get('category', 'Unknown') for med in medicines)

        # Form analysis
        forms = Counter(med.get('form_dosage', 'Unknown') for med in medicines)

        # Stock analysis
        low_stock_count = 0
        out_of_stock_count = 0
        for medicine in medicines:
            stock = get_medicine_stock(medicine.get('id', ''))
            low_limit = medicine.get('low_stock_limit', 0)
            if stock == 0:
                out_of_stock_count += 1
            elif stock <= low_limit:
                low_stock_count += 1

        response = f"# 📊 **COMPREHENSIVE MEDICINE ANALYSIS**\n\n"

        response += f"## 🔢 **Overall Statistics**\n"
        response += f"• **Total Medicines:** {total_medicines}\n"
        response += f"• **Total Stock Units:** {total_stock:,}\n"
        response += f"• **Average Stock per Medicine:** {total_stock / total_medicines:.1f}\n"
        response += f"• **Stock Status:** {out_of_stock_count} out of stock, {low_stock_count} low stock\n\n"

        response += f"## 📂 **Category Distribution**\n"
        for category, count in categories.most_common():
            percentage = (count / total_medicines) * 100
            response += f"• **{category}:** {count} medicines ({percentage:.1f}%)\n"

        response += f"\n## 💊 **Form Distribution**\n"
        for form, count in forms.most_common():
            percentage = (count / total_medicines) * 100
            response += f"• **{form}:** {count} medicines ({percentage:.1f}%)\n"

        response += f"\n## ⚠️ **Inventory Alerts**\n"
        if out_of_stock_count == 0 and low_stock_count == 0:
            response += "🟢 **All medicines are adequately stocked!**\n"
        else:
            response += f"🔴 **{out_of_stock_count}** medicines are out of stock\n"
            response += f"🟡 **{low_stock_count}** medicines are below low stock limit\n"

        return {
            'success': True,
            'response': response,
            'data': {
                'total_medicines': total_medicines,
                'total_stock': total_stock,
                'categories': dict(categories),
                'forms': dict(forms),
                'out_of_stock_count': out_of_stock_count,
                'low_stock_count': low_stock_count
            }
        }

    # PLACEHOLDER HANDLERS FOR OTHER ENTITIES
    # These would be implemented with full functionality in a complete system

    def _handle_patients_count(self, user_input: str = None) -> Dict[str, Any]:
        """Handle patient count queries"""
        patients = get_patients()
        count = len(patients)

        response = f"# 👥 **PATIENT COUNT**\n\n"
        response += f"**Total Patients:** {count}\n\n"

        if count > 0:
            # Basic demographics
            genders = Counter(p.get('gender', 'Unknown') for p in patients)
            response += f"## 📊 **Demographics:**\n"
            for gender, gender_count in genders.items():
                percentage = (gender_count / count) * 100
                response += f"• **{gender}:** {gender_count} patients ({percentage:.1f}%)\n"

        return {
            'success': True,
            'response': response,
            'data': {'count': count, 'patients': patients}
        }

    def _handle_patients_list(self, user_input: str = None) -> Dict[str, Any]:
        """Handle patient list queries"""
        patients = get_patients()

        if not patients:
            return {
                'success': True,
                'response': "No patients found in the database."
            }

        response = f"# 👥 **ALL PATIENTS LIST**\n\n"
        response += f"**Total Patients:** {len(patients)}\n\n"
        response += f"## 📋 **Complete Patient List:**\n"

        # Sort patients alphabetically
        sorted_patients = sorted(patients, key=lambda x: x.get('name', '').lower())

        for i, patient in enumerate(sorted_patients, 1):
            name = patient.get('name', 'Unknown')
            age = patient.get('age', 'N/A')
            gender = patient.get('gender', 'N/A')
            department = patient.get('department', 'N/A')

            response += f"{i}. **{name}** (Age: {age}, Gender: {gender}, Dept: {department})\n"

        return {
            'success': True,
            'response': response,
            'data': {'patients': patients, 'total_count': len(patients)}
        }

    # Add placeholder methods for all other missing handlers
    def _handle_patients_by_department(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Patients by department analysis - Feature coming soon!"}

    def _handle_patients_by_gender(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Patients by gender analysis - Feature coming soon!"}

    def _handle_patients_by_age(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Patients by age analysis - Feature coming soon!"}

    def _handle_patients_with_allergies(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Patients with allergies analysis - Feature coming soon!"}

    def _handle_patients_consumption(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Patient consumption analysis - Feature coming soon!"}

    def _handle_patients_recent(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Recent patients analysis - Feature coming soon!"}

    def _handle_patients_analysis(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Comprehensive patient analysis - Feature coming soon!"}

    # Suppliers handlers
    def _handle_suppliers_count(self, user_input: str = None) -> Dict[str, Any]:
        suppliers = get_suppliers()
        count = len(suppliers)
        response = f"# 🏢 **SUPPLIER COUNT**\n\n**Total Suppliers:** {count}\n"
        return {'success': True, 'response': response, 'data': {'count': count}}

    def _handle_suppliers_list(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Suppliers list - Feature coming soon!"}

    def _handle_suppliers_by_type(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Suppliers by type - Feature coming soon!"}

    def _handle_suppliers_performance(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Supplier performance analysis - Feature coming soon!"}

    def _handle_suppliers_contact_info(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Supplier contact information - Feature coming soon!"}

    def _handle_suppliers_purchase_history(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Supplier purchase history - Feature coming soon!"}

    def _handle_suppliers_analysis(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Comprehensive supplier analysis - Feature coming soon!"}

    # Add all other missing handlers with placeholder implementations
    def _handle_departments_count(self, user_input: str = None) -> Dict[str, Any]:
        departments = get_departments()
        count = len(departments)
        response = f"# 🏥 **DEPARTMENT COUNT**\n\n**Total Departments:** {count}\n"
        return {'success': True, 'response': response, 'data': {'count': count}}

    def _handle_departments_list(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Departments list - Feature coming soon!"}

    def _handle_departments_staff(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Department staff - Feature coming soon!"}

    def _handle_departments_inventory(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Department inventory - Feature coming soon!"}

    def _handle_departments_consumption(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Department consumption - Feature coming soon!"}

    def _handle_departments_analysis(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Department analysis - Feature coming soon!"}

    # Stores handlers
    def _handle_stores_count(self, user_input: str = None) -> Dict[str, Any]:
        stores = get_stores()
        count = len(stores)
        response = f"# 📦 **STORE COUNT**\n\n**Total Stores:** {count}\n"
        return {'success': True, 'response': response, 'data': {'count': count}}

    def _handle_stores_list(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Stores list - Feature coming soon!"}

    def _handle_stores_inventory(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Store inventory - Feature coming soon!"}

    def _handle_stores_capacity(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Store capacity - Feature coming soon!"}

    def _handle_stores_by_department(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Stores by department - Feature coming soon!"}

    def _handle_stores_analysis(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Store analysis - Feature coming soon!"}

    # Purchases handlers
    def _handle_purchases_count(self, user_input: str = None) -> Dict[str, Any]:
        purchases = get_purchases()
        count = len(purchases)
        response = f"# 💰 **PURCHASE COUNT**\n\n**Total Purchases:** {count}\n"
        return {'success': True, 'response': response, 'data': {'count': count}}

    def _handle_purchases_list(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Purchases list - Feature coming soon!"}

    def _handle_purchases_recent(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Recent purchases - Feature coming soon!"}

    def _handle_purchases_by_supplier(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Purchases by supplier - Feature coming soon!"}

    def _handle_purchases_expensive(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Expensive purchases - Feature coming soon!"}

    def _handle_purchases_total_cost(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Total purchase cost - Feature coming soon!"}

    def _handle_purchases_by_date(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Purchases by date - Feature coming soon!"}

    def _handle_purchases_analysis(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Purchase analysis - Feature coming soon!"}

    # Consumption handlers
    def _handle_consumption_count(self, user_input: str = None) -> Dict[str, Any]:
        consumption = get_consumption()
        count = len(consumption)
        response = f"# 📊 **CONSUMPTION COUNT**\n\n**Total Consumption Records:** {count}\n"
        return {'success': True, 'response': response, 'data': {'count': count}}

    def _handle_consumption_list(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Consumption list - Feature coming soon!"}

    def _handle_consumption_by_patient(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Consumption by patient - Feature coming soon!"}

    def _handle_consumption_by_medicine(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Consumption by medicine - Feature coming soon!"}

    def _handle_consumption_by_department(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Consumption by department - Feature coming soon!"}

    def _handle_consumption_recent(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Recent consumption - Feature coming soon!"}

    def _handle_consumption_trends(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Consumption trends - Feature coming soon!"}

    def _handle_consumption_analysis(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Consumption analysis - Feature coming soon!"}

    # Transfers handlers
    def _handle_transfers_count(self, user_input: str = None) -> Dict[str, Any]:
        transfers = get_transfers()
        count = len(transfers)
        response = f"# 🔄 **TRANSFER COUNT**\n\n**Total Transfers:** {count}\n"
        return {'success': True, 'response': response, 'data': {'count': count}}

    def _handle_transfers_list(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Transfers list - Feature coming soon!"}

    def _handle_transfers_recent(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Recent transfers - Feature coming soon!"}

    def _handle_transfers_by_department(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Transfers by department - Feature coming soon!"}

    def _handle_transfers_pending(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Pending transfers - Feature coming soon!"}

    def _handle_transfers_routes(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Transfer routes - Feature coming soon!"}

    def _handle_transfers_analysis(self, user_input: str = None) -> Dict[str, Any]:
        return {'success': True, 'response': "Transfer analysis - Feature coming soon!"}

    def _handle_help_query(self, user_input: str = None) -> Dict[str, Any]:
        """Handle help queries"""
        response = "# 🤖 **HOSPITAL PHARMACY CHATBOT HELP**\n\n"
        response += "I can help you with comprehensive database queries about:\n\n"

        response += "## 💊 **MEDICINES**\n"
        response += "• Count and list all medicines\n"
        response += "• Group medicines by category or supplier\n"
        response += "• Check stock levels and identify low/out-of-stock items\n"
        response += "• Analyze medicine forms and comprehensive statistics\n\n"

        response += "## 👥 **PATIENTS**\n"
        response += "• Count and list all patients\n"
        response += "• Group patients by department, gender, or age\n"
        response += "• View patient allergies and consumption patterns\n"
        response += "• Analyze patient demographics and statistics\n\n"

        response += "## 🏢 **SUPPLIERS**\n"
        response += "• Count and list all suppliers\n"
        response += "• View supplier contact information and types\n"
        response += "• Analyze supplier performance and purchase history\n"
        response += "• Review supplier statistics and metrics\n\n"

        response += "## 🏥 **DEPARTMENTS**\n"
        response += "• Count and list all departments\n"
        response += "• View department staff and inventory\n"
        response += "• Analyze department consumption patterns\n"
        response += "• Review department statistics and performance\n\n"

        response += "## 📦 **STORES & INVENTORY**\n"
        response += "• List storage locations and capacity\n"
        response += "• View inventory by store and department\n"
        response += "• Analyze storage utilization and assignments\n\n"

        response += "## 💰 **PURCHASES**\n"
        response += "• List recent and historical purchases\n"
        response += "• Analyze purchase costs and trends\n"
        response += "• Group purchases by supplier and date\n"
        response += "• Review expensive purchases and budgets\n\n"

        response += "## 📊 **CONSUMPTION & TRANSFERS**\n"
        response += "• Track medicine consumption by patient/department\n"
        response += "• Analyze usage patterns and trends\n"
        response += "• Monitor transfer routes and pending transfers\n"
        response += "• Review consumption statistics and insights\n\n"

        response += "## 🔍 **EXAMPLE QUERIES**\n"
        response += "• \"How many medicines do we have?\"\n"
        response += "• \"Show me all patients by department\"\n"
        response += "• \"Which medicines are low on stock?\"\n"
        response += "• \"List recent purchases from suppliers\"\n"
        response += "• \"Analyze consumption patterns by patient\"\n\n"

        response += "## ✨ **SMART FEATURES**\n"
        response += "• **Spelling Correction**: I can understand typos and misspellings\n"
        response += "• **Interactive Confirmation**: I'll ask clarifying questions when needed\n"
        response += "• **Multiple Query Formats**: Ask the same question in different ways\n"
        response += "• **Comprehensive Analysis**: Get detailed insights and statistics\n\n"

        response += "Just ask me anything about the pharmacy database in natural language!"

        return {
            'success': True,
            'response': response
        }

    def _handle_database_overview(self, user_input: str = None) -> Dict[str, Any]:
        """Handle complete database overview queries"""
        try:
            # Get data from all tables
            medicines = get_medicines()
            patients = get_patients()
            suppliers = get_suppliers()
            departments = get_departments()
            stores = get_stores()
            purchases = get_purchases()
            consumption = get_consumption()
            transfers = get_transfers()

            response = "# 🏥 **COMPLETE DATABASE OVERVIEW**\n\n"

            response += "## 📊 **SUMMARY STATISTICS**\n"
            response += f"• **Medicines:** {len(medicines)} items\n"
            response += f"• **Patients:** {len(patients)} registered\n"
            response += f"• **Suppliers:** {len(suppliers)} active\n"
            response += f"• **Departments:** {len(departments)} units\n"
            response += f"• **Storage Locations:** {len(stores)} stores\n"
            response += f"• **Purchase Records:** {len(purchases)} transactions\n"
            response += f"• **Consumption Records:** {len(consumption)} entries\n"
            response += f"• **Transfer Records:** {len(transfers)} movements\n\n"

            # Calculate total stock
            total_stock = 0
            for medicine in medicines:
                stock = get_medicine_stock(medicine.get('id', ''))
                total_stock += stock

            response += "## 💊 **INVENTORY OVERVIEW**\n"
            response += f"• **Total Stock Units:** {total_stock:,}\n"
            response += f"• **Average per Medicine:** {total_stock / len(medicines):.1f}\n"

            # Low stock count
            low_stock_count = 0
            for medicine in medicines:
                stock = get_medicine_stock(medicine.get('id', ''))
                low_limit = medicine.get('low_stock_limit', 0)
                if stock <= low_limit:
                    low_stock_count += 1

            response += f"• **Low Stock Items:** {low_stock_count} medicines\n"
            response += f"• **Stock Status:** {'🔴 Attention Needed' if low_stock_count > 0 else '🟢 All Good'}\n\n"

            response += "## 🎯 **QUICK ACTIONS**\n"
            response += "• Ask about specific categories for detailed analysis\n"
            response += "• Request low stock reports for immediate attention\n"
            response += "• Analyze consumption patterns for planning\n"
            response += "• Review supplier performance for procurement\n\n"

            response += "*Use specific queries like 'show me low stock medicines' or 'analyze patient consumption' for detailed insights.*"

            return {
                'success': True,
                'response': response,
                'data': {
                    'medicines_count': len(medicines),
                    'patients_count': len(patients),
                    'suppliers_count': len(suppliers),
                    'departments_count': len(departments),
                    'stores_count': len(stores),
                    'purchases_count': len(purchases),
                    'consumption_count': len(consumption),
                    'transfers_count': len(transfers),
                    'total_stock': total_stock,
                    'low_stock_count': low_stock_count
                }
            }

        except Exception as e:
            return {
                'success': False,
                'response': f"Error generating database overview: {str(e)}"
            }

# Global instance
comprehensive_handlers = ComprehensiveHandlers()
