"""
Consumption Repository Module
Consumption management functions
"""

from datetime import datetime
from typing import List, Dict

from .base import load_data, save_data, generate_id, renumber_ids
from .medicines import get_medicines


def get_consumption() -> List[Dict]:
    """Get all consumption records"""
    return load_data('consumption')


def save_consumption(consumption_data: Dict) -> str:
    """Save new consumption and update inventory"""
    consumption = get_consumption()
    consumption_id = generate_id('consumption')
    consumption_data['id'] = consumption_id
    consumption_data['created_at'] = datetime.now().isoformat()
    consumption.append(consumption_data)
    save_data('consumption', consumption)

    # Update store inventory (deduct)
    department_id = consumption_data.get('department_id')
    update_store_inventory(department_id, consumption_data['medicines'], 'subtract')

    return consumption_id


def update_consumption(consumption_id: str, consumption_data: Dict):
    """Update existing consumption"""
    consumption = get_consumption()
    for i, record in enumerate(consumption):
        if record['id'] == consumption_id:
            consumption_data['id'] = consumption_id
            consumption_data['updated_at'] = datetime.now().isoformat()
            consumption[i] = {**record, **consumption_data}
            break
    save_data('consumption', consumption)


def delete_consumption(consumption_id: str):
    """Delete consumption and renumber remaining records"""
    consumption = get_consumption()
    consumption = [c for c in consumption if c['id'] != consumption_id]
    save_data('consumption', consumption)

    # Renumber consumption (no cascade needed - consumption doesn't have foreign keys referencing it)
    renumber_ids('consumption', protect_ids=[])


def update_store_inventory(department_id: str, medicines: list, operation: str):
    """Update specific store inventory"""
    from .stores import get_stores
    stores = get_stores()
    store = next((s for s in stores if s['department_id'] == department_id), None)

    if store:
        for medicine in medicines:
            medicine_id = medicine['medicine_id']
            quantity = medicine['quantity']

            current_stock = store['inventory'].get(medicine_id, 0)

            if operation == 'add':
                store['inventory'][medicine_id] = current_stock + quantity
            elif operation == 'subtract':
                store['inventory'][medicine_id] = max(0, current_stock - quantity)

        save_data('stores', stores)


def get_medicine_stock(medicine_id: str, department_id: str = None) -> int:
    """Get current stock for a medicine in a specific store or all stores"""
    from .stores import get_stores
    stores = get_stores()

    if department_id:
        # Get stock for specific department store
        store = next((s for s in stores if s.get('department_id') == department_id), None)
        if store:
            return store.get('inventory', {}).get(medicine_id, 0)
        return 0
    else:
        # Get total stock across all stores
        total_stock = 0
        for store in stores:
            total_stock += store.get('inventory', {}).get(medicine_id, 0)
        return total_stock


def get_low_stock_medicines(department_id: str = None) -> List[Dict]:
    """Get medicines that are at or below low stock limit"""
    from .stores import get_stores
    medicines = get_medicines()
    stores = get_stores()
    low_stock_medicines = []

    for medicine in medicines:
        current_stock = get_medicine_stock(medicine['id'], department_id)
        if current_stock <= medicine.get('low_stock_limit', 0):
            low_stock_medicines.append({
                'medicine': medicine,
                'current_stock': current_stock,
                'low_stock_limit': medicine.get('low_stock_limit', 0)
            })

    return low_stock_medicines


def get_stock_status(medicine_id: str, department_id: str = None) -> Dict:
    """Get stock status for a medicine"""
    medicines = get_medicines()
    medicine = next((m for m in medicines if m['id'] == medicine_id), None)

    if not medicine:
        return {'status': 'unknown', 'color': 'secondary', 'message': 'Medicine not found'}

    current_stock = get_medicine_stock(medicine_id, department_id)
    low_limit = medicine.get('low_stock_limit', 0)

    if current_stock <= low_limit:
        return {'status': 'low', 'color': 'danger', 'message': 'Low Stock'}
    elif current_stock <= low_limit * 1.5:
        return {'status': 'medium', 'color': 'warning', 'message': 'Medium Stock'}
    else:
        return {'status': 'good', 'color': 'success', 'message': 'Good Stock'}


def validate_consumption_stock(medicines: list, department_id: str) -> Dict:
    """Validate if consumption is possible with current stock"""
    validation_result = {'valid': True, 'errors': []}

    for medicine_item in medicines:
        medicine_id = medicine_item['medicine_id']
        requested_qty = medicine_item['quantity']
        available_stock = get_medicine_stock(medicine_id, department_id)

        if requested_qty > available_stock:
            medicines_list = get_medicines()
            medicine = next((m for m in medicines_list if m['id'] == medicine_id), None)
            medicine_name = medicine['name'] if medicine else f'Medicine ID {medicine_id}'

            validation_result['valid'] = False
            validation_result['errors'].append(
                f'{medicine_name}: Requested {requested_qty}, but only {available_stock} available'
            )

    return validation_result


def get_available_medicines_for_consumption(department_id: str = None) -> List[Dict]:
    """Get medicines available for consumption with stock > 0"""
    medicines = get_medicines()
    available_medicines = []

    for medicine in medicines:
        stock = get_medicine_stock(medicine['id'], department_id)
        if stock > 0:
            medicine_with_stock = medicine.copy()
            medicine_with_stock['available_stock'] = stock
            available_medicines.append(medicine_with_stock)

    return available_medicines


__all__ = [
    'get_consumption', 'save_consumption', 'update_consumption', 'delete_consumption',
    'get_medicine_stock', 'update_store_inventory', 'get_low_stock_medicines',
    'get_available_medicines_for_consumption', 'validate_consumption_stock',
    'get_stock_status',
]
