"""
Unit tests for database repository modules
"""

import pytest
import json
import os

# Mark all tests in this module as unit tests
pytestmark = pytest.mark.unit


class TestUserRepository:
    """Test suite for User repository functions"""

    def test_get_users_empty(self, temp_dir):
        """Test getting users from empty file"""
        from app.utils.database.users import get_users

        # Temporarily override data directory
        import app.utils.database.base as base_module
        original_data_dir = base_module.DATA_DIR
        original_files = base_module.DB_FILES.copy()

        try:
            base_module.DATA_DIR = temp_dir
            test_file = os.path.join(temp_dir, 'users.json')
            with open(test_file, 'w') as f:
                json.dump([], f)
            base_module.DB_FILES['users'] = test_file

            users = get_users()
            assert users == []
        finally:
            base_module.DATA_DIR = original_data_dir
            base_module.DB_FILES = original_files

    def test_get_users_with_data(self, temp_dir):
        """Test getting users with data"""
        from app.utils.database.users import get_users

        import app.utils.database.base as base_module
        original_data_dir = base_module.DATA_DIR
        original_files = base_module.DB_FILES.copy()

        try:
            base_module.DATA_DIR = temp_dir
            test_file = os.path.join(temp_dir, 'users.json')
            test_data = [
                {'id': '01', 'username': 'admin', 'role': 'admin'},
                {'id': '02', 'username': 'pharmacy', 'role': 'department_user'}
            ]
            with open(test_file, 'w') as f:
                json.dump(test_data, f)
            base_module.DB_FILES['users'] = test_file

            users = get_users()
            assert len(users) == 2
            assert users[0]['username'] == 'admin'
            assert users[1]['username'] == 'pharmacy'
        finally:
            base_module.DATA_DIR = original_data_dir
            base_module.DB_FILES = original_files

    def test_get_user_by_id_found(self, temp_dir):
        """Test getting a specific user by ID"""
        from app.utils.database.users import get_user_by_id

        import app.utils.database.base as base_module
        original_data_dir = base_module.DATA_DIR
        original_files = base_module.DB_FILES.copy()

        try:
            base_module.DATA_DIR = temp_dir
            test_file = os.path.join(temp_dir, 'users.json')
            test_data = [
                {'id': '01', 'username': 'admin', 'role': 'admin'},
                {'id': '02', 'username': 'pharmacy', 'role': 'department_user'}
            ]
            with open(test_file, 'w') as f:
                json.dump(test_data, f)
            base_module.DB_FILES['users'] = test_file

            user = get_user_by_id('01')
            assert user is not None
            assert user['username'] == 'admin'
            assert user['role'] == 'admin'
        finally:
            base_module.DATA_DIR = original_data_dir
            base_module.DB_FILES = original_files

    def test_get_user_by_id_not_found(self, temp_dir):
        """Test getting a user that doesn't exist"""
        from app.utils.database.users import get_user_by_id

        import app.utils.database.base as base_module
        original_data_dir = base_module.DATA_DIR
        original_files = base_module.DB_FILES.copy()

        try:
            base_module.DATA_DIR = temp_dir
            test_file = os.path.join(temp_dir, 'users.json')
            test_data = [
                {'id': '01', 'username': 'admin', 'role': 'admin'}
            ]
            with open(test_file, 'w') as f:
                json.dump(test_data, f)
            base_module.DB_FILES['users'] = test_file

            user = get_user_by_id('99')
            assert user is None
        finally:
            base_module.DATA_DIR = original_data_dir
            base_module.DB_FILES = original_files

    def test_get_user_by_username_found(self, temp_dir):
        """Test getting a user by username"""
        from app.utils.database.users import get_user_by_username

        import app.utils.database.base as base_module
        original_data_dir = base_module.DATA_DIR
        original_files = base_module.DB_FILES.copy()

        try:
            base_module.DATA_DIR = temp_dir
            test_file = os.path.join(temp_dir, 'users.json')
            test_data = [
                {'id': '01', 'username': 'admin', 'role': 'admin'},
                {'id': '02', 'username': 'pharmacy', 'role': 'department_user'}
            ]
            with open(test_file, 'w') as f:
                json.dump(test_data, f)
            base_module.DB_FILES['users'] = test_file

            user = get_user_by_username('pharmacy')
            assert user is not None
            assert user['id'] == '02'
            assert user['role'] == 'department_user'
        finally:
            base_module.DATA_DIR = original_data_dir
            base_module.DB_FILES = original_files

    def test_create_user(self, temp_dir):
        """Test creating a new user"""
        from app.utils.database.users import create_user

        import app.utils.database.base as base_module
        original_data_dir = base_module.DATA_DIR
        original_files = base_module.DB_FILES.copy()

        try:
            base_module.DATA_DIR = temp_dir
            test_file = os.path.join(temp_dir, 'users.json')
            test_data = [
                {'id': '01', 'username': 'admin', 'role': 'admin'}
            ]
            with open(test_file, 'w') as f:
                json.dump(test_data, f)
            base_module.DB_FILES['users'] = test_file

            new_user_data = {
                'username': 'newuser',
                'password': 'password123',
                'role': 'department_user',
                'name': 'New User',
                'email': 'newuser@example.com'
            }

            user = create_user(new_user_data)
            assert user is not None
            assert user['username'] == 'newuser'
            assert user['role'] == 'department_user'

            # Verify it was saved
            with open(test_file, 'r') as f:
                users = json.load(f)
            assert len(users) == 2
            assert any(u['username'] == 'newuser' for u in users)
        finally:
            base_module.DATA_DIR = original_data_dir
            base_module.DB_FILES = original_files

    def test_update_user(self, temp_dir):
        """Test updating an existing user"""
        from app.utils.database.users import update_user

        import app.utils.database.base as base_module
        original_data_dir = base_module.DATA_DIR
        original_files = base_module.DB_FILES.copy()

        try:
            base_module.DATA_DIR = temp_dir
            test_file = os.path.join(temp_dir, 'users.json')
            test_data = [
                {'id': '01', 'username': 'admin', 'role': 'admin', 'email': 'old@example.com'}
            ]
            with open(test_file, 'w') as f:
                json.dump(test_data, f)
            base_module.DB_FILES['users'] = test_file

            updated_data = {
                'email': 'new@example.com',
                'name': 'Updated Admin'
            }

            user = update_user('01', updated_data)
            assert user is not None
            assert user['email'] == 'new@example.com'
            assert user['name'] == 'Updated Admin'

            # Verify it was saved
            with open(test_file, 'r') as f:
                users = json.load(f)
            updated_user = next(u for u in users if u['id'] == '01')
            assert updated_user['email'] == 'new@example.com'
        finally:
            base_module.DATA_DIR = original_data_dir
            base_module.DB_FILES = original_files

    def test_delete_user(self, temp_dir):
        """Test deleting a user"""
        from app.utils.database.users import delete_user

        import app.utils.database.base as base_module
        original_data_dir = base_module.DATA_DIR
        original_files = base_module.DB_FILES.copy()

        try:
            base_module.DATA_DIR = temp_dir
            test_file = os.path.join(temp_dir, 'users.json')
            test_data = [
                {'id': '01', 'username': 'admin', 'role': 'admin'},
                {'id': '02', 'username': 'pharmacy', 'role': 'department_user'}
            ]
            with open(test_file, 'w') as f:
                json.dump(test_data, f)
            base_module.DB_FILES['users'] = test_file

            result = delete_user('01')
            assert result is True

            # Verify it was deleted
            with open(test_file, 'r') as f:
                users = json.load(f)
            assert len(users) == 1
            assert users[0]['id'] == '02'
        finally:
            base_module.DATA_DIR = original_data_dir
            base_module.DB_FILES = original_files

    def test_delete_user_not_found(self, temp_dir):
        """Test deleting a user that doesn't exist"""
        from app.utils.database.users import delete_user

        import app.utils.database.base as base_module
        original_data_dir = base_module.DATA_DIR
        original_files = base_module.DB_FILES.copy()

        try:
            base_module.DATA_DIR = temp_dir
            test_file = os.path.join(temp_dir, 'users.json')
            test_data = [
                {'id': '01', 'username': 'admin', 'role': 'admin'}
            ]
            with open(test_file, 'w') as f:
                json.dump(test_data, f)
            base_module.DB_FILES['users'] = test_file

            result = delete_user('99')
            assert result is False

            # Verify no change
            with open(test_file, 'r') as f:
                users = json.load(f)
            assert len(users) == 1
        finally:
            base_module.DATA_DIR = original_data_dir
            base_module.DB_FILES = original_files


