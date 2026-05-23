import os
import tempfile
from pathlib import Path
from werkzeug.utils import secure_filename


ALLOWED_FACE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


def get_uploaded_face_file(request_files):
    """
    Accepts an uploaded image from:
    - backend test form
    - Postman
    - PowerShell Invoke-RestMethod
    - ESP32-CAM later

    Required multipart/form-data field:
    faceImage
    """
    if "faceImage" not in request_files:
        return None, {
            "success": False,
            "message": "faceImage file is required",
            "reason": "missing_face_image",
        }

    uploaded_file = request_files["faceImage"]

    if not uploaded_file or uploaded_file.filename == "":
        return None, {
            "success": False,
            "message": "Uploaded face image is empty",
            "reason": "empty_filename",
        }

    filename = secure_filename(uploaded_file.filename)
    suffix = Path(filename).suffix.lower()

    if suffix not in ALLOWED_FACE_SUFFIXES:
        return None, {
            "success": False,
            "message": "Invalid image type. Use jpg, jpeg, png, or webp.",
            "reason": "invalid_file_type",
        }

    return {
        "file": uploaded_file,
        "filename": filename,
        "suffix": suffix,
    }, None


def save_uploaded_face_temporarily(uploaded_face):
    """
    Saves uploaded image to a temporary file.
    Returns temp file path.
    Caller should delete it after processing.
    """
    uploaded_file = uploaded_face["file"]
    suffix = uploaded_face["suffix"]

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_path = temp_file.name
        uploaded_file.save(temp_path)

    return temp_path


def delete_temp_face_file(temp_path):
    if temp_path and os.path.exists(temp_path):
        os.remove(temp_path)