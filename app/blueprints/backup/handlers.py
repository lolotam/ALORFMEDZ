"""
Backup Handlers

CSV export handlers for backup functionality.
"""

import os
import csv
from app.utils.database import (
    get_medicines, get_patients, get_suppliers, get_departments,
    get_stores, get_purchases, get_consumption, get_history, get_users, load_data
)


def export_all_data_to_csv(output_dir):
    """Export all data to CSV files and return list of created files"""
    csv_files = []

    try:
        # Export medicines
        medicines = get_medicines()
        if medicines:
            csv_path = os.path.join(output_dir, 'medicines.csv')
            export_medicines_to_csv(medicines, csv_path)
            csv_files.append(csv_path)

        # Export patients
        patients = get_patients()
        if patients:
            csv_path = os.path.join(output_dir, 'patients.csv')
            export_patients_to_csv(patients, csv_path)
            csv_files.append(csv_path)

        # Export suppliers
        suppliers = get_suppliers()
        if suppliers:
            csv_path = os.path.join(output_dir, 'suppliers.csv')
            export_suppliers_to_csv(suppliers, csv_path)
            csv_files.append(csv_path)

        # Export departments
        departments = get_departments()
        if departments:
            csv_path = os.path.join(output_dir, 'departments.csv')
            export_departments_to_csv(departments, csv_path)
            csv_files.append(csv_path)

        # Export doctors
        try:
            doctors = load_data('doctors')
            if doctors:
                csv_path = os.path.join(output_dir, 'doctors.csv')
                export_doctors_to_csv(doctors, csv_path)
                csv_files.append(csv_path)
        except:
            pass  # Doctors might not exist yet

        # Export stores
        stores = get_stores()
        if stores:
            csv_path = os.path.join(output_dir, 'stores.csv')
            export_stores_to_csv(stores, csv_path)
            csv_files.append(csv_path)

        # Export purchases
        purchases = get_purchases()
        if purchases:
            csv_path = os.path.join(output_dir, 'purchases.csv')
            export_purchases_to_csv(purchases, csv_path)
            csv_files.append(csv_path)

        # Export consumption
        consumption = get_consumption()
        if consumption:
            csv_path = os.path.join(output_dir, 'consumption.csv')
            export_consumption_to_csv(consumption, csv_path)
            csv_files.append(csv_path)

        # Export transfers
        try:
            transfers = load_data('transfers')
            if transfers:
                csv_path = os.path.join(output_dir, 'transfers.csv')
                export_transfers_to_csv(transfers, csv_path)
                csv_files.append(csv_path)
        except:
            pass

        # Export users (without passwords)
        users = get_users()
        if users:
            csv_path = os.path.join(output_dir, 'users.csv')
            export_users_to_csv(users, csv_path)
            csv_files.append(csv_path)

        # Export history
        history = get_history(limit=5000)
        if history:
            csv_path = os.path.join(output_dir, 'history.csv')
            export_history_to_csv(history, csv_path)
            csv_files.append(csv_path)

    except Exception as e:
        print(f"Error exporting CSV files: {str(e)}")

    return csv_files


def export_medicines_to_csv(medicines, csv_path):
    """Export medicines to CSV"""
    fieldnames = ['id', 'name', 'supplier_id', 'category', 'form_dosage', 'strength',
                 'low_stock_limit', 'unit_price', 'notes', 'created_at']

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for record in medicines:
            filtered_record = {k: v for k, v in record.items() if k in fieldnames}
            writer.writerow(filtered_record)


def export_patients_to_csv(patients, csv_path):
    """Export patients to CSV"""
    fieldnames = ['id', 'name', 'age', 'gender', 'phone', 'address',
                 'medical_history', 'allergies', 'created_at']

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for record in patients:
            filtered_record = {k: v for k, v in record.items() if k in fieldnames}
            writer.writerow(filtered_record)


def export_suppliers_to_csv(suppliers, csv_path):
    """Export suppliers to CSV"""
    fieldnames = ['id', 'name', 'contact_person', 'phone', 'email',
                 'address', 'city', 'created_at']

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for record in suppliers:
            filtered_record = {k: v for k, v in record.items() if k in fieldnames}
            writer.writerow(filtered_record)


def export_departments_to_csv(departments, csv_path):
    """Export departments to CSV"""
    fieldnames = ['id', 'name', 'description', 'responsible_person',
                 'telephone', 'notes', 'created_at']

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for record in departments:
            filtered_record = {k: v for k, v in record.items() if k in fieldnames}
            writer.writerow(filtered_record)


def export_doctors_to_csv(doctors, csv_path):
    """Export doctors to CSV"""
    fieldnames = ['id', 'dr_name', 'gender', 'nationality', 'department_id', 'specialist',
                 'position', 'type', 'mobile_no', 'email', 'license_number', 'note',
                 'created_at', 'updated_at']

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for record in doctors:
            filtered_record = {k: v for k, v in record.items() if k in fieldnames}
            writer.writerow(filtered_record)