class TestMedicineRepository:
    """Test suite for Medicine repository functions"""

    def test_get_medicines_empty(self, temp_dir):
        """Test getting medicines from empty file"""
        from app.utils.database.medicines import get_medicines

        import app.utils.database.base as base_module
        original_data_dir = base_module.DATA_DIR
        original_files = base_module.DB_FILES.copy()

        try:
            base_module.DATA_DIR = temp_dir
            test_file = os.path.join(temp_dir, 'medicines.json')
            with open(test_file, 'w') as f:
                json.dump([], f)
            base_module.DB_FILES['medicines'] = test_file

            medicines = get_medicines()
            assert medicines == []
        finally:
            base_module.DATA_DIR = original_data_dir
            base_module.DB_FILES = original_files

    def test_get_medicine_by_id(self, temp_dir):
        """Test getting a specific medicine by ID"""
        from app.utils.database.medicines import get_medicine_by_id

        import app.utils.database.base as base_module
        original_data_dir = base_module.DATA_DIR
        original_files = base_module.DB_FILES.copy()

        try:
            base_module.DATA_DIR = temp_dir
            test_file = os.path.join(temp_dir, 'medicines.json')
            test_data = [
                {'id': '01', 'name': 'Aspirin', 'category': 'Pain Reliever'},
                {'id': '02', 'name': 'Ibuprofen', 'category': 'NSAID'}
            ]
            with open(test_file, 'w') as f:
                json.dump(test_data, f)
            base_module.DB_FILES['medicines'] = test_file

            medicine = get_medicine_by_id('02')
            assert medicine is not None
            assert medicine['name'] == 'Ibuprofen'
            assert medicine['category'] == 'NSAID'
        finally:
            base_module.DATA_DIR = original_data_dir
            base_module.DB_FILES = original_files

    def test_get_medicines_by_supplier(self, temp_dir):
        """Test getting medicines by supplier ID"""
        from app.utils.database.medicines import get_medicines_by_supplier

        import app.utils.database.base as base_module
        original_data_dir = base_module.DATA_DIR
        original_files = base_module.DB_FILES.copy()

        try:
            base_module.DATA_DIR = temp_dir
            test_file = os.path.join(temp_dir, 'medicines.json')
            test_data = [
                {'id': '01', 'name': 'Aspirin', 'supplier_id': '01'},
                {'id': '02', 'name': 'Ibuprofen', 'supplier_id': '01'},
                {'id': '03', 'name': 'Paracetamol', 'supplier_id': '02'}
            ]
            with open(test_file, 'w') as f:
                json.dump(test_data, f)
            base_module.DB_FILES['medicines'] = test_file

            medicines = get_medicines_by_supplier('01')
            assert len(medicines) == 2
            assert all(m['supplier_id'] == '01' for m in medicines)
        finally:
            base_module.DATA_DIR = original_data_dir
            base_module.DB_FILES = original_files

    def test_create_medicine(self, temp_dir):
        """Test creating a new medicine"""
        from app.utils.database.medicines import create_medicine

        import app.utils.database.base as base_module
        original_data_dir = base_module.DATA_DIR
        original_files = base_module.DB_FILES.copy()

        try:
            base_module.DATA_DIR = temp_dir
            test_file = os.path.join(temp_dir, 'medicines.json')
            test_data = [
                {'id': '01', 'name': 'Aspirin', 'category': 'Pain Reliever'}
            ]
            with open(test_file, 'w') as f:
                json.dump(test_data, f)
            base_module.DB_FILES['medicines'] = test_file

            new_medicine_data = {
                'name': 'Ibuprofen',
                'category': 'NSAID',
                'supplier_id': '01',
                'purchase_price': 5.00,
                'selling_price': 7.50
            }

            medicine = create_medicine(new_medicine_data)
            assert medicine is not None
            assert medicine['name'] == 'Ibuprofen'
            assert medicine['category'] == 'NSAID'
        finally:
            base_module.DATA_DIR = original_data_dir
            base_module.DB_FILES = original_files


