#!/usr/bin/env python3
"""
Script to add 20 new sample purchase records with specific purchaser names
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import get_suppliers, get_medicines, save_data, load_data, generate_id
from datetime import datetime, timedelta
import random

def generate_realistic_purchases():
    """Generate 20 realistic purchase records"""
    
    # Get available suppliers and medicines
    suppliers = get_suppliers()
    medicines = get_medicines()
    supplier_ids = [s['id'] for s in suppliers]
    medicine_ids = [m['id'] for m in medicines]
    
    # Specific purchaser names as requested
    purchaser_names = ["Waleed", "Charlotte", "Marlen"]
    
    # Payment methods
    payment_methods = ["Bank Transfer", "Credit Card", "Cash", "Check", "Wire Transfer"]
    
    # Status options
    status_options = ["completed", "pending", "delivered"]
    
    print(f"Adding 20 new purchase records...")
    
    purchases = load_data('purchases')
    
    for i in range(1, 21):
        # Generate realistic purchase data
        supplier_id = random.choice(supplier_ids)
        supplier = next(s for s in suppliers if s['id'] == supplier_id)
        
        # Generate medicines for this purchase (1-5 medicines per purchase)
        num_medicines = random.randint(1, 5)
        selected_medicines = random.sample(medicine_ids, min(num_medicines, len(medicine_ids)))
        
        medicines_list = []
        total_amount = 0
        
        for med_id in selected_medicines:
            quantity = random.randint(50, 500)
            unit_price = round(random.uniform(5.0, 200.0), 2)
            medicine_total = quantity * unit_price
            total_amount += medicine_total
            
            medicines_list.append({
                "medicine_id": med_id,
                "quantity": quantity,
                "unit_price": unit_price,
                "total_price": medicine_total
            })
        
        # Generate purchase record
        purchase_record = {
            'id': generate_id('purchases'),
            'supplier_id': supplier_id,
            'invoice_number': f"INV-{random.randint(1000, 9999)}",
            'purchase_date': generate_purchase_date(),
            'medicines': medicines_list,
            'total_amount': round(total_amount, 2),
            'status': random.choice(status_options),
            'notes': f"Bulk purchase from {supplier['name']}",
            'created_at': datetime.now().isoformat(),
            'delivery_date': generate_delivery_date(),
            'payment_method': random.choice(payment_methods),
            'received_by': random.choice(purchaser_names)  # Using specific names as requested
        }
        
        try:
            purchases.append(purchase_record)
            print(f"✓ Added purchase {i}/20: Invoice {purchase_record['invoice_number']} - Received by {purchase_record['received_by']} (ID: {purchase_record['id']})")
        except Exception as e:
            print(f"✗ Error adding purchase {i}: {e}")
    
    # Save all purchases
    save_data('purchases', purchases)
    print(f"\n✅ Successfully added 20 new purchase records!")

def generate_purchase_date():
    """Generate realistic purchase date (within last 6 months)"""
    days_ago = random.randint(1, 180)  # 1 day to 6 months ago
    purchase_date = datetime.now() - timedelta(days=days_ago)
    return purchase_date.strftime('%Y-%m-%d')

def generate_delivery_date():
    """Generate realistic delivery date (1-7 days after purchase)"""
    days_after = random.randint(1, 7)
    purchase_date = datetime.now() - timedelta(days=random.randint(1, 180))
    delivery_date = purchase_date + timedelta(days=days_after)
    return delivery_date.strftime('%Y-%m-%d')

if __name__ == "__main__":
    generate_realistic_purchases()
