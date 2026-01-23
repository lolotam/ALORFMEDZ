"""
Medicine Query Handlers
Handles all medicine-related queries
"""

from typing import Dict, List, Any
from collections import Counter
from .base import BaseHandler
from app.utils.database import get_medicines, get_suppliers, get_medicine_stock


class MedicineHandler(BaseHandler):
    """Handler for medicine queries"""

    SUPPORTED_QUERIES = [
        'medicines_count', 'medicines_list', 'medicines_by_category',
        'medicines_by_supplier', 'medicines_stock_levels', 'medicines_low_stock',
        'medicines_out_of_stock', 'medicines_highest_stock', 'medicines_by_form',
        'medicines_analysis'
    ]

    def can_handle(self, query_type: str) -> bool:
        """Check if this handler can process the query"""
        return query_type in self.SUPPORTED_QUERIES

    def handle(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the query"""
        query_type = query_data.get('type')
        user_input = query_data.get('input', '')

        handler_map = {
            'medicines_count': self._handle_count,
            'medicines_list': self._handle_list,
            'medicines_by_category': self._handle_by_category,
            'medicines_by_supplier': self._handle_by_supplier,
            'medicines_stock_levels': self._handle_stock_levels,
            'medicines_low_stock': self._handle_low_stock,
            'medicines_out_of_stock': self._handle_out_of_stock,
            'medicines_highest_stock': self._handle_highest_stock,
            'medicines_by_form': self._handle_by_form,
            'medicines_analysis': self._handle_analysis
        }

        handler = handler_map.get(query_type)
        if handler:
            return handler(user_input)

        return self.format_error_response(f"Unknown medicine query type: {query_type}")

    def get_supported_query_types(self) -> List[str]:
        """Get supported query types"""
        return self.SUPPORTED_QUERIES

    def _handle_count(self, user_input: str) -> Dict[str, Any]:
        """Handle medicine count queries"""
        medicines = get_medicines()
        count = len(medicines)

        response = f"# 💊 **MEDICINE COUNT**\n\n"
        response += f"**Total Medicines:** {count}\n\n"

        if count > 0:
            suppliers = get_suppliers()
            supplier_counts = Counter(med.get('supplier_id') for med in medicines)

            response += f"## 📊 **Additional Statistics:**\n"
            response += f"• **Unique Suppliers:** {len(supplier_counts)}\n"
            response += f"• **Average per Supplier:** {count / len(supplier_counts):.1f}\n"

            forms = Counter(med.get('form_dosage', 'Unknown') for med in medicines)
            response += f"• **Most Common Form:** {forms.most_common(1)[0][0]} ({forms.most_common(1)[0][1]} medicines)\n"

        return self.format_success_response(response, {'count': count, 'medicines': medicines})

    def _handle_list(self, user_input: str) -> Dict[str, Any]:
        """Handle medicine list queries"""
        medicines = get_medicines()

        if not medicines:
            return self.format_success_response("No medicines found in the database.")

        response = f"# 💊 **ALL MEDICINES LIST**\n\n"
        response += f"**Total Medicines:** {len(medicines)}\n\n"
        response += f"## 📋 **Complete Medicine List:**\n"

        sorted_medicines = sorted(medicines, key=lambda x: x.get('name', '').lower())

        for i, medicine in enumerate(sorted_medicines, 1):
            name = medicine.get('name', 'Unknown')
            form = medicine.get('form_dosage', 'N/A')
            stock = get_medicine_stock(medicine.get('id', ''))
            response += f"{i}. **{name}** ({form}) - Stock: {stock}\n"

        return self.format_success_response(response, {'medicines': medicines, 'total_count': len(medicines)})

    def _handle_by_category(self, user_input: str) -> Dict[str, Any]:
        """Handle medicines by category queries"""
        from collections import defaultdict

        medicines = get_medicines()

        if not medicines:
            return self.format_success_response("No medicines found in the database.")

        categories = defaultdict(list)
        for medicine in medicines:
            category = medicine.get('category', 'Uncategorized')
            categories[category].append(medicine)

        response = f"# 💊 **MEDICINES BY CATEGORY**\n\n"
        response += f"**Total Categories:** {len(categories)}\n"
        response += f"**Total Medicines:** {len(medicines)}\n\n"

        sorted_categories = sorted(categories.items(), key=lambda x: len(x[1]), reverse=True)

        for category, meds in sorted_categories:
            response += f"## 📂 **{category}** ({len(meds)} medicines)\n"
            for med in sorted(meds, key=lambda x: x.get('name', '')):
                name = med.get('name', 'Unknown')
                form = med.get('form_dosage', 'N/A')
                response += f"• **{name}** ({form})\n"
            response += "\n"

        return self.format_success_response(response, {'categories': dict(categories), 'total_count': len(medicines)})

    def _handle_by_supplier(self, user_input: str) -> Dict[str, Any]:
        """Handle medicines by supplier queries"""
        from collections import defaultdict

        medicines = get_medicines()
        suppliers = get_suppliers()

        if not medicines:
            return self.format_success_response("No medicines found in the database.")

        supplier_lookup = {s.get('id'): s.get('name', 'Unknown') for s in suppliers}

        by_supplier = defaultdict(list)
        for medicine in medicines:
            supplier_id = medicine.get('supplier_id', 'Unknown')
            supplier_name = supplier_lookup.get(supplier_id, f'Unknown Supplier ({supplier_id})')
            by_supplier[supplier_name].append(medicine)

        response = f"# 💊 **MEDICINES BY SUPPLIER**\n\n"
        response += f"**Total Suppliers:** {len(by_supplier)}\n"
        response += f"**Total Medicines:** {len(medicines)}\n\n"

        sorted_suppliers = sorted(by_supplier.items(), key=lambda x: len(x[1]), reverse=True)

        for supplier_name, meds in sorted_suppliers:
            response += f"## 🏢 **{supplier_name}** ({len(meds)} medicines)\n"
            for med in sorted(meds, key=lambda x: x.get('name', '')):
                name = med.get('name', 'Unknown')
                form = med.get('form_dosage', 'N/A')
                stock = get_medicine_stock(med.get('id', ''))
                response += f"• **{name}** ({form}) - Stock: {stock}\n"
            response += "\n"

        return self.format_success_response(response, {'by_supplier': dict(by_supplier), 'total_count': len(medicines)})

    def _handle_stock_levels(self, user_input: str) -> Dict[str, Any]:
        """Handle medicine stock levels queries"""
        medicines = get_medicines()

        if not medicines:
            return self.format_success_response("No medicines found in the database.")

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

        return self.format_success_response(response, {'medicine_stocks': medicine_stocks, 'total_stock': total_stock})

    def _handle_low_stock(self, user_input: str) -> Dict[str, Any]:
        """Handle low stock medicines queries"""
        medicines = get_medicines()

        if not medicines:
            return self.format_success_response("No medicines found in the database.")

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

            low_stock_medicines.sort(key=lambda x: x['stock'])

            for i, med in enumerate(low_stock_medicines, 1):
                urgency = "🔴 CRITICAL" if med['stock'] == 0 else "🟡 LOW"
                response += f"{i}. **{med['name']}** ({med['form']})\n"
                response += f"   Current Stock: {med['stock']} | Limit: {med['low_limit']} | Status: {urgency}\n\n"

        return self.format_success_response(response, {'low_stock_medicines': low_stock_medicines, 'total_count': len(medicines)})

    def _handle_out_of_stock(self, user_input: str) -> Dict[str, Any]:
        """Handle out of stock medicines queries"""
        from collections import defaultdict

        medicines = get_medicines()

        if not medicines:
            return self.format_success_response("No medicines found in the database.")

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

            by_category = defaultdict(list)
            for med in out_of_stock:
                by_category[med['category']].append(med)

            for category, meds in by_category.items():
                response += f"\n### 📂 **{category}** ({len(meds)} medicines)\n"
                for med in sorted(meds, key=lambda x: x['name']):
                    response += f"• **{med['name']}** ({med['form']})\n"

        return self.format_success_response(response, {'out_of_stock': out_of_stock, 'total_count': len(medicines)})

    def _handle_highest_stock(self, user_input: str) -> Dict[str, Any]:
        """Handle highest stock medicines queries"""
        medicines = get_medicines()

        if not medicines:
            return self.format_success_response("No medicines found in the database.")

        medicine_stocks = []
        for medicine in medicines:
            stock = get_medicine_stock(medicine.get('id', ''))
            medicine_stocks.append({
                'name': medicine.get('name', 'Unknown'),
                'form': medicine.get('form_dosage', 'N/A'),
                'stock': stock,
                'category': medicine.get('category', 'Unknown')
            })

        medicine_stocks.sort(key=lambda x: x['stock'], reverse=True)
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

        return self.format_success_response(response, {'highest_stock': top_medicines, 'total_stock': total_stock})

    def _handle_by_form(self, user_input: str) -> Dict[str, Any]:
        """Handle medicines by form queries"""
        from collections import defaultdict

        medicines = get_medicines()

        if not medicines:
            return self.format_success_response("No medicines found in the database.")

        by_form = defaultdict(list)
        for medicine in medicines:
            form = medicine.get('form_dosage', 'Unknown')
            by_form[form].append(medicine)

        response = f"# 💊 **MEDICINES BY FORM/DOSAGE**\n\n"
        response += f"**Total forms:** {len(by_form)}\n"
        response += f"**Total medicines:** {len(medicines)}\n\n"

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

        return self.format_success_response(response, {'by_form': dict(by_form), 'total_count': len(medicines)})

    def _handle_analysis(self, user_input: str) -> Dict[str, Any]:
        """Handle comprehensive medicine analysis queries"""
        medicines = get_medicines()

        if not medicines:
            return self.format_success_response("No medicines found in the database.")

        total_medicines = len(medicines)
        total_stock = sum(get_medicine_stock(med.get('id', '')) for med in medicines)

        categories = Counter(med.get('category', 'Unknown') for med in medicines)
        forms = Counter(med.get('form_dosage', 'Unknown') for med in medicines)

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

        return self.format_success_response(response, {
            'total_medicines': total_medicines,
            'total_stock': total_stock,
            'categories': dict(categories),
            'forms': dict(forms),
            'out_of_stock_count': out_of_stock_count,
            'low_stock_count': low_stock_count
        })
