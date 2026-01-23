"""
Unit tests for database base functions
"""

import pytest
import json
import os
import tempfile
from datetime import datetime

# Mark all tests in this module as unit tests
pytestmark = pytest.mark.unit


class TestLoadData:
    """Test suite for load_data function"""

    def test_load_data_valid_file(self, test_data_dir):
        """Test loading data from a valid JSON file"""
        from app.utils.database.base import load_data

        # Create test data
        test_data = [
            {'id': '01', 'name': 'Test Medicine', 'price': 10.0},
            {'id': '02', 'name': 'Another Medicine', 'price': 20.0}
        ]

        test_file = os.path.join(test_data_dir, 'test_medicines.json')
        with open(test_file, 'w') as f:
            json.dump(test_data, f)

        # Temporarily modify the DB_FILES dict
        import app.utils.database.base as base_module
        original_files = base_module.DB_FILES.copy()
        base_module.DB_FILES['test_medicines'] = test_file

        try:
            result = load_data('test_medicines')
            assert result == test_data
        finally:
            # Restore original DB_FILES
            base_module.DB_FILES = original_files

    def test_load_data_nonexistent_file(self, test_data_dir):
        """Test loading data from a non-existent file"""
        from app.utils.database.base import load_data

        # Test with a file type that doesn't have a valid path
        result = load_data('nonexistent')
        assert result == []

    def test_load_data_invalid_json(self, test_data_dir):
        """Test loading data from a file with invalid JSON"""
        from app.utils.database.base import load_data

        test_file = os.path.join(test_data_dir, 'invalid.json')
        with open(test_file, 'w') as f:
            f.write('invalid json content')

        import app.utils.database.base as base_module
        original_files = base_module.DB_FILES.copy()
        base_module.DB_FILES['invalid'] = test_file

        try:
            result = load_data('invalid')
            assert result == []
        finally:
            base_module.DB_FILES = original_files

    def test_load_data_empty_file(self, test_data_dir):
        """Test loading data from an empty JSON file"""
        from app.utils.database.base import load_data

        test_file = os.path.join(test_data_dir, 'empty.json')
        with open(test_file, 'w') as f:
            json.dump([], f)

        import app.utils.database.base as base_module
        original_files = base_module.DB_FILES.copy()
        base_module.DB_FILES['empty'] = test_file

        try:
            result = load_data('empty')
            assert result == []
        finally:
            base_module.DB_FILES = original_files


class TestSaveData:
    """Test suite for save_data function"""

    def test_save_data_valid_data(self, test_data_dir):
        """Test saving valid data to a file"""
        from app.utils.database.base import save_data

        test_file = os.path.join(test_data_dir, 'save_test.json')
        test_data = [
            {'id': '01', 'name': 'Test Medicine', 'price': 10.0}
        ]

        import app.utils.database.base as base_module
        original_files = base_module.DB_FILES.copy()
        base_module.DB_FILES['save_test'] = test_file

        try:
            result = save_data('save_test', test_data)
            assert result is True

            # Verify file was created and contains correct data
            with open(test_file, 'r') as f:
                saved_data = json.load(f)
            assert saved_data == test_data
        finally:
            base_module.DB_FILES = original_files

    def test_save_data_invalid_file_type(self):
        """Test saving data with an invalid file type"""
        from app.utils.database.base import save_data

        test_data = [{'id': '01', 'name': 'Test'}]
        result = save_data('invalid_file_type', test_data)
        assert result is False

    def test_save_data_readonly_directory(self, monkeypatch):
        """Test saving data when directory is read-only"""
        from app.utils.database.base import save_data

        # Mock to fail on file write
        def mock_open(*args, **kwargs):
            raise PermissionError("Permission denied")

        monkeypatch.setattr('builtins.open', mock_open)

        test_data = [{'id': '01', 'name': 'Test'}]
        result = save_data('users', test_data)
        assert result is False


