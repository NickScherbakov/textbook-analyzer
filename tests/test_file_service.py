import unittest
import os
import tempfile
import shutil
from app.services.file_service import FileService
from unittest.mock import MagicMock, patch

class TestFileService(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.test_upload_dir = tempfile.mkdtemp()
        
        # Patch the Config.UPLOAD_FOLDER
        patcher = patch('app.config.Config.UPLOAD_FOLDER', self.test_upload_dir)
        self.mock_config = patcher.start()
        self.addCleanup(patcher.stop)
        
        self.file_service = FileService()
    
    def tearDown(self):
        # Remove the temporary directory
        shutil.rmtree(self.test_upload_dir)
        
    def test_get_file_type(self):
        # Test various file extensions
        self.assertEqual(self.file_service.get_file_type('test.txt'), '.txt')
        self.assertEqual(self.file_service.get_file_type('test.jpg'), '.jpg')
        self.assertEqual(self.file_service.get_file_type('test.PDF'), '.pdf')
        self.assertEqual(self.file_service.get_file_type('test'), None)
        self.assertEqual(self.file_service.get_file_type(None), None)
    
    def test_save_file(self):
        # Create mock file
        mock_file = MagicMock()
        mock_file.filename = 'test.txt'
        
        # Call the method
        file_path = self.file_service.save_file(mock_file)
        
        # Verify the file was saved
        self.assertIsNotNone(file_path)
        self.assertTrue(file_path.startswith(self.test_upload_dir))
        self.assertTrue('test.txt' in file_path)
        mock_file.save.assert_called_once()
    
    def test_delete_file(self):
        # Create a test file
        test_file_path = os.path.join(self.test_upload_dir, 'test_delete.txt')
        with open(test_file_path, 'w') as f:
            f.write('test content')
        
        # Verify file exists
        self.assertTrue(os.path.exists(test_file_path))
        
        # Delete the file
        result = self.file_service.delete_file(test_file_path)
        
        # Verify deletion
        self.assertTrue(result)
        self.assertFalse(os.path.exists(test_file_path))
        
        # Try to delete non-existent file
        result = self.file_service.delete_file('/nonexistent/path.txt')
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
