import os
import uuid
import shutil
from werkzeug.utils import secure_filename
from app.config import Config

class FileService:
    def __init__(self):
        self.upload_folder = Config.UPLOAD_FOLDER
        # Create upload folder if it doesn't exist
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)

    def save_file(self, file):
        """
        Save an uploaded file to a permanent location
        and return the file path
        """
        if file and file.filename:
            filename = secure_filename(file.filename)
            # Generate unique filename
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(self.upload_folder, unique_filename)
            file.save(file_path)
            return file_path
        return None

    def delete_file(self, file_path):
        """Delete a file from the filesystem"""
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

    def get_file_type(self, filename):
        """Get the file type based on extension"""
        if not filename:
            return None
        return os.path.splitext(filename)[1].lower()
