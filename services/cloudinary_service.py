import cloudinary
import cloudinary.uploader
from config import settings
import os

cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET")
)


class CloudinaryUploader:
    @staticmethod
    def upload(file, folder="ministry_works"):
        try:
            result = cloudinary.uploader.upload(
                file,
                folder=folder,
                resource_type="auto"
            )
            return result["secure_url"]
        except Exception as e:
            raise Exception(f"Failed to upload file to Cloudinary: {str(e)}")

    @staticmethod
    def delete(public_id):
        try:
            cloudinary.uploader.destroy(public_id)
        except Exception as e:
            raise Exception(f"Failed to delete file from Cloudinary: {str(e)}")

cloudinary_uploader = CloudinaryUploader()