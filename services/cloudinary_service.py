import cloudinary
import cloudinary.uploader
from config import settings
import os
import mimetypes

cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET")
)

class CloudinaryUploader:
    @staticmethod
    def upload(file, folder="ministry_works"):
        try:
            # Extract filename from the SpooledTemporaryFile
            filename = getattr(file, "filename", "unknown_file")

            # Read file content as bytes
            file_bytes = file.read()

            # Detect file type using filename
            mime_type, _ = mimetypes.guess_type(filename)

            # Set resource type dynamically
            if mime_type:
                if mime_type.startswith("image"):
                    resource_type = "image"
                elif mime_type.startswith("video"):
                    resource_type = "video"
                else:
                    resource_type = "raw"  # Default for PDFs, ZIPs, etc.
            else:
                resource_type = "raw"  # Fallback for unknown types

            # Upload to Cloudinary using raw bytes
            result = cloudinary.uploader.upload(
                file_bytes,
                folder=folder,
                resource_type=resource_type,
                filename=filename  # Pass filename to help Cloudinary
            )
            return result["secure_url"]
        except Exception as e:
            raise Exception(f"Failed to upload file to Cloudinary: {str(e)}")

    @staticmethod
    def delete(public_id, resource_type="raw"):
        try:
            cloudinary.uploader.destroy(public_id, resource_type=resource_type)
        except Exception as e:
            raise Exception(f"Failed to delete file from Cloudinary: {str(e)}")

cloudinary_uploader = CloudinaryUploader()
