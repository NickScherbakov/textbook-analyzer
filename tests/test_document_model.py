import unittest
from app.models.document import Document
from datetime import datetime

class TestDocumentModel(unittest.TestCase):
    def test_document_initialization(self):
        # Arrange & Act
        doc = Document(
            title="Test Document",
            content="This is test content",
            file_path="/path/to/file.txt",
            file_type=".txt"
        )
        
        # Assert
        self.assertEqual(doc.title, "Test Document")
        self.assertEqual(doc.content, "This is test content")
        self.assertEqual(doc.file_path, "/path/to/file.txt")
        self.assertEqual(doc.file_type, ".txt")
        
    def test_to_dict_method(self):
        # Arrange
        doc = Document(
            title="Test Document",
            content="This is test content",
            file_path="/path/to/file.txt",
            file_type=".txt"
        )
        # Mock the database-generated fields
        doc.id = 1
        doc.uuid = "test-uuid"
        doc.created_at = datetime(2023, 1, 1, 12, 0, 0)
        doc.updated_at = datetime(2023, 1, 1, 12, 0, 0)
        
        # Act
        result = doc.to_dict()
        
        # Assert
        self.assertEqual(result["id"], 1)
        self.assertEqual(result["uuid"], "test-uuid")
        self.assertEqual(result["title"], "Test Document")
        self.assertEqual(result["content"], "This is test content")
        self.assertEqual(result["file_path"], "/path/to/file.txt")
        self.assertEqual(result["file_type"], ".txt")
        self.assertEqual(result["created_at"], "2023-01-01T12:00:00")
        self.assertEqual(result["updated_at"], "2023-01-01T12:00:00")

if __name__ == '__main__':
    unittest.main()
