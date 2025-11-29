import os
import json
import shutil
import zipfile
from werkzeug.utils import secure_filename # pyright: ignore[reportMissingImports]

UPLOAD_FOLDER = 'uploads'

def save_uploaded_file(file, job_id):
    job_dir = os.path.join(UPLOAD_FOLDER, job_id)
    os.makedirs(job_dir, exist_ok=True)
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(job_dir, filename)
    file.save(file_path)
    
    print(f"Received file: {filename}")

    if filename.endswith('.zip'):
        print("File is a ZIP archive. Extracting...")
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(job_dir)
        os.remove(file_path)
        print("Extraction complete.")
    elif filename.endswith('.json'):
        print("File is a single JSON. No extraction needed.")
    else:
        print("File is not a recognized ZIP or JSON. It will be ignored by the translation process.")

    return job_dir

def get_file_path(job_id, translated=False):
    job_dir = os.path.join(UPLOAD_FOLDER, job_id)
    if translated:
        translated_dir = os.path.join(job_dir, 'translated')
        if not os.path.exists(translated_dir):
            raise FileNotFoundError(f"Translated files not found for job {job_id}")
        return translated_dir
    else:
        if not os.path.exists(job_dir):
            raise FileNotFoundError(f"Files not found for job {job_id}")
        return job_dir

def clean_up_files(job_id):
    job_dir = os.path.join(UPLOAD_FOLDER, job_id)
    if os.path.exists(job_dir):
        shutil.rmtree(job_dir)

def create_translated_directory(job_id):
    job_dir = os.path.join(UPLOAD_FOLDER, job_id)
    translated_dir = os.path.join(job_dir, 'translated')
    os.makedirs(translated_dir, exist_ok=True)
    return translated_dir

def get_rpgm_files(directory):
    """Find all RPG Maker files that need translation in a more robust way."""
    rpgm_files = []
    
    data_dir = os.path.join(directory, 'data')
    if os.path.exists(data_dir) and os.path.isdir(data_dir):
        for file in os.listdir(data_dir):
            if file.endswith('.json'):
                rpgm_files.append(os.path.join(data_dir, file))
        if rpgm_files:
            print(f"Found {len(rpgm_files)} files in standard 'data' directory.")
            return rpgm_files

    for file in os.listdir(directory):
        if file.endswith('.json'):
            rpgm_files.append(os.path.join(directory, file))
    if rpgm_files:
        print(f"Found {len(rpgm_files)} files in the root directory (likely a single file upload).")
        return rpgm_files

    subdirs = [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]
    if len(subdirs) == 1:
        potential_game_dir = os.path.join(directory, subdirs[0])
        potential_data_dir = os.path.join(potential_game_dir, 'data')
        if os.path.exists(potential_data_dir) and os.path.isdir(potential_data_dir):
            for file in os.listdir(potential_data_dir):
                if file.endswith('.json'):
                    rpgm_files.append(os.path.join(potential_data_dir, file))
            if rpgm_files:
                print(f"Found {len(rpgm_files)} files in a subdirectory '{subdirs[0]}/data'.")
                return rpgm_files

    print("Could not find any RPG Maker .json files.")
    return rpgm_files

def parse_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        return json.load(f)

def save_json_file(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def create_zip(translated_dir, job_id, filename="translated.zip"):
    zip_path = os.path.join(os.path.dirname(translated_dir), filename)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(translated_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, translated_dir)
                zipf.write(file_path, arcname)
    return zip_path