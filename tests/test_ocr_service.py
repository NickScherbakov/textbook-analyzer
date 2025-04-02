import unittest
import os
import io
from PIL import Image
from app.services.ocr_service import OCRService
from unittest.mock import patch, MagicMock

class TestOCRService(unittest.TestCase):
    def setUp(self):
        self.ocr_service = OCRService()
    
    @patch('pytesseract.image_to_string')
    def test_process_image_calls_tesseract(self, mock_image_to_string):
        # Arrange
        mock_image_to_string.return_value = "Sample text"
        
        # Create a simple test image
        img = Image.new('RGB', (100, 30), color = (255, 255, 255))
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # Act
        result = self.ocr_service.process_image(img_byte_arr)
        
        # Assert
        self.assertEqual(result, "Sample text")
        mock_image_to_string.assert_called_once()

if __name__ == '__main__':
    unittest.main()