class TestSupplierRepository:
    """Test suite for Supplier repository functions"""

    def test_get_suppliers(self, temp_dir):
        """Test getting all suppliers"""
        from app.utils.database.suppliers import get_suppliers

        import app.utils.database.base as base_module
        original_data_dir = base_module.DATA_DIR
        original_files = base_module.DB_FILES.copy()

        try:
            base_module.DATA_DIR = temp_dir
            test_file = os.path.join(temp_dir, 'suppliers.json')
            test_data = [
                {'id': '01', 'name': 'PharmaCorp'},
                {'id': '02', 'name': 'MediSupply'}
            ]
            with open(test_file, 'w') as f:
                json.dump(test_data, f)
            base_module.DB_FILES['suppliers'] = test_file

            suppliers = get_suppliers()
            assert len(suppliers) == 2
            assert suppliers[0]['name'] == 'PharmaCorp'
        finally:
            base_module.DATA_DIR = original_data_dir
            base_module.DB_FILES = original_files

    def test_get_supplier_by_id(self, temp_dir):
        """Test getting a specific supplier by ID"""
        from app.utils.database.suppliers import get_supplier_by_id

        import app.utils.database.base as base_module
        original_data_dir = base_module.DATA_DIR
        original_files = base_module.DB_FILES.copy()

        try:
            base_module.DATA_DIR = temp_dir
            test_file = os.path.join(temp_dir, 'suppliers.json')
            test_data = [
                {'id': '01', 'name': 'PharmaCorp', 'contact_person': 'John Doe'},
                {'id': '02', 'name': 'MediSupply', 'contact_person': 'Jane Smith'}
            ]
            with open(test_file, 'w') as f:
                json.dump(test_data, f)
            base_module.DB_FILES['suppliers'] = test_file

            supplier = get_supplier_by_id('02')
            assert supplier is not None
            assert supplier['name'] == 'MediSupply'
            assert supplier['contact_person'] == 'Jane Smith'
        finally:
            base_module.DATA_DIR = original_data_dir
            base_module.DB_FILES = original_files

    def test_create_supplier(self, temp_dir):
        """Test creating a new supplier"""
        from app.utils.database.suppliers import create_supplier

        import app.utils.database.base as base_module
        original_data_dir = base_module.DATA_DIR
        original_files = base_module.DB_FILES.copy()

        try:
            base_module.DATA_DIR = temp_dir
            test_file = os.path.join(temp_dir, 'suppliers.json')
            test_data = [
                {'id': '01', 'name': 'PharmaCorp'}
            ]
            with open(test_file, 'w') as f:
                json.dump(test_data, f)
            base_module.DB_FILES['suppliers'] = test_file

            new_supplier_data = {
                'name': 'HealthDist',
                'contact_person': 'Bob Johnson',
                'phone': '+1234567890',
                'email': 'contact@healthdist.com'
            }

            supplier = create_supplier(new_supplier_data)
            assert supplier is not None
            assert supplier['name'] == 'HealthDist'
            assert supplier['contact_person'] == 'Bob Johnson'
        finally:
            base_module.DATA_DIR = original_data_dir
            base_module.DB_FILES = original_files