class TestGenerateID:
    """Test suite for generate_id function"""

    def test_generate_id_empty_data(self, test_data_dir):
        """Test ID generation with empty data"""
        from app.utils.database.base import generate_id

        test_file = os.path.join(test_data_dir, 'empty_test.json')
        with open(test_file, 'w') as f:
            json.dump([], f)

        import app.utils.database.base as base_module
        original_files = base_module.DB_FILES.copy()
        base_module.DB_FILES['empty_test'] = test_file

        try:
            result = generate_id('empty_test')
            assert result == '01'
        finally:
            base_module.DB_FILES = original_files

    def test_generate_id_single_record(self, test_data_dir):
        """Test ID generation with existing single record"""
        from app.utils.database.base import generate_id

        test_data = [{'id': '01', 'name': 'Test'}]
        test_file = os.path.join(test_data_dir, 'single_test.json')
        with open(test_file, 'w') as f:
            json.dump(test_data, f)

        import app.utils.database.base as base_module
        original_files = base_module.DB_FILES.copy()
        base_module.DB_FILES['single_test'] = test_file

        try:
            result = generate_id('single_test')
            assert result == '02'
        finally:
            base_module.DB_FILES = original_files

    def test_generate_id_multiple_records(self, test_data_dir):
        """Test ID generation with multiple records"""
        from app.utils.database.base import generate_id

        test_data = [
            {'id': '01', 'name': 'Test1'},
            {'id': '02', 'name': 'Test2'},
            {'id': '03', 'name': 'Test3'}
        ]
        test_file = os.path.join(test_data_dir, 'multiple_test.json')
        with open(test_file, 'w') as f:
            json.dump(test_data, f)

        import app.utils.database.base as base_module
        original_files = base_module.DB_FILES.copy()
        base_module.DB_FILES['multiple_test'] = test_file

        try:
            result = generate_id('multiple_test')
            assert result == '04'
        finally:
            base_module.DB_FILES = original_files

    def test_generate_id_gaps_in_sequence(self, test_data_dir):
        """Test ID generation with gaps in sequence"""
        from app.utils.database.base import generate_id

        test_data = [
            {'id': '01', 'name': 'Test1'},
            {'id': '03', 'name': 'Test3'},
            {'id': '05', 'name': 'Test5'}
        ]
        test_file = os.path.join(test_data_dir, 'gaps_test.json')
        with open(test_file, 'w') as f:
            json.dump(test_data, f)

        import app.utils.database.base as base_module
        original_files = base_module.DB_FILES.copy()
        base_module.DB_FILES['gaps_test'] = test_file

        try:
            result = generate_id('gaps_test')
            # Should return highest + 1 = 06
            assert result == '06'
        finally:
            base_module.DB_FILES = original_files

    def test_generate_id_non_numeric_ids(self, test_data_dir):
        """Test ID generation with non-numeric IDs"""
        from app.utils.database.base import generate_id

        test_data = [
            {'id': 'abc', 'name': 'Test1'},
            {'id': 'xyz', 'name': 'Test2'}
        ]
        test_file = os.path.join(test_data_dir, 'non_numeric_test.json')
        with open(test_file, 'w') as f:
            json.dump(test_data, f)

        import app.utils.database.base as base_module
        original_files = base_module.DB_FILES.copy()
        base_module.DB_FILES['non_numeric_test'] = test_file

        try:
            result = generate_id('non_numeric_test')
            # Should handle non-numeric IDs gracefully
            assert result == '01'
        finally:
            base_module.DB_FILES = original_files


