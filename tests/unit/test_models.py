"""
Unit tests for data models
"""

import pytest
from datetime import datetime

# Mark all tests in this module as unit tests
pytestmark = pytest.mark.unit


class TestUserModel:
    """Test suite for User model"""

    def test_user_creation(self):
        """Test creating a User instance"""
        from app.utils.models.user import User

        user = User(
            id='01',
            username='admin',
            password='hashed_password',
            role='admin',
            name='Admin User',
            email='admin@example.com'
        )

        assert user.id == '01'
        assert user.username == 'admin'
        assert user.password == 'hashed_password'
        assert user.role == 'admin'
        assert user.name == 'Admin User'
        assert user.email == 'admin@example.com'
        assert user.department_id is None
        assert user.failed_login_attempts == 0
        assert user.account_locked is False
        assert user.password_changed_at is None
        assert user.must_change_password is False
        assert user.created_at is not None
        assert user.updated_at is None

    def test_user_creation_with_optional_fields(self):
        """Test creating a User instance with optional fields"""
        from app.utils.models.user import User

        user = User(
            id='02',
            username='pharmacy',
            password='hashed_password',
            role='department_user',
            name='Pharmacy User',
            email='pharmacy@example.com',
            department_id='01',
            failed_login_attempts=2,
            account_locked=True,
            password_changed_at='2023-01-01T00:00:00',
            must_change_password=True,
            created_at='2023-01-01T00:00:00',
            updated_at='2023-01-02T00:00:00'
        )

        assert user.id == '02'
        assert user.department_id == '01'
        assert user.failed_login_attempts == 2
        assert user.account_locked is True
        assert user.password_changed_at == '2023-01-01T00:00:00'
        assert user.must_change_password is True
        assert user.created_at == '2023-01-01T00:00:00'
        assert user.updated_at == '2023-01-02T00:00:00'

    def test_user_to_dict(self):
        """Test User to_dict method"""
        from app.utils.models.user import User

        user = User(
            id='01',
            username='admin',
            password='hashed_password',
            role='admin',
            name='Admin User',
            email='admin@example.com',
            department_id='01'
        )

        user_dict = user.to_dict()

        assert isinstance(user_dict, dict)
        assert user_dict['id'] == '01'
        assert user_dict['username'] == 'admin'
        assert user_dict['password'] == 'hashed_password'
        assert user_dict['role'] == 'admin'
        assert user_dict['name'] == 'Admin User'
        assert user_dict['email'] == 'admin@example.com'
        assert user_dict['department_id'] == '01'
        assert 'created_at' in user_dict

    def test_user_from_dict(self):
        """Test creating User from dictionary"""
        from app.utils.models.user import User

        user_data = {
            'id': '03',
            'username': 'testuser',
            'password': 'hashed_password',
            'role': 'department_user',
            'name': 'Test User',
            'email': 'test@example.com',
            'department_id': '01'
        }

        user = User.from_dict(user_data)

        assert user.id == '03'
        assert user.username == 'testuser'
        assert user.password == 'hashed_password'
        assert user.role == 'department_user'
        assert user.name == 'Test User'
        assert user.email == 'test@example.com'
        assert user.department_id == '01'

    def test_user_to_dict_from_dict_roundtrip(self):
        """Test round-trip conversion: User -> dict -> User"""
        from app.utils.models.user import User

        original_user = User(
            id='04',
            username='roundtrip',
            password='hashed_password',
            role='admin',
            name='Round Trip User',
            email='roundtrip@example.com',
            department_id='01',
            failed_login_attempts=1,
            must_change_password=True
        )

        # Convert to dict and back
        user_dict = original_user.to_dict()
        reconstructed_user = User.from_dict(user_dict)

        # Verify all fields match
        assert reconstructed_user.id == original_user.id
        assert reconstructed_user.username == original_user.username
        assert reconstructed_user.password == original_user.password
        assert reconstructed_user.role == original_user.role
        assert reconstructed_user.name == original_user.name
        assert reconstructed_user.email == original_user.email
        assert reconstructed_user.department_id == original_user.department_id
        assert reconstructed_user.failed_login_attempts == original_user.failed_login_attempts
        assert reconstructed_user.account_locked == original_user.account_locked
        assert reconstructed_user.password_changed_at == original_user.password_changed_at
        assert reconstructed_user.must_change_password == original_user.must_change_password