class TestDepartmentRepository:
    """Test suite for Department repository functions"""

    def test_get_departments(self, temp_dir):
        """Test getting all departments"""
        from app.utils.database.departments import get_departments

        import app.utils.database.base as base_module
        original_data_dir = base_module.DATA_DIR
        original_files = base_module.DB_FILES.copy()

        try:
            base_module.DATA_DIR = temp_dir
            test_file = os.path.join(temp_dir, 'departments.json')
            test_data = [
                {'id': '01', 'name': 'Main Pharmacy'},
                {'id': '02', 'name': 'Emergency Pharmacy'}
            ]
            with open(test_file, 'w') as f:
                json.dump(test_data, f)
            base_module.DB_FILES['departments'] = test_file

            departments = get_departments()
            assert len(departments) == 2
            assert departments[0]['name'] == 'Main Pharmacy'
        finally:
            base_module.DATA_DIR = original_data_dir
            base_module.DB_FILES = original_files

    def test_get_department_by_id(self, temp_dir):
        """Test getting a specific department by ID"""
        from app.utils.database.departments import get_department_by_id

        import app.utils.database.base as base_module
        original_data_dir = base_module.DATA_DIR
        original_files = base_module.DB_FILES.copy()

        try:
            base_module.DATA_DIR = temp_dir
            test_file = os.path.join(temp_dir, 'departments.json')
            test_data = [
                {'id': '01', 'name': 'Main Pharmacy', 'responsible_person': 'Dr. Smith'},
                {'id': '02', 'name': 'Emergency Pharmacy', 'responsible_person': 'Dr. Jones'}
            ]
            with open(test_file, 'w') as f:
                json.dump(test_data, f)
            base_module.DB_FILES['departments'] = test_file

            department = get_department_by_id('02')
            assert department is not None
            assert department['name'] == 'Emergency Pharmacy'
            assert department['responsible_person'] == 'Dr. Jones'
        finally:
            base_module.DATA_DIR = original_data_dir
            base_module.DB_FILES = original_files