class TestInitDatabase:
    """Test suite for init_database function"""

    def test_init_database_creates_files(self, temp_dir):
        """Test that init_database creates all required files"""
        from app.utils.database.base import init_database, DB_FILES

        # Temporarily change DATA_DIR to temp_dir
        import app.utils.database.base as base_module
        original_data_dir = base_module.DATA_DIR
        original_files = base_module.DB_FILES.copy()

        try:
            base_module.DATA_DIR = temp_dir
            # Update DB_FILES to use temp_dir
            new_files = {}
            for key, _ in original_files.items():
                new_files[key] = os.path.join(temp_dir, f'{key}.json')
            base_module.DB_FILES = new_files

            # Initialize database
            init_database()

            # Check that all files were created
            for file_type, file_path in new_files.items():
                assert os.path.exists(file_path), f"File {file_path} was not created"

                # Verify file contains valid JSON
                with open(file_path, 'r') as f:
                    data = json.load(f)
                assert isinstance(data, list), f"File {file_path} does not contain a list"
        finally:
            base_module.DATA_DIR = original_data_dir
            base_module.DB_FILES = original_files

    def test_init_database_preserves_existing_data(self, temp_dir):
        """Test that init_database preserves existing data"""
        from app.utils.database.base import init_database

        import app.utils.database.base as base_module
        original_data_dir = base_module.DATA_DIR
        original_files = base_module.DB_FILES.copy()

        try:
            base_module.DATA_DIR = temp_dir
            # Update DB_FILES to use temp_dir
            new_files = {}
            for key, _ in original_files.items():
                new_files[key] = os.path.join(temp_dir, f'{key}.json')
            base_module.DB_FILES = new_files

            # Pre-create a file with existing data
            existing_data = [{'id': '01', 'name': 'Existing Medicine'}]
            with open(new_files['medicines'], 'w') as f:
                json.dump(existing_data, f)

            # Initialize database
            init_database()

            # Verify existing data is preserved
            with open(new_files['medicines'], 'r') as f:
                saved_data = json.load(f)
            assert saved_data == existing_data
        finally:
            base_module.DATA_DIR = original_data_dir
            base_module.DB_FILES = original_files


class TestEnsureMainEntities:
    """Test suite for ensure_main_entities function"""

    def test_ensure_main_entities_creates_missing(self, temp_dir):
        """Test that ensure_main_entities creates missing main entities"""
        from app.utils.database.base import ensure_main_entities

        import app.utils.database.base as base_module
        original_data_dir = base_module.DATA_DIR
        original_files = base_module.DB_FILES.copy()

        try:
            base_module.DATA_DIR = temp_dir
            # Update DB_FILES to use temp_dir
            new_files = {}
            for key, _ in original_files.items():
                new_files[key] = os.path.join(temp_dir, f'{key}.json')
            base_module.DB_FILES = new_files

            # Initialize database with empty data
            init_database()

            # Manually delete main department and store
            departments = []
            stores = []
            with open(new_files['departments'], 'w') as f:
                json.dump(departments, f)
            with open(new_files['stores'], 'w') as f:
                json.dump(stores, f)

            # Call ensure_main_entities
            ensure_main_entities()

            # Verify main department was recreated
            with open(new_files['departments'], 'r') as f:
                departments = json.load(f)
            assert len(departments) == 1
            assert departments[0]['id'] == '01'
            assert departments[0]['name'] == 'Main Pharmacy'

            # Verify main store was recreated
            with open(new_files['stores'], 'r') as f:
                stores = json.load(f)
            assert len(stores) == 1
            assert stores[0]['id'] == '01'
            assert stores[0]['name'] == 'Main Pharmacy Store'
            assert stores[0]['department_id'] == '01'
        finally:
            base_module.DATA_DIR = original_data_dir
            base_module.DB_FILES = original_files

    def test_ensure_main_entities_preserves_existing(self, temp_dir):
        """Test that ensure_main_entities preserves existing main entities"""
        from app.utils.database.base import ensure_main_entities

        import app.utils.database.base as base_module
        original_data_dir = base_module.DATA_DIR
        original_files = base_module.DB_FILES.copy()

        try:
            base_module.DATA_DIR = temp_dir
            # Update DB_FILES to use temp_dir
            new_files = {}
            for key, _ in original_files.items():
                new_files[key] = os.path.join(temp_dir, f'{key}.json')
            base_module.DB_FILES = new_files

            # Initialize database normally
            init_database()

            # Call ensure_main_entities
            ensure_main_entities()

            # Verify main department still exists
            with open(new_files['departments'], 'r') as f:
                departments = json.load(f)
            main_dept = [d for d in departments if d['id'] == '01']
            assert len(main_dept) == 1
            assert main_dept[0]['name'] == 'Main Pharmacy'

            # Verify main store still exists
            with open(new_files['stores'], 'r') as f:
                stores = json.load(f)
            main_store = [s for s in stores if s['id'] == '01']
            assert len(main_store) == 1
            assert main_store[0]['name'] == 'Main Pharmacy Store'
        finally:
            base_module.DATA_DIR = original_data_dir
            base_module.DB_FILES = original_files
