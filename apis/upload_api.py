from flask import Blueprint, request, jsonify, send_from_directory, current_app
import os
import uuid

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': '没有选择文件'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': '没有选择文件'}), 400

        allowed_ext = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        if file and file.filename.rsplit('.', 1)[1].lower() in allowed_ext:
            file_ext = file.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
            upload_folder = os.path.join(current_app.root_path, 'uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            filepath = os.path.join(upload_folder, unique_filename)
            file.save(filepath)
            file_url = f"/uploads/{unique_filename}"
            return jsonify({'status': 'success', 'file_url': file_url, 'filename': unique_filename})
        return jsonify({'status': 'error', 'message': '文件类型不支持'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'上传失败: {str(e)}'}), 500

@upload_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    upload_folder = os.path.join(current_app.root_path, 'uploads')
    return send_from_directory(upload_folder, filename) 