class TestStoreRepository:
    """Test suite for Store repository functions"""

    def test_get_stores(self, temp_dir):
        """Test getting all stores"""
        from app.utils.database.stores import get_stores

        import app.utils.database.base as base_module
        original_data_dir = base_module.DATA_DIR
        original_files = base_module.DB_FILES.copy()

        try:
            base_module.DATA_DIR = temp_dir
            test_file = os.path.join(temp_dir, 'stores.json')
            test_data = [
                {'id': '01', 'name': 'Main Store', 'department_id': '01'},
                {'id': '02', 'name': 'Emergency Store', 'department_id': '02'}
            ]
            with open(test_file, 'w') as f:
                json.dump(test_data, f)
            base_module.DB_FILES['stores'] = test_file

            stores = get_stores()
            assert len(stores) == 2
            assert stores[0]['name'] == 'Main Store'
        finally:
            base_module.DATA_DIR = original_data_dir
            base_module.DB_FILES = original_files

    def test_get_store_by_id(self, temp_dir):
        """Test getting a specific store by ID"""
        from app.utils.database.stores import get_store_by_id

        import app.utils.database.base as base_module
        original_data_dir = base_module.DATA_DIR
        original_files = base_module.DB_FILES.copy()

        try:
            base_module.DATA_DIR = temp_dir
            test_file = os.path.join(temp_dir, 'stores.json')
            test_data = [
                {'id': '01', 'name': 'Main Store', 'department_id': '01'},
                {'id': '02', 'name': 'Emergency Store', 'department_id': '02'}
            ]
            with open(test_file, 'w') as f:
                json.dump(test_data, f)
            base_module.DB_FILES['stores'] = test_file

            store = get_store_by_id('02')
            assert store is not None
            assert store['name'] == 'Emergency Store'
            assert store['department_id'] == '02'
        finally:
            base_module.DATA_DIR = original_data_dir
            base_module.DB_FILES = original_files

    def test_get_stores_by_department(self, temp_dir):
        """Test getting stores by department ID"""
        from app.utils.database.stores import get_stores_by_department

        import app.utils.database.base as base_module
        original_data_dir = base_module.DATA_DIR
        original_files = base_module.DB_FILES.copy()

        try:
            base_module.DATA_DIR = temp_dir
            test_file = os.path.join(temp_dir, 'stores.json')
            test_data = [
                {'id': '01', 'name': 'Main Store', 'department_id': '01'},
                {'id': '02', 'name': 'Emergency Store', 'department_id': '01'},
                {'id': '03', 'name': 'ICU Store', 'department_id': '02'}
            ]
            with open(test_file, 'w') as f:
                json.dump(test_data, f)
            base_module.DB_FILES['stores'] = test_file

            stores = get_stores_by_department('01')
            assert len(stores) == 2
            assert all(s['department_id'] == '01' for s in stores)
        finally:
            base_module.DATA_DIR = original_data_dir
            base_module.DB_FILES = original_files