class TestMedicineModel:
    """Test suite for Medicine model"""

    def test_medicine_creation(self):
        """Test creating a Medicine instance"""
        from app.utils.models.medicine import Medicine

        medicine = Medicine(
            id='01',
            name='Aspirin',
            generic_name='Acetylsalicylic Acid',
            category='Pain Reliever',
            supplier_id='01',
            purchase_price=5.00,
            selling_price=7.50,
            unit_of_measure='tablet',
            low_stock_limit=100,
            description='Pain reliever and fever reducer'
        )

        assert medicine.id == '01'
        assert medicine.name == 'Aspirin'
        assert medicine.generic_name == 'Acetylsalicylic Acid'
        assert medicine.category == 'Pain Reliever'
        assert medicine.supplier_id == '01'
        assert medicine.purchase_price == 5.00
        assert medicine.selling_price == 7.50
        assert medicine.unit_of_measure == 'tablet'
        assert medicine.low_stock_limit == 100
        assert medicine.description == 'Pain reliever and fever reducer'

    def test_medicine_to_dict(self):
        """Test Medicine to_dict method"""
        from app.utils.models.medicine import Medicine

        medicine = Medicine(
            id='02',
            name='Ibuprofen',
            generic_name='Ibuprofen',
            category='NSAID',
            supplier_id='01',
            purchase_price=3.00,
            selling_price=5.00,
            unit_of_measure='tablet',
            low_stock_limit=50
        )

        medicine_dict = medicine.to_dict()

        assert isinstance(medicine_dict, dict)
        assert medicine_dict['id'] == '02'
        assert medicine_dict['name'] == 'Ibuprofen'
        assert medicine_dict['category'] == 'NSAID'
        assert medicine_dict['purchase_price'] == 3.00
        assert medicine_dict['selling_price'] == 5.00

    def test_medicine_from_dict(self):
        """Test creating Medicine from dictionary"""
        from app.utils.models.medicine import Medicine

        medicine_data = {
            'id': '03',
            name='Paracetamol',
            'generic_name': 'Paracetamol',
            'category': 'Pain Reliever',
            'supplier_id': '02',
            'purchase_price': 2.00,
            'selling_price': 3.50,
            'unit_of_measure': 'tablet',
            'low_stock_limit': 75
        }

        medicine = Medicine.from_dict(medicine_data)

        assert medicine.id == '03'
        assert medicine.name == 'Paracetamol'
        assert medicine.purchase_price == 2.00
        assert medicine.low_stock_limit == 75


class TestPatientModel:
    """Test suite for Patient model"""

    def test_patient_creation(self):
        """Test creating a Patient instance"""
        from app.utils.models.patient import Patient

        patient = Patient(
            id='01',
            first_name='John',
            last_name='Doe',
            date_of_birth='1990-01-01',
            gender='Male',
            phone='+1234567890',
            email='john.doe@example.com',
            address='123 Main St',
            emergency_contact='Jane Doe',
            emergency_phone='+1234567891',
            medical_history='No known allergies'
        )

        assert patient.id == '01'
        assert patient.first_name == 'John'
        assert patient.last_name == 'Doe'
        assert patient.date_of_birth == '1990-01-01'
        assert patient.gender == 'Male'
        assert patient.phone == '+1234567890'
        assert patient.email == 'john.doe@example.com'
        assert patient.address == '123 Main St'
        assert patient.emergency_contact == 'Jane Doe'
        assert patient.emergency_phone == '+1234567891'
        assert patient.medical_history == 'No known allergies'

    def test_patient_to_dict(self):
        """Test Patient to_dict method"""
        from app.utils.models.patient import Patient

        patient = Patient(
            id='02',
            first_name='Jane',
            last_name='Smith',
            date_of_birth='1985-05-15',
            gender='Female'
        )

        patient_dict = patient.to_dict()

        assert isinstance(patient_dict, dict)
        assert patient_dict['id'] == '02'
        assert patient_dict['first_name'] == 'Jane'
        assert patient_dict['last_name'] == 'Smith'
        assert patient_dict['date_of_birth'] == '1985-05-15'

    def test_patient_from_dict(self):
        """Test creating Patient from dictionary"""
        from app.utils.models.patient import Patient

        patient_data = {
            'id': '03',
            'first_name': 'Bob',
            'last_name': 'Johnson',
            'date_of_birth': '1975-12-31',
            'gender': 'Male',
            'phone': '+9876543210',
            'email': 'bob@example.com'
        }

        patient = Patient.from_dict(patient_data)

        assert patient.id == '03'
        assert patient.first_name == 'Bob'
        assert patient.last_name == 'Johnson'
        assert patient.email == 'bob@example.com'


class TestSupplierModel:
    """Test suite for Supplier model"""

    def test_supplier_creation(self):
        """Test creating a Supplier instance"""
        from app.utils.models.supplier import Supplier

        supplier = Supplier(
            id='01',
            name='PharmaCorp',
            contact_person='John Smith',
            phone='+1234567890',
            email='contact@pharmacorp.com',
            address='456 Pharma St',
            notes='Reliable supplier'
        )

        assert supplier.id == '01'
        assert supplier.name == 'PharmaCorp'
        assert supplier.contact_person == 'John Smith'
        assert supplier.phone == '+1234567890'
        assert supplier.email == 'contact@pharmacorp.com'
        assert supplier.address == '456 Pharma St'
        assert supplier.notes == 'Reliable supplier'

    def test_supplier_to_dict(self):
        """Test Supplier to_dict method"""
        from app.utils.models.supplier import Supplier

        supplier = Supplier(
            id='02',
            name='MediSupply Inc',
            contact_person='Jane Doe'
        )

        supplier_dict = supplier.to_dict()

        assert isinstance(supplier_dict, dict)
        assert supplier_dict['id'] == '02'
        assert supplier_dict['name'] == 'MediSupply Inc'
        assert supplier_dict['contact_person'] == 'Jane Doe'

    def test_supplier_from_dict(self):
        """Test creating Supplier from dictionary"""
        from app.utils.models.supplier import Supplier

        supplier_data = {
            'id': '03',
            'name': 'HealthDistributors',
            'contact_person': 'Bob Wilson',
            'phone': '+5555555555',
            'email': 'info@healthdist.com'
        }

        supplier = Supplier.from_dict(supplier_data)

        assert supplier.id == '03'
        assert supplier.name == 'HealthDistributors'
        assert supplier.contact_person == 'Bob Wilson'


class TestDepartmentModel:
    """Test suite for Department model"""

    def test_department_creation(self):
        """Test creating a Department instance"""
        from app.utils.models.department import Department

        department = Department(
            id='01',
            name='Main Pharmacy',
            description='Main hospital pharmacy',
            responsible_person='Dr. Smith',
            telephone='+1234567890',
            notes='Primary pharmacy location'
        )

        assert department.id == '01'
        assert department.name == 'Main Pharmacy'
        assert department.description == 'Main hospital pharmacy'
        assert department.responsible_person == 'Dr. Smith'
        assert department.telephone == '+1234567890'
        assert department.notes == 'Primary pharmacy location'

    def test_department_to_dict(self):
        """Test Department to_dict method"""
        from app.utils.models.department import Department

        department = Department(
            id='02',
            name='Emergency Pharmacy',
            description='24/7 emergency pharmacy'
        )

        department_dict = department.to_dict()

        assert isinstance(department_dict, dict)
        assert department_dict['id'] == '02'
        assert department_dict['name'] == 'Emergency Pharmacy'
        assert department_dict['description'] == '24/7 emergency pharmacy'

    def test_department_from_dict(self):
        """Test creating Department from dictionary"""
        from app.utils.models.department import Department

        department_data = {
            'id': '03',
            'name': 'Outpatient Pharmacy',
            'description': 'Outpatient services pharmacy',
            'responsible_person': 'Dr. Johnson',
            'telephone': '+9876543210'
        }

        department = Department.from_dict(department_data)

        assert department.id == '03'
        assert department.name == 'Outpatient Pharmacy'
        assert department.responsible_person == 'Dr. Johnson'


class TestStoreModel:
    """Test suite for Store model"""

    def test_store_creation(self):
        """Test creating a Store instance"""
        from app.utils.models.store import Store

        store = Store(
            id='01',
            name='Main Pharmacy Store',
            department_id='01',
            location='Main Building, Ground Floor',
            description='Primary pharmacy inventory'
        )

        assert store.id == '01'
        assert store.name == 'Main Pharmacy Store'
        assert store.department_id == '01'
        assert store.location == 'Main Building, Ground Floor'
        assert store.description == 'Primary pharmacy inventory'
        assert store.inventory == {}

    def test_store_with_inventory(self):
        """Test creating a Store with inventory"""
        from app.utils.models.store import Store

        store = Store(
            id='02',
            name='Emergency Store',
            department_id='02',
            location='Emergency Wing',
            inventory={'01': 100, '02': 50}
        )

        assert store.id == '02'
        assert store.inventory == {'01': 100, '02': 50}

    def test_store_to_dict(self):
        """Test Store to_dict method"""
        from app.utils.models.store import Store

        store = Store(
            id='03',
            name='Satellite Store',
            department_id='01',
            inventory={'01': 25}
        )

        store_dict = store.to_dict()

        assert isinstance(store_dict, dict)
        assert store_dict['id'] == '03'
        assert store_dict['name'] == 'Satellite Store'
        assert store_dict['inventory'] == {'01': 25}

    def test_store_from_dict(self):
        """Test creating Store from dictionary"""
        from app.utils.models.store import Store

        store_data = {
            'id': '04',
            'name': 'ICU Pharmacy',
            'department_id': '03',
            'location': 'ICU Floor 2',
            'inventory': {}
        }

        store = Store.from_dict(store_data)

        assert store.id == '04'
        assert store.name == 'ICU Pharmacy'
        assert store.location == 'ICU Floor 2'


class TestPurchaseModel:
    """Test suite for Purchase model"""

    def test_purchase_creation(self):
        """Test creating a Purchase instance"""
        from app.utils.models.purchase import Purchase

        purchase = Purchase(
            id='01',
            supplier_id='01',
            purchase_date='2023-01-01',
            total_amount=1000.00,
            status='pending',
            invoice_number='INV-001',
            notes='Monthly purchase'
        )

        assert purchase.id == '01'
        assert purchase.supplier_id == '01'
        assert purchase.purchase_date == '2023-01-01'
        assert purchase.total_amount == 1000.00
        assert purchase.status == 'pending'
        assert purchase.invoice_number == 'INV-001'
        assert purchase.notes == 'Monthly purchase'

    def test_purchase_to_dict(self):
        """Test Purchase to_dict method"""
        from app.utils.models.purchase import Purchase

        purchase = Purchase(
            id='02',
            supplier_id='02',
            purchase_date='2023-01-15',
            total_amount=500.00,
            status='delivered'
        )

        purchase_dict = purchase.to_dict()

        assert isinstance(purchase_dict, dict)
        assert purchase_dict['id'] == '02'
        assert purchase_dict['total_amount'] == 500.00
        assert purchase_dict['status'] == 'delivered'

    def test_purchase_from_dict(self):
        """Test creating Purchase from dictionary"""
        from app.utils.models.purchase import Purchase

        purchase_data = {
            'id': '03',
            'supplier_id': '01',
            'purchase_date': '2023-02-01',
            'total_amount': 750.00,
            'status': 'pending',
            'invoice_number': 'INV-003'
        }

        purchase = Purchase.from_dict(purchase_data)

        assert purchase.id == '03'
        assert purchase.total_amount == 750.00
        assert purchase.invoice_number == 'INV-003'


