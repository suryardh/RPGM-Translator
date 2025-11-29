from flask import Flask, request, jsonify, send_file 
from dotenv import load_dotenv
from flask_cors import CORS 
import os
import uuid
import time
import threading
from threading import Timer
import atexit
from translator import translate_rpgm_file, get_translation_status, update_translation_status
from file_handler import create_zip, save_uploaded_file, get_file_path, clean_up_files, parse_json_file, save_json_file

load_dotenv()

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def cleanup_old_data():
    import time
    from translator import translation_status
    
    current_time = time.time()
    for job_id in list(translation_status.keys()):
        if current_time - translation_status[job_id].get('timestamp', 0) > 86400:
            clean_up_files(job_id)
            del translation_status[job_id]
    
    Timer(3600, cleanup_old_data).start()

Timer(3600, cleanup_old_data).start()
atexit.register(cleanup_old_data)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        job_id = str(uuid.uuid4())
        original_filename = file.filename
        
        file_path = save_uploaded_file(file, job_id)
        
        update_translation_status(job_id, {
            'status': 'uploaded', 
            'original_filename': original_filename,
            'message': 'File uploaded successfully, ready to translate.'
        })
        
        return jsonify({
            'message': 'File uploaded successfully',
            'job_id': job_id,
            'file_path': file_path
        }), 200

@app.route('/api/translate', methods=['POST'])
def translate_file():
    data = request.json
    job_id = data.get('job_id')
    target_language = data.get('target_language')
    source_language = data.get('source_language', 'it')
    
    if not job_id or not target_language:
        return jsonify({'error': 'Missing job_id or target_language'}), 400
    
    try:
        thread = threading.Thread(target=translate_rpgm_file, args=(job_id, target_language, source_language))
        thread.start()
        
        return jsonify({'status': 'processing', 'message': 'Translation has started.'}), 202
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status/<job_id>', methods=['GET'])
def get_translation_status_endpoint(job_id):
    try:
        status = get_translation_status(job_id)
        return jsonify(status), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<job_id>')
def download_file(job_id):
    try:
        # 1. Ambil status untuk mendapatkan nama file yang benar
        status = get_translation_status(job_id)
        if status.get('status') != 'completed':
            return jsonify({'error': 'File not ready or not found.'}), 404

        zip_filename = status.get('zip_filename', 'translated.zip')

        # 2. Cari lokasi file
        translated_dir = get_file_path(job_id, translated=True)
        zip_path = os.path.join(os.path.dirname(translated_dir), zip_filename)
        
        # 3. Kirim file dengan nama yang benar
        return send_file(zip_path, as_attachment=True, download_name=zip_filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/translated_data/<job_id>', methods=['GET'])
def get_translated_data_route(job_id):
    try:
        status = get_translation_status(job_id)
        if status.get('status') != 'completed':
            return jsonify({'error': 'Translation not yet completed.'}), 400
        
        return jsonify({'logs': status.get('logs', [])}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/edit/<job_id>', methods=['POST'])
def edit_translation_route(job_id):
    try:
        data = request.json
        edited_logs = data.get('logs', [])
        
        if not edited_logs:
            return jsonify({'error': 'No edited logs provided.'}), 400

        translated_dir = get_file_path(job_id, translated=True)
        files_to_update = {}
        for log_entry in edited_logs:
            if log_entry.get('type') in ['object', 'dialog', 'common_event'] and log_entry.get('path'):
                file_name = log_entry.get('file')
                if file_name not in files_to_update:
                    file_path = os.path.join(translated_dir, file_name)
                    if os.path.exists(file_path):
                        files_to_update[file_name] = parse_json_file(file_path)
                
                if file_name in files_to_update:
                    path_parts = log_entry['path'].replace('[', '.').replace(']', '').split('.')
                    current_data = files_to_update[file_name]
                    for part in path_parts[:-1]:
                        if part.isdigit():
                            current_data = current_data[int(part)]
                        else:
                            current_data = current_data[part]
                    
                    final_key = path_parts[-1]
                    if final_key.isdigit():
                        current_data[int(final_key)] = log_entry['translated']
                    else:
                        current_data[final_key] = log_entry['translated']

        for file_name, content in files_to_update.items():
            file_path = os.path.join(translated_dir, file_name)
            save_json_file(content, file_path)
        
        zip_path = create_zip(translated_dir, job_id)
        
        return jsonify({
            'message': 'Translations updated successfully.',
            'download_url': f"/api/download/{job_id}"
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('FLASK_PORT', 5000))
    app.run(debug=True)