class TestPatientRepository:
    """Test suite for Patient repository functions"""

    def test_get_patients(self, temp_dir):
        """Test getting all patients"""
        from app.utils.database.patients import get_patients

        import app.utils.database.base as base_module
        original_data_dir = base_module.DATA_DIR
        original_files = base_module.DB_FILES.copy()

        try:
            base_module.DATA_DIR = temp_dir
            test_file = os.path.join(temp_dir, 'patients.json')
            test_data = [
                {'id': '01', 'first_name': 'John', 'last_name': 'Doe'},
                {'id': '02', 'first_name': 'Jane', 'last_name': 'Smith'}
            ]
            with open(test_file, 'w') as f:
                json.dump(test_data, f)
            base_module.DB_FILES['patients'] = test_file

            patients = get_patients()
            assert len(patients) == 2
            assert patients[0]['first_name'] == 'John'
        finally:
            base_module.DATA_DIR = original_data_dir
            base_module.DB_FILES = original_files

    def test_get_patient_by_id(self, temp_dir):
        """Test getting a specific patient by ID"""
        from app.utils.database.patients import get_patient_by_id

        import app.utils.database.base as base_module
        original_data_dir = base_module.DATA_DIR
        original_files = base_module.DB_FILES.copy()

        try:
            base_module.DATA_DIR = temp_dir
            test_file = os.path.join(temp_dir, 'patients.json')
            test_data = [
                {'id': '01', 'first_name': 'John', 'last_name': 'Doe'},
                {'id': '02', 'first_name': 'Jane', 'last_name': 'Smith'}
            ]
            with open(test_file, 'w') as f:
                json.dump(test_data, f)
            base_module.DB_FILES['patients'] = test_file

            patient = get_patient_by_id('02')
            assert patient is not None
            assert patient['first_name'] == 'Jane'
            assert patient['last_name'] == 'Smith'
        finally:
            base_module.DATA_DIR = original_data_dir
            base_module.DB_FILES = original_files


class TestPurchaseRepository:
    """Test suite for Purchase repository functions"""

    def test_get_purchases(self, temp_dir):
        """Test getting all purchases"""
        from app.utils.database.purchases import get_purchases

        import app.utils.database.base as base_module
        original_data_dir = base_module.DATA_DIR
        original_files = base_module.DB_FILES.copy()

        try:
            base_module.DATA_DIR = temp_dir
            test_file = os.path.join(temp_dir, 'purchases.json')
            test_data = [
                {'id': '01', 'supplier_id': '01', 'total_amount': 1000.00},
                {'id': '02', 'supplier_id': '02', 'total_amount': 500.00}
            ]
            with open(test_file, 'w') as f:
                json.dump(test_data, f)
            base_module.DB_FILES['purchases'] = test_file

            purchases = get_purchases()
            assert len(purchases) == 2
            assert purchases[0]['total_amount'] == 1000.00
        finally:
            base_module.DATA_DIR = original_data_dir
            base_module.DB_FILES = original_files

    def test_get_purchase_by_id(self, temp_dir):
        """Test getting a specific purchase by ID"""
        from app.utils.database.purchases import get_purchase_by_id

        import app.utils.database.base as base_module
        original_data_dir = base_module.DATA_DIR
        original_files = base_module.DB_FILES.copy()

        try:
            base_module.DATA_DIR = temp_dir
            test_file = os.path.join(temp_dir, 'purchases.json')
            test_data = [
                {'id': '01', 'supplier_id': '01', 'total_amount': 1000.00},
                {'id': '02', 'supplier_id': '02', 'total_amount': 500.00}
            ]
            with open(test_file, 'w') as f:
                json.dump(test_data, f)
            base_module.DB_FILES['purchases'] = test_file

            purchase = get_purchase_by_id('02')
            assert purchase is not None
            assert purchase['supplier_id'] == '02'
            assert purchase['total_amount'] == 500.00
        finally:
            base_module.DATA_DIR = original_data_dir
            base_module.DB_FILES = original_files


