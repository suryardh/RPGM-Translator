import os
import json
import time
import copy
from googletrans import Translator # type: ignore
from print_neatly import print_neatly
from file_handler import (
    get_rpgm_files, parse_json_file, save_json_file, 
    create_translated_directory, create_zip, get_file_path
)

translator = Translator()
translation_status = {}

def update_translation_status(job_id, status):
    status['timestamp'] = time.time()
    translation_status[job_id] = status

def get_translation_status(job_id):
    return translation_status.get(job_id, {'status': 'not_found'})

def translate_sentence(text, src='it', dst='en'):
    if not text or not text.strip(): return text
    try:
        translation = translator.translate(text, src=src, dest=dst).text
        if text[0].isalpha() and translation[0].isalpha() and not text[0].isupper():
            translation = translation[0].lower() + translation[1:]
        return translation
    except Exception as e:
        print(f"Direct translation failed for '{text}': {e}")
        return text

def try_translate_sentence(text, src='it', dst='en', max_retries=3):
    if not text or not text.strip(): return text, True
    for attempt in range(max_retries):
        try:
            result = translate_sentence(text, src, dst)
            return result, True
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Translation failed after {max_retries} retries for '{text}': {e}")
                return text, False
            time.sleep(1)
    return text, False

def translate_objects_file(data, src, dst, logs, max_len=55):
    translations = 0
    for i, d in enumerate(data):
        if d is None: continue
        total_items = sum(1 for key in d if key in ['name', 'description', 'profile'] or key.startswith('message'))
        current_item_index = 0

        if 'name' in d and d['name'] and len(d['name'].strip()) > 0:
            current_item_index += 1
            tr, success = try_translate_sentence(d['name'], src, dst)
            if success:
                translations += 1
                logs.append({'type': 'object', 'file': '', 'path': f'object[{i}].name', 'index': current_item_index, 'total': total_items, 'raw': d['name'], 'translated': tr})
                d['name'] = tr
            else: logs.append({'type': 'anomaly', 'path': f'object[{i}].name', 'raw': d['name']})

        if 'description' in d and d['description'] and len(d['description'].strip()) > 0:
            current_item_index += 1
            tr, success = try_translate_sentence(d['description'], src, dst)
            if success:
                translations += 1
                try: text_neat = print_neatly(tr, max_len); final_translated = '\n'.join(text_neat)
                except: final_translated = tr
                logs.append({'type': 'object', 'file': '', 'path': f'object[{i}].description', 'index': current_item_index, 'total': total_items, 'raw': d['description'], 'translated': final_translated})
                d['description'] = final_translated
            else: logs.append({'type': 'anomaly', 'path': f'object[{i}].description', 'raw': d['description']})

        if 'profile' in d and d['profile'] and len(d['profile'].strip()) > 0:
            current_item_index += 1
            tr, success = try_translate_sentence(d['profile'], src, dst)
            if success:
                translations += 1
                try: text_neat = print_neatly(tr, max_len); final_translated = '\n'.join(text_neat)
                except: final_translated = tr
                logs.append({'type': 'object', 'file': '', 'path': f'object[{i}].profile', 'index': current_item_index, 'total': total_items, 'raw': d['profile'], 'translated': final_translated})
                d['profile'] = final_translated
            else: logs.append({'type': 'anomaly', 'path': f'object[{i}].profile', 'raw': d['profile']})
        
        for m in range(1, 5):
            message_key = f'message{m}'
            if message_key in d and d[message_key] and len(d[message_key].strip()) > 0:
                current_item_index += 1
                tr, success = try_translate_sentence(d[message_key], src, dst)
                if success:
                    translations += 1
                    logs.append({'type': 'object', 'file': '', 'path': f'object[{i}].{message_key}', 'index': current_item_index, 'total': total_items, 'raw': d[message_key], 'translated': tr})
                    d[message_key] = tr
                else: logs.append({'type': 'anomaly', 'path': f'object[{i}].{message_key}', 'raw': d[message_key]})
    return data, translations

def translate_dialogs_file(data, src, dst, logs, max_len=40, use_neatly=False):
    translations = 0
    all_translatable_items = []
    for event in data.get("events", []):
        if event is None: continue
        for page in event.get('pages', []):
            for command in page.get('list', []):
                if command.get('code') in [401, 102] or (command.get('code') == 402 and len(command.get('parameters', [])) == 2):
                    all_translatable_items.append({'event': event, 'page': page, 'command': command})
    total_items = len(all_translatable_items)

    for i, item in enumerate(all_translatable_items):
        command = item['command']; current_index = i + 1
        if command.get('code') == 102:
            for j, choice in enumerate(command['parameters'][0]):
                if choice:
                    tr, success = try_translate_sentence(choice, src, dst)
                    if success:
                        translations += 1
                        logs.append({'type': 'dialog', 'file': '', 'path': f'command[{i}].choice[{j}]', 'index': current_index, 'total': total_items, 'raw': choice, 'translated': tr})
                        command['parameters'][0][j] = tr
                    else: logs.append({'type': 'anomaly', 'path': f'command[{i}].choice[{j}]', 'raw': choice})
        elif command.get('code') == 402:
            tr, success = try_translate_sentence(command['parameters'][1], src, dst)
            if success:
                translations += 1
                logs.append({'type': 'dialog', 'file': '', 'path': f'command[{i}].answer', 'index': current_index, 'total': total_items, 'raw': command['parameters'][1], 'translated': tr})
                command['parameters'][1] = tr
            else: logs.append({'type': 'anomaly', 'path': f'command[{i}].answer', 'raw': command['parameters'][1]})
        elif command.get('code') == 401:
            tr, success = try_translate_sentence(command['parameters'][0], src, dst)
            if success:
                translations += 1
                logs.append({'type': 'dialog', 'file': '', 'path': f'command[{i}].text', 'index': current_index, 'total': total_items, 'raw': command['parameters'][0], 'translated': tr})
                command['parameters'][0] = tr
            else: logs.append({'type': 'anomaly', 'path': f'command[{i}].text', 'raw': command['parameters'][0]})
    return data, translations

