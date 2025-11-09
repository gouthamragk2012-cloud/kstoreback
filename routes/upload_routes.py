from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
import os
import uuid
from utils.response_utils import success_response, error_response
from utils.auth_utils import admin_required

upload_bp = Blueprint('upload', __name__)

# Configure upload settings
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_folder():
    """Ensure upload folder exists"""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

@upload_bp.route('/image', methods=['POST'])
@jwt_required()
@admin_required()
def upload_image():
    """Upload product image"""
    ensure_upload_folder()
    
    if 'file' not in request.files:
        return error_response('No file provided')
    
    file = request.files['file']
    
    if file.filename == '':
        return error_response('No file selected')
    
    if not allowed_file(file.filename):
        return error_response('Invalid file type. Allowed: png, jpg, jpeg, gif, webp')
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        return error_response('File too large. Maximum size: 5MB')
    
    # Generate unique filename
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    try:
        file.save(filepath)
        
        # Return URL (adjust based on your server setup)
        image_url = f"/static/uploads/{filename}"
        
        return success_response({
            'image_url': image_url,
            'filename': filename
        }, 'Image uploaded successfully', 201)
        
    except Exception as e:
        return error_response(f'Upload failed: {str(e)}', 500)

@upload_bp.route('/images', methods=['POST'])
@jwt_required()
@admin_required()
def upload_multiple_images():
    """Upload multiple product images"""
    ensure_upload_folder()
    
    if 'files' not in request.files:
        return error_response('No files provided')
    
    files = request.files.getlist('files')
    
    if not files:
        return error_response('No files selected')
    
    uploaded_images = []
    errors = []
    
    for file in files:
        if file.filename == '':
            continue
            
        if not allowed_file(file.filename):
            errors.append(f'{file.filename}: Invalid file type')
            continue
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            errors.append(f'{file.filename}: File too large')
            continue
        
        # Generate unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        try:
            file.save(filepath)
            image_url = f"/static/uploads/{filename}"
            uploaded_images.append({
                'image_url': image_url,
                'filename': filename,
                'original_name': file.filename
            })
        except Exception as e:
            errors.append(f'{file.filename}: {str(e)}')
    
    if not uploaded_images and errors:
        return error_response('All uploads failed', 400)
    
    return success_response({
        'images': uploaded_images,
        'errors': errors if errors else None
    }, f'{len(uploaded_images)} images uploaded successfully', 201)