def export_stores_to_csv(stores, csv_path):
    """Export stores to CSV"""
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Store ID', 'Store Name', 'Department ID', 'Location',
                       'Description', 'Medicine ID', 'Medicine Stock', 'Created At'])

        for store in stores:
            inventory = store.get('inventory', {})
            if inventory:
                for med_id, stock in inventory.items():
                    writer.writerow([
                        store.get('id', ''),
                        store.get('name', ''),
                        store.get('department_id', ''),
                        store.get('location', ''),
                        store.get('description', ''),
                        med_id,
                        stock,
                        store.get('created_at', '')
                    ])
            else:
                writer.writerow([
                    store.get('id', ''),
                    store.get('name', ''),
                    store.get('department_id', ''),
                    store.get('location', ''),
                    store.get('description', ''),
                    '', '',
                    store.get('created_at', '')
                ])


def export_purchases_to_csv(purchases, csv_path):
    """Export purchases to CSV"""
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Purchase ID', 'Supplier ID', 'Invoice Number', 'Purchase Date',
                       'Medicine ID', 'Quantity', 'Status', 'Notes', 'Created At'])

        for purchase in purchases:
            medicines = purchase.get('medicines', [])
            if medicines:
                for med in medicines:
                    writer.writerow([
                        purchase.get('id', ''),
                        purchase.get('supplier_id', ''),
                        purchase.get('invoice_number', ''),
                        purchase.get('date', ''),
                        med.get('medicine_id', ''),
                        med.get('quantity', ''),
                        purchase.get('status', ''),
                        purchase.get('notes', ''),
                        purchase.get('created_at', '')
                    ])
            else:
                writer.writerow([
                    purchase.get('id', ''),
                    purchase.get('supplier_id', ''),
                    purchase.get('invoice_number', ''),
                    purchase.get('date', ''),
                    '', '',
                    purchase.get('status', ''),
                    purchase.get('notes', ''),
                    purchase.get('created_at', '')
                ])


def export_consumption_to_csv(consumption, csv_path):
    """Export consumption to CSV"""
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Consumption ID', 'Patient ID', 'Date', 'Medicine ID',
                       'Quantity', 'Prescribed By', 'Notes', 'Created At'])

        for consumption_record in consumption:
            medicines = consumption_record.get('medicines', [])
            if medicines:
                for med in medicines:
                    writer.writerow([
                        consumption_record.get('id', ''),
                        consumption_record.get('patient_id', ''),
                        consumption_record.get('date', ''),
                        med.get('medicine_id', ''),
                        med.get('quantity', ''),
                        consumption_record.get('prescribed_by', ''),
                        consumption_record.get('notes', ''),
                        consumption_record.get('created_at', '')
                    ])
            else:
                writer.writerow([
                    consumption_record.get('id', ''),
                    consumption_record.get('patient_id', ''),
                    consumption_record.get('date', ''),
                    '', '',
                    consumption_record.get('prescribed_by', ''),
                    consumption_record.get('notes', ''),
                    consumption_record.get('created_at', '')
                ])


def export_transfers_to_csv(transfers, csv_path):
    """Export transfers to CSV"""
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Transfer ID', 'Source Store ID', 'Destination Store ID',
                       'Medicine ID', 'Quantity', 'Transfer Date', 'Status',
                       'Notes', 'Created At'])

        for transfer in transfers:
            medicines = transfer.get('medicines', [])
            if medicines:
                for med in medicines:
                    writer.writerow([
                        transfer.get('id', ''),
                        transfer.get('source_store_id', ''),
                        transfer.get('destination_store_id', ''),
                        med.get('medicine_id', ''),
                        med.get('quantity', ''),
                        transfer.get('transfer_date', ''),
                        transfer.get('status', ''),
                        transfer.get('notes', ''),
                        transfer.get('created_at', '')
                    ])
            else:
                writer.writerow([
                    transfer.get('id', ''),
                    transfer.get('source_store_id', ''),
                    transfer.get('destination_store_id', ''),
                    '', '',
                    transfer.get('transfer_date', ''),
                    transfer.get('status', ''),
                    transfer.get('notes', ''),
                    transfer.get('created_at', '')
                ])


def export_users_to_csv(users, csv_path):
    """Export users to CSV (without passwords)"""
    fieldnames = ['id', 'username', 'role', 'name', 'email',
                 'department_id', 'created_at']

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for record in users:
            # Exclude password for security
            filtered_record = {k: v for k, v in record.items() if k in fieldnames}
            writer.writerow(filtered_record)


def export_history_to_csv(history, csv_path):
    """Export history to CSV"""
    import json
    fieldnames = ['id', 'action', 'entity_type', 'entity_id', 'user_id',
                 'username', 'timestamp', 'details']

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for record in history:
            # Convert details dict to string if needed
            record_copy = record.copy()
            if 'details' in record_copy and isinstance(record_copy['details'], dict):
                record_copy['details'] = json.dumps(record_copy['details'])
            filtered_record = {k: v for k, v in record_copy.items() if k in fieldnames}
            writer.writerow(filtered_record)