def translate_common_events_file(data, src, dst, logs, max_len=55):
    translations = 0
    all_translatable_items = []
    for d in data:
        if d is None: continue
        for command in d.get('list', []):
            if command.get('code') == 401:
                all_translatable_items.append({'event': d, 'command': command})
    total_items = len(all_translatable_items)
    for i, item in enumerate(all_translatable_items):
        command = item['command']; current_index = i + 1
        tr, success = try_translate_sentence(command['parameters'][0], src, dst)
        if success:
            translations += 1
            logs.append({'type': 'common_event', 'file': '', 'path': f'common_event[{i}].text', 'index': current_index, 'total': total_items, 'raw': command['parameters'][0], 'translated': tr})
            command['parameters'][0] = tr
        else: logs.append({'type': 'anomaly', 'path': f'common_event[{i}].text', 'raw': command['parameters'][0]})
    return data, translations

def translate_rpgm_file(job_id, target_language, source_language='it'):
    try:
        initial_status = get_translation_status(job_id)
        original_filename = initial_status.get('original_filename', 'project')
        base_name = os.path.splitext(original_filename)[0]
        zip_filename = f"{target_language}_{base_name}.zip"

        update_translation_status(job_id, {'status': 'processing', 'total_files': 0, 'current_file': 0, 'logs': []})
        
        source_dir = get_file_path(job_id)
        translated_dir = create_translated_directory(job_id)
        rpgm_files = get_rpgm_files(source_dir)
        
        if not rpgm_files:
            error_message = "No RPG Maker files found. Please upload a .zip file of your project containing the 'data' folder with .json files, or a single .json file."
            update_translation_status(job_id, {'status': 'error', 'message': error_message})
            return {'status': 'error', 'message': error_message}

        structured_logs = []
        update_translation_status(job_id, {'status': 'processing', 'total_files': len(rpgm_files), 'current_file': 0, 'logs': structured_logs})
        
        total_translations = 0
        for i, file_path in enumerate(rpgm_files):
            file_name = os.path.basename(file_path)
            update_translation_status(job_id, {'status': 'processing', 'total_files': len(rpgm_files), 'current_file': i + 1, 'logs': structured_logs})
            
            try:
                data = parse_json_file(file_path); t = 0
                if file_name.startswith('Map'): data, t = translate_dialogs_file(data, source_language, target_language, structured_logs, use_neatly=True)
                elif file_name == 'CommonEvents.json': data, t = translate_common_events_file(data, source_language, target_language, structured_logs)
                elif file_name in ['Actors.json', 'Classes.json', 'Skills.json', 'Items.json', 'Weapons.json', 'Armors.json', 'Enemies.json', 'States.json', 'System.json']:
                    data, t = translate_objects_file(data, source_language, target_language, structured_logs)
                else: continue
                
                for log_entry in structured_logs:
                    if log_entry.get('file') == '': log_entry['file'] = file_name

                total_translations += t
                relative_path = os.path.relpath(file_path, source_dir)
                translated_file_path = os.path.join(translated_dir, relative_path)
                os.makedirs(os.path.dirname(translated_file_path), exist_ok=True)
                save_json_file(data, translated_file_path)
            except Exception as e:
                structured_logs.append({'type': 'error', 'message': f"CRITICAL ERROR processing {file_name}: {str(e)}"})
                update_translation_status(job_id, {'status': 'processing', 'total_files': len(rpgm_files), 'current_file': i + 1, 'logs': structured_logs})
                continue
        
        zip_path = create_zip(translated_dir, job_id, zip_filename)
        final_status = {'status': 'completed',
                         'total_files': len(rpgm_files),
                         'current_file': len(rpgm_files),
                         'logs': structured_logs,
                         'download_url': f"/api/download/{job_id}",
                         'total_translations': total_translations,
                         'zip_filename': zip_filename
                         }
        
        update_translation_status(job_id, final_status)
        return final_status
    
    except Exception as e:
        error_status = {'status': 'error', 'message': str(e)}
        update_translation_status(job_id, error_status)
        return error_status