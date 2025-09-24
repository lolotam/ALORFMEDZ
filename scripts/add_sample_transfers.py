#!/usr/bin/env python3
"""
Script to add 15 new inventory transfer records
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import get_stores, get_medicines, save_data, load_data, generate_id
from datetime import datetime, timedelta
import random

def generate_inventory_transfers():
    """Generate 15 realistic inventory transfer records"""
    
    # Get available data
    stores = get_stores()
    medicines = get_medicines()
    medicine_ids = [m['id'] for m in medicines]
    
    # Find main pharmacy store (usually ID "01")
    main_store = next((s for s in stores if s.get('department_id') == '01'), stores[0])
    
    # Get all other stores (destination stores)
    destination_stores = [s for s in stores if s['id'] != main_store['id']]
    
    # Staff names for transfers
    pharmacists = [
        "Pharmacist Johnson", "Pharmacist Smith", "Pharmacist Brown", "Pharmacist Davis",
        "Pharmacist Wilson", "Pharmacist Miller", "Pharmacist Taylor", "Pharmacist Anderson"
    ]
    
    approvers = [
        "Medical Director", "Pharmacy Director", "Department Head", "Chief Pharmacist",
        "Clinical Supervisor", "Operations Manager"
    ]
    
    print(f"Adding 15 new inventory transfer records...")
    
    transfers = load_data('transfers')

    # Get current max ID to avoid conflicts
    transfer_ids = [int(t['id']) for t in transfers if t['id'].isdigit()]
    next_transfer_id = max(transfer_ids) + 1 if transfer_ids else 1

    for i in range(1, 16):
        # Select random destination store
        destination_store = random.choice(destination_stores)

        # Generate medicines for this transfer (1-4 medicines per transfer)
        num_medicines = random.randint(1, 4)
        selected_medicines = random.sample(medicine_ids, min(num_medicines, len(medicine_ids)))

        medicines_list = []
        for med_id in selected_medicines:
            quantity = random.randint(10, 100)  # Realistic transfer quantities
            medicines_list.append({
                "medicine_id": med_id,
                "quantity": quantity
            })

        # Generate unique transfer ID
        transfer_id = f"{next_transfer_id:02d}"
        next_transfer_id += 1

        # Generate transfer record
        transfer_record = {
            'id': transfer_id,
            'source_store_id': main_store['id'],
            'destination_store_id': destination_store['id'],
            'medicines': medicines_list,
            'notes': f"Transfer to {destination_store['name']}",
            'status': random.choice(['completed', 'pending', 'in_transit']),
            'created_at': datetime.now().isoformat(),
            'transfer_date': generate_transfer_date(),
            'requested_by': random.choice(pharmacists),
            'approved_by': random.choice(approvers)
        }
        
        try:
            transfers.append(transfer_record)
            print(f"✓ Added transfer {i}/15: {main_store['name']} → {destination_store['name']} (ID: {transfer_record['id']})")
        except Exception as e:
            print(f"✗ Error adding transfer {i}: {e}")
    
    # Save all transfers
    save_data('transfers', transfers)
    print(f"\n✅ Successfully added 15 new inventory transfer records!")

def generate_transfer_date():
    """Generate realistic transfer date (within last 2 months)"""
    days_ago = random.randint(1, 60)  # 1 day to 2 months ago
    transfer_date = datetime.now() - timedelta(days=days_ago)
    return transfer_date.strftime('%Y-%m-%d')

if __name__ == "__main__":
    generate_inventory_transfers()
