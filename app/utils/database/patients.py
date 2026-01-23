"""
Patient Repository Module
Patient management functions
"""

from datetime import datetime
from typing import List, Dict

from .base import load_data, save_data, generate_id, renumber_ids, cascade_update_patient_references
from .consumption import get_consumption


def get_patients() -> List[Dict]:
    """Get all patients"""
    return load_data('patients')


def save_patient(patient_data: Dict) -> str:
    """Save new patient"""
    patients = get_patients()
    patient_id = generate_id('patients')
    patient_data['id'] = patient_id
    patient_data['created_at'] = datetime.now().isoformat()
    patients.append(patient_data)
    save_data('patients', patients)
    return patient_id


def update_patient(patient_id: str, patient_data: Dict):
    """Update existing patient"""
    patients = get_patients()
    for i, patient in enumerate(patients):
        if patient['id'] == patient_id:
            patient_data['id'] = patient_id
            patient_data['updated_at'] = datetime.now().isoformat()
            patients[i] = {**patient, **patient_data}
            break
    save_data('patients', patients)


def delete_patient(patient_id: str, skip_renumber: bool = False, cascade_delete: bool = True):
    """Delete patient and optionally renumber remaining records

    Args:
        patient_id: ID of the patient to delete
        skip_renumber: If True, skip renumbering (used in bulk operations)
        cascade_delete: If True, delete associated consumption records first (default: True)
    """
    # Step 1: Delete associated consumption records if cascade_delete is enabled
    if cascade_delete:
        consumption_records = get_consumption()
        # Filter out consumption records for this patient
        updated_consumption = [
            record for record in consumption_records
            if record.get('patient_id') != patient_id
        ]
        # Save updated consumption data
        if len(updated_consumption) < len(consumption_records):
            save_data('consumption', updated_consumption)

    # Step 2: Delete the patient record
    patients = get_patients()
    patients = [p for p in patients if p['id'] != patient_id]
    save_data('patients', patients)

    # Step 3: Renumber patients and cascade update all references (unless skipped for bulk operations)
    if not skip_renumber:
        id_mapping = renumber_ids('patients', protect_ids=[])
        cascade_update_patient_references(id_mapping)


__all__ = [
    'get_patients', 'save_patient', 'update_patient', 'delete_patient',
]
