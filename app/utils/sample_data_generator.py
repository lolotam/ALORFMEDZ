"""
Sample Data Generator
Creates additional realistic sample records for inventory transfers and purchases
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List
from app.utils.database import (
    get_medicines, get_stores, get_suppliers, get_transfers, get_purchases,
    save_data, generate_id
)

class SampleDataGenerator:
    def __init__(self):
        self.medicines = get_medicines()
        self.stores = get_stores()
        self.suppliers = get_suppliers()
        self.transfers = get_transfers()
        self.purchases = get_purchases()
        
        # Get current max IDs
        self.next_transfer_id = self._get_next_id(self.transfers)
        self.next_purchase_id = self._get_next_id(self.purchases)

    def _get_next_id(self, records: List[Dict]) -> str:
        """Get next available ID for records"""
        if not records:
            return "01"
        
        max_id = max([int(record['id']) for record in records if record['id'].isdigit()])
        return f"{max_id + 1:02d}"

    def create_inventory_transfers(self, count: int = 10):
        """Create realistic inventory transfer records"""
        print(f"Creating {count} inventory transfer records...")
        
        new_transfers = []
        
        for i in range(count):
            # Select random source and destination stores (different stores)
            source_store = random.choice(self.stores)
            destination_stores = [s for s in self.stores if s['id'] != source_store['id']]
            destination_store = random.choice(destination_stores)
            
            # Select 1-3 random medicines for transfer
            num_medicines = random.randint(1, 3)
            selected_medicines = random.sample(self.medicines, num_medicines)
            
            medicines_list = []
            for medicine in selected_medicines:
                # Transfer reasonable quantities (5-50 units)
                quantity = random.randint(5, 50)
                medicines_list.append({
                    "medicine_id": medicine['id'],
                    "quantity": quantity
                })
            
            # Generate transfer date (within last 60 days)
            days_ago = random.randint(1, 60)
            transfer_date = datetime.now() - timedelta(days=days_ago)
            
            # Create transfer record
            transfer_record = {
                "id": self.next_transfer_id,
                "source_store_id": source_store['id'],
                "destination_store_id": destination_store['id'],
                "medicines": medicines_list,
                "transfer_date": transfer_date.strftime('%Y-%m-%d'),
                "notes": f"Transfer from {source_store['name']} to {destination_store['name']}",
                "status": random.choice(["completed", "pending", "in_transit"]),
                "requested_by": random.choice([
                    "Dr. Smith", "Nurse Johnson", "Pharmacist Brown", 
                    "Dr. Wilson", "Nurse Davis", "Dr. Martinez"
                ]),
                "approved_by": random.choice([
                    "Pharmacy Manager", "Department Head", 
                    "Chief Pharmacist", "Medical Director"
                ]),
                "created_at": transfer_date.isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            new_transfers.append(transfer_record)
            
            # Increment ID for next record
            self.next_transfer_id = f"{int(self.next_transfer_id) + 1:02d}"
        
        # Add new transfers to existing transfers
        self.transfers.extend(new_transfers)
        save_data('transfers', self.transfers)
        
        print(f"Created {len(new_transfers)} new transfer records")
        return len(new_transfers)

    def create_purchase_records(self, count: int = 15):
        """Create additional purchase records"""
        print(f"Creating {count} purchase records...")
        
        new_purchases = []
        
        for i in range(count):
            # Select random supplier
            supplier = random.choice(self.suppliers)
            
            # Select 2-5 random medicines for purchase
            num_medicines = random.randint(2, 5)
            selected_medicines = random.sample(self.medicines, num_medicines)
            
            medicines_list = []
            total_amount = 0
            
            for medicine in selected_medicines:
                # Purchase reasonable quantities (50-500 units)
                quantity = random.randint(50, 500)
                # Generate realistic price per unit ($1-50)
                unit_price = round(random.uniform(1.0, 50.0), 2)
                medicine_total = quantity * unit_price
                total_amount += medicine_total
                
                medicines_list.append({
                    "medicine_id": medicine['id'],
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total_price": round(medicine_total, 2)
                })
            
            # Generate purchase date (within last 90 days)
            days_ago = random.randint(1, 90)
            purchase_date = datetime.now() - timedelta(days=days_ago)
            
            # Generate delivery date (1-7 days after purchase)
            delivery_days = random.randint(1, 7)
            delivery_date = purchase_date + timedelta(days=delivery_days)
            
            # Generate invoice number
            invoice_number = f"INV-{random.randint(1000, 9999)}"
            
            # Create purchase record
            purchase_record = {
                "id": self.next_purchase_id,
                "supplier_id": supplier['id'],
                "invoice_number": invoice_number,
                "purchase_date": purchase_date.strftime('%Y-%m-%d'),
                "delivery_date": delivery_date.strftime('%Y-%m-%d'),
                "medicines": medicines_list,
                "total_amount": round(total_amount, 2),
                "status": random.choice(["completed", "pending", "delivered", "cancelled"]),
                "payment_method": random.choice([
                    "Bank Transfer", "Credit Card", "Cash", "Check", "Net 30"
                ]),
                "received_by": random.choice([
                    "John Doe", "Jane Smith", "Mike Johnson", 
                    "Sarah Wilson", "Tom Brown", "Lisa Davis"
                ]),
                "notes": f"Purchase from {supplier['name']} - {invoice_number}",
                "created_at": purchase_date.isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            new_purchases.append(purchase_record)
            
            # Increment ID for next record
            self.next_purchase_id = f"{int(self.next_purchase_id) + 1:02d}"
        
        # Add new purchases to existing purchases
        self.purchases.extend(new_purchases)
        save_data('purchases', self.purchases)
        
        print(f"Created {len(new_purchases)} new purchase records")
        return len(new_purchases)

    def generate_all_sample_data(self):
        """Generate all sample data"""
        print("=== Starting Sample Data Generation ===\n")
        
        results = {
            'transfers': self.create_inventory_transfers(10),
            'purchases': self.create_purchase_records(15)
        }
        
        print(f"\n=== Sample Data Generation Summary ===")
        for data_type, count in results.items():
            print(f"{data_type.capitalize()}: {count} records created")
        
        total_created = sum(results.values())
        print(f"Total new records created: {total_created}")
        
        return results

if __name__ == "__main__":
    generator = SampleDataGenerator()
    generator.generate_all_sample_data()
