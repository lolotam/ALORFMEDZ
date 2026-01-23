"""
Purchase Repository Module
Purchase management functions
"""

from datetime import datetime
from typing import List, Dict

from .base import load_data, save_data, generate_id, renumber_ids
from .stores import update_main_store_inventory


def get_purchases() -> List[Dict]:
    """Get all purchases"""
    return load_data('purchases')


def save_purchase(purchase_data: Dict) -> str:
    """Save new purchase and update inventory"""
    purchases = get_purchases()
    purchase_id = generate_id('purchases')
    purchase_data['id'] = purchase_id
    purchase_data['created_at'] = datetime.now().isoformat()
    purchases.append(purchase_data)
    save_data('purchases', purchases)

    # Update main store inventory
    update_main_store_inventory(purchase_data['medicines'], 'add')

    return purchase_id


def update_purchase(purchase_id: str, purchase_data: Dict):
    """Update existing purchase"""
    purchases = get_purchases()
    for i, purchase in enumerate(purchases):
        if purchase['id'] == purchase_id:
            purchase_data['id'] = purchase_id
            purchase_data['updated_at'] = datetime.now().isoformat()
            purchases[i] = {**purchase, **purchase_data}
            break
    save_data('purchases', purchases)


def delete_purchase(purchase_id: str):
    """Delete purchase and renumber remaining records"""
    purchases = get_purchases()
    purchases = [p for p in purchases if p['id'] != purchase_id]
    save_data('purchases', purchases)

    # Renumber purchases (no cascade needed - purchases don't have foreign keys referencing them)
    renumber_ids('purchases', protect_ids=[])


__all__ = [
    'get_purchases', 'save_purchase', 'update_purchase', 'delete_purchase',
]