class TestConsumptionModel:
    """Test suite for Consumption model"""

    def test_consumption_creation(self):
        """Test creating a Consumption instance"""
        from app.utils.models.consumption import Consumption

        consumption = Consumption(
            id='01',
            patient_id='01',
            department_id='01',
            consumption_date='2023-01-01',
            total_amount=50.00,
            prescriber='Dr. Smith',
            diagnosis='Headache'
        )

        assert consumption.id == '01'
        assert consumption.patient_id == '01'
        assert consumption.department_id == '01'
        assert consumption.consumption_date == '2023-01-01'
        assert consumption.total_amount == 50.00
        assert consumption.prescriber == 'Dr. Smith'
        assert consumption.diagnosis == 'Headache'

    def test_consumption_to_dict(self):
        """Test Consumption to_dict method"""
        from app.utils.models.consumption import Consumption

        consumption = Consumption(
            id='02',
            patient_id='02',
            department_id='01',
            consumption_date='2023-01-15',
            total_amount=25.00
        )

        consumption_dict = consumption.to_dict()

        assert isinstance(consumption_dict, dict)
        assert consumption_dict['id'] == '02'
        assert consumption_dict['patient_id'] == '02'
        assert consumption_dict['total_amount'] == 25.00

    def test_consumption_from_dict(self):
        """Test creating Consumption from dictionary"""
        from app.utils.models.consumption import Consumption

        consumption_data = {
            'id': '03',
            'patient_id': '03',
            'department_id': '02',
            'consumption_date': '2023-02-01',
            'total_amount': 100.00,
            'prescriber': 'Dr. Johnson',
            'diagnosis': 'Fever'
        }

        consumption = Consumption.from_dict(consumption_data)

        assert consumption.id == '03'
        assert consumption.prescriber == 'Dr. Johnson'
        assert consumption.diagnosis == 'Fever'


class TestTransferModel:
    """Test suite for Transfer model"""

    def test_transfer_creation(self):
        """Test creating a Transfer instance"""
        from app.utils.models.transfer import Transfer

        transfer = Transfer(
            id='01',
            source_store_id='01',
            destination_store_id='02',
            transfer_date='2023-01-01',
            status='pending',
            requested_by='User01',
            approved_by='User02',
            notes='Emergency transfer'
        )

        assert transfer.id == '01'
        assert transfer.source_store_id == '01'
        assert transfer.destination_store_id == '02'
        assert transfer.transfer_date == '2023-01-01'
        assert transfer.status == 'pending'
        assert transfer.requested_by == 'User01'
        assert transfer.approved_by == 'User02'
        assert transfer.notes == 'Emergency transfer'

    def test_transfer_to_dict(self):
        """Test Transfer to_dict method"""
        from app.utils.models.transfer import Transfer

        transfer = Transfer(
            id='02',
            source_store_id='02',
            destination_store_id='03',
            transfer_date='2023-01-15',
            status='completed'
        )

        transfer_dict = transfer.to_dict()

        assert isinstance(transfer_dict, dict)
        assert transfer_dict['id'] == '02'
        assert transfer_dict['source_store_id'] == '02'
        assert transfer_dict['status'] == 'completed'

    def test_transfer_from_dict(self):
        """Test creating Transfer from dictionary"""
        from app.utils.models.transfer import Transfer

        transfer_data = {
            'id': '03',
            'source_store_id': '01',
            'destination_store_id': '03',
            'transfer_date': '2023-02-01',
            'status': 'pending',
            'requested_by': 'User03'
        }

        transfer = Transfer.from_dict(transfer_data)

        assert transfer.id == '03'
        assert transfer.source_store_id == '01'
        assert transfer.requested_by == 'User03'
