"""
Enhanced Database Access Layer for AI Chatbot
Provides comprehensive data access and administrative operations for the AI chatbot
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from app.utils.database import (
    get_medicines, get_patients, get_suppliers, get_departments, 
    get_stores, get_purchases, get_consumption, get_transfers,
    save_medicine, update_medicine, delete_medicine,
    save_patient, update_patient, delete_patient,
    save_supplier, update_supplier, delete_supplier,
    save_department, update_department, delete_department,
    save_purchase, update_purchase, delete_purchase,
    save_consumption, get_medicine_stock, log_activity,
    update_store_inventory, get_low_stock_medicines
)

class ChatbotDatabaseManager:
    """Enhanced database manager for AI chatbot with comprehensive access and operations"""
    
    def __init__(self):
        self.data_sources = {
            'medicines': get_medicines,
            'patients': get_patients,
            'suppliers': get_suppliers,
            'departments': get_departments,
            'stores': get_stores,
            'purchases': get_purchases,
            'consumption': get_consumption,
            'transfers': get_transfers
        }
    
    def get_comprehensive_data(self) -> Dict[str, Any]:
        """Get all data from all tables for comprehensive analysis"""
        try:
            data = {}
            for source_name, source_func in self.data_sources.items():
                data[source_name] = source_func()
            
            # Add calculated fields
            data['analytics'] = self._calculate_analytics(data)
            data['inventory_summary'] = self._get_inventory_summary(data)
            data['low_stock_alerts'] = get_low_stock_medicines()
            
            return data
        except Exception as e:
            print(f"Error getting comprehensive data: {e}")
            return {}
    
    def _calculate_analytics(self, data: Dict) -> Dict[str, Any]:
        """Calculate advanced analytics from the data"""
        try:
            analytics = {
                'total_counts': {
                    'medicines': len(data.get('medicines', [])),
                    'patients': len(data.get('patients', [])),
                    'suppliers': len(data.get('suppliers', [])),
                    'departments': len(data.get('departments', [])),
                    'stores': len(data.get('stores', [])),
                    'purchases': len(data.get('purchases', [])),
                    'consumption_records': len(data.get('consumption', [])),
                    'transfers': len(data.get('transfers', []))
                }
            }
            
            # Medicine analytics
            medicines = data.get('medicines', [])
            if medicines:
                categories = {}
                for med in medicines:
                    cat = med.get('category', 'Unknown')
                    categories[cat] = categories.get(cat, 0) + 1
                analytics['medicine_categories'] = categories
            
            # Purchase analytics
            purchases = data.get('purchases', [])
            if purchases:
                total_cost = sum(float(p.get('total_cost', 0)) for p in purchases)
                analytics['total_purchase_cost'] = total_cost
                
                # Recent purchases (last 30 days)
                thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                recent_purchases = [p for p in purchases if p.get('date', '') >= thirty_days_ago]
                analytics['recent_purchases_count'] = len(recent_purchases)
                analytics['recent_purchase_cost'] = sum(float(p.get('total_cost', 0)) for p in recent_purchases)
            
            # Consumption analytics
            consumption = data.get('consumption', [])
            if consumption:
                thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                recent_consumption = [c for c in consumption if c.get('date', '') >= thirty_days_ago]
                analytics['recent_consumption_count'] = len(recent_consumption)
                
                # Patient consumption patterns
                patient_consumption = {}
                for record in recent_consumption:
                    patient_id = record.get('patient_id')
                    if patient_id:
                        patient_consumption[patient_id] = patient_consumption.get(patient_id, 0) + 1
                analytics['top_consuming_patients'] = sorted(
                    patient_consumption.items(), key=lambda x: x[1], reverse=True
                )[:5]
            
            return analytics
        except Exception as e:
            print(f"Error calculating analytics: {e}")
            return {}
    
    def _get_inventory_summary(self, data: Dict) -> Dict[str, Any]:
        """Get comprehensive inventory summary"""
        try:
            stores = data.get('stores', [])
            medicines = data.get('medicines', [])
            
            # Calculate total inventory across all stores
            total_inventory = {}
            store_inventories = {}
            
            for store in stores:
                store_name = store.get('name', f"Store {store.get('id', 'Unknown')}")
                store_inventories[store_name] = store.get('inventory', {})
                
                for med_id, quantity in store.get('inventory', {}).items():
                    total_inventory[med_id] = total_inventory.get(med_id, 0) + quantity
            
            # Find highest and lowest stock medicines
            medicine_stocks = []
            for medicine in medicines:
                med_id = medicine['id']
                stock = total_inventory.get(med_id, 0)
                medicine_stocks.append({
                    'id': med_id,
                    'name': medicine.get('name', 'Unknown'),
                    'stock': stock,
                    'category': medicine.get('category', 'Unknown'),
                    'low_stock_limit': medicine.get('low_stock_limit', 0)
                })
            
            # Sort by stock levels
            medicine_stocks.sort(key=lambda x: x['stock'], reverse=True)
            
            return {
                'total_inventory': total_inventory,
                'store_inventories': store_inventories,
                'highest_stock_medicines': medicine_stocks[:10],
                'lowest_stock_medicines': medicine_stocks[-10:],
                'total_medicines_in_stock': len([m for m in medicine_stocks if m['stock'] > 0]),
                'out_of_stock_medicines': len([m for m in medicine_stocks if m['stock'] == 0])
            }
        except Exception as e:
            print(f"Error getting inventory summary: {e}")
            return {}
    
    def search_data(self, query: str, data_type: str = None) -> Dict[str, List]:
        """Advanced search across all data types"""
        try:
            results = {}
            query_lower = query.lower()
            
            search_targets = [data_type] if data_type else self.data_sources.keys()
            
            for source_name in search_targets:
                if source_name in self.data_sources:
                    data = self.data_sources[source_name]()
                    matches = []
                    
                    for item in data:
                        # Search in all string fields
                        for key, value in item.items():
                            if isinstance(value, str) and query_lower in value.lower():
                                matches.append(item)
                                break
                    
                    if matches:
                        results[source_name] = matches
            
            return results
        except Exception as e:
            print(f"Error searching data: {e}")
            return {}
    
    def get_advanced_analytics(self, query_type: str, **kwargs) -> Dict[str, Any]:
        """Get advanced analytics based on query type"""
        try:
            if query_type == "highest_stock":
                return self._get_highest_stock_analysis()
            elif query_type == "top_consuming_patients":
                return self._get_top_consuming_patients(**kwargs)
            elif query_type == "expensive_purchases":
                return self._get_expensive_purchases(**kwargs)
            elif query_type == "department_stock_analysis":
                return self._get_department_stock_analysis()
            elif query_type == "expiry_analysis":
                return self._get_expiry_analysis(**kwargs)
            else:
                return {"error": f"Unknown query type: {query_type}"}
        except Exception as e:
            return {"error": f"Error in analytics: {str(e)}"}
    
    def _get_highest_stock_analysis(self) -> Dict[str, Any]:
        """Get analysis of medicines with highest stock"""
        try:
            data = self.get_comprehensive_data()
            inventory_summary = data.get('inventory_summary', {})
            highest_stock = inventory_summary.get('highest_stock_medicines', [])
            
            if highest_stock:
                top_medicine = highest_stock[0]
                return {
                    "highest_stock_medicine": top_medicine,
                    "top_10_highest_stock": highest_stock[:10],
                    "analysis": f"The medicine with highest stock is {top_medicine['name']} with {top_medicine['stock']} units."
                }
            else:
                return {"error": "No stock data available"}
        except Exception as e:
            return {"error": f"Error analyzing highest stock: {str(e)}"}
    
    def _get_top_consuming_patients(self, period_days: int = 30) -> Dict[str, Any]:
        """Get top consuming patients analysis"""
        try:
            consumption = get_consumption()
            patients = get_patients()
            
            cutoff_date = (datetime.now() - timedelta(days=period_days)).strftime('%Y-%m-%d')
            recent_consumption = [c for c in consumption if c.get('date', '') >= cutoff_date]
            
            patient_consumption = {}
            for record in recent_consumption:
                patient_id = record.get('patient_id')
                if patient_id:
                    medicines_count = len(record.get('medicines', []))
                    patient_consumption[patient_id] = patient_consumption.get(patient_id, 0) + medicines_count
            
            # Get patient details
            top_patients = []
            for patient_id, consumption_count in sorted(patient_consumption.items(), key=lambda x: x[1], reverse=True)[:10]:
                patient = next((p for p in patients if p['id'] == patient_id), None)
                if patient:
                    top_patients.append({
                        "patient_id": patient_id,
                        "patient_name": patient.get('name', 'Unknown'),
                        "consumption_count": consumption_count,
                        "department": patient.get('department', 'Unknown')
                    })
            
            return {
                "top_consuming_patients": top_patients,
                "period_days": period_days,
                "total_patients_analyzed": len(patient_consumption)
            }
        except Exception as e:
            return {"error": f"Error analyzing patient consumption: {str(e)}"}
    
    def _get_expensive_purchases(self, limit: int = 5, period_days: int = 365) -> Dict[str, Any]:
        """Get most expensive purchases analysis"""
        try:
            purchases = get_purchases()
            
            cutoff_date = (datetime.now() - timedelta(days=period_days)).strftime('%Y-%m-%d')
            recent_purchases = [p for p in purchases if p.get('date', '') >= cutoff_date]
            
            # Sort by total cost
            expensive_purchases = sorted(
                recent_purchases, 
                key=lambda x: float(x.get('total_cost', 0)), 
                reverse=True
            )[:limit]
            
            return {
                "top_expensive_purchases": expensive_purchases,
                "period_days": period_days,
                "total_purchases_analyzed": len(recent_purchases),
                "total_cost_analyzed": sum(float(p.get('total_cost', 0)) for p in recent_purchases)
            }
        except Exception as e:
            return {"error": f"Error analyzing expensive purchases: {str(e)}"}
    
    def _get_department_stock_analysis(self) -> Dict[str, Any]:
        """Get department-wise stock analysis"""
        try:
            stores = get_stores()
            departments = get_departments()
            
            department_stocks = {}
            for store in stores:
                dept_id = store.get('department_id')
                if dept_id:
                    inventory = store.get('inventory', {})
                    total_items = sum(inventory.values())
                    unique_medicines = len(inventory)
                    
                    dept = next((d for d in departments if d['id'] == dept_id), None)
                    dept_name = dept.get('name', f'Department {dept_id}') if dept else f'Department {dept_id}'
                    
                    department_stocks[dept_name] = {
                        "department_id": dept_id,
                        "total_stock": total_items,
                        "unique_medicines": unique_medicines,
                        "average_stock_per_medicine": total_items / unique_medicines if unique_medicines > 0 else 0
                    }
            
            # Sort by average stock
            sorted_departments = sorted(
                department_stocks.items(), 
                key=lambda x: x[1]['average_stock_per_medicine']
            )
            
            return {
                "department_stock_analysis": department_stocks,
                "lowest_average_stock_department": sorted_departments[0] if sorted_departments else None,
                "highest_average_stock_department": sorted_departments[-1] if sorted_departments else None
            }
        except Exception as e:
            return {"error": f"Error analyzing department stocks: {str(e)}"}
    
    def _get_expiry_analysis(self, days_ahead: int = 30) -> Dict[str, Any]:
        """Get medicines expiring within specified days"""
        try:
            medicines = get_medicines()
            cutoff_date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
            
            expiring_medicines = []
            for medicine in medicines:
                expiry_date = medicine.get('expiry_date')
                if expiry_date and expiry_date <= cutoff_date:
                    stock = get_medicine_stock(medicine['id'])
                    expiring_medicines.append({
                        "id": medicine['id'],
                        "name": medicine.get('name', 'Unknown'),
                        "expiry_date": expiry_date,
                        "current_stock": stock,
                        "category": medicine.get('category', 'Unknown')
                    })
            
            # Sort by expiry date
            expiring_medicines.sort(key=lambda x: x['expiry_date'])
            
            return {
                "expiring_medicines": expiring_medicines,
                "days_ahead": days_ahead,
                "total_expiring": len(expiring_medicines),
                "total_expiring_stock": sum(m['current_stock'] for m in expiring_medicines)
            }
        except Exception as e:
            return {"error": f"Error analyzing expiry dates: {str(e)}"}

# Global instance for easy access
chatbot_db = ChatbotDatabaseManager()