class TestConsumptionRepository:
    """Test suite for Consumption repository functions"""

    def test_get_consumption(self, temp_dir):
        """Test getting all consumption records"""
        from app.utils.database.consumption import get_consumption

        import app.utils.database.base as base_module
        original_data_dir = base_module.DATA_DIR
        original_files = base_module.DB_FILES.copy()

        try:
            base_module.DATA_DIR = temp_dir
            test_file = os.path.join(temp_dir, 'consumption.json')
            test_data = [
                {'id': '01', 'patient_id': '01', 'total_amount': 50.00},
                {'id': '02', 'patient_id': '02', 'total_amount': 75.00}
            ]
            with open(test_file, 'w') as f:
                json.dump(test_data, f)
            base_module.DB_FILES['consumption'] = test_file

            consumption = get_consumption()
            assert len(consumption) == 2
            assert consumption[0]['total_amount'] == 50.00
        finally:
            base_module.DATA_DIR = original_data_dir
            base_module.DB_FILES = original_files

    def test_get_consumption_by_patient(self, temp_dir):
        """Test getting consumption records by patient ID"""
        from app.utils.database.consumption import get_consumption_by_patient

        import app.utils.database.base as base_module
        original_data_dir = base_module.DATA_DIR
        original_files = base_module.DB_FILES.copy()

        try:
            base_module.DATA_DIR = temp_dir
            test_file = os.path.join(temp_dir, 'consumption.json')
            test_data = [
                {'id': '01', 'patient_id': '01', 'total_amount': 50.00},
                {'id': '02', 'patient_id': '01', 'total_amount': 25.00},
                {'id': '03', 'patient_id': '02', 'total_amount': 75.00}
            ]
            with open(test_file, 'w') as f:
                json.dump(test_data, f)
            base_module.DB_FILES['consumption'] = test_file

            consumption = get_consumption_by_patient('01')
            assert len(consumption) == 2
            assert all(c['patient_id'] == '01' for c in consumption)
        finally:
            base_module.DATA_DIR = original_data_dir
            base_module.DB_FILES = original_files


class TestTransferRepository:
    """Test suite for Transfer repository functions"""

    def test_get_transfers(self, temp_dir):
        """Test getting all transfers"""
        from app.utils.database.transfers import get_transfers

        import app.utils.database.base as base_module
        original_data_dir = base_module.DATA_DIR
        original_files = base_module.DB_FILES.copy()

        try:
            base_module.DATA_DIR = temp_dir
            test_file = os.path.join(temp_dir, 'transfers.json')
            test_data = [
                {'id': '01', 'source_store_id': '01', 'destination_store_id': '02'},
                {'id': '02', 'source_store_id': '02', 'destination_store_id': '03'}
            ]
            with open(test_file, 'w') as f:
                json.dump(test_data, f)
            base_module.DB_FILES['transfers'] = test_file

            transfers = get_transfers()
            assert len(transfers) == 2
            assert transfers[0]['source_store_id'] == '01'
        finally:
            base_module.DATA_DIR = original_data_dir
            base_module.DB_FILES = original_files

    def test_get_transfer_by_id(self, temp_dir):
        """Test getting a specific transfer by ID"""
        from app.utils.database.transfers import get_transfer_by_id

        import app.utils.database.base as base_module
        original_data_dir = base_module.DATA_DIR
        original_files = base_module.DB_FILES.copy()

        try:
            base_module.DATA_DIR = temp_dir
            test_file = os.path.join(temp_dir, 'transfers.json')
            test_data = [
                {'id': '01', 'source_store_id': '01', 'destination_store_id': '02'},
                {'id': '02', 'source_store_id': '02', 'destination_store_id': '03'}
            ]
            with open(test_file, 'w') as f:
                json.dump(test_data, f)
            base_module.DB_FILES['transfers'] = test_file

            transfer = get_transfer_by_id('02')
            assert transfer is not None
            assert transfer['source_store_id'] == '02'
            assert transfer['destination_store_id'] == '03'
        finally:
            base_module.DATA_DIR = original_data_dir
            base_module.DB_FILES = original_files
