import os
import json
import csv
import glob


def validate_record(record):
    # Check if the record is a dictionary and does not contain an error
    if not isinstance(record, dict) or 'error' in record:
        return False
    # Check for required fields and handle 'null' values
    if record.get('memorial_number') is None or record.get('inscription') is None:
        return False
    return True


def collect_records(records):
    valid_records = []
    for record in records:
        if validate_record(record):
            # Handle 'null' values for memorial_number and inscription
            record['memorial_number'] = record.get(
                'memorial_number', 'Unknown')
            record['inscription'] = record.get('inscription', 'No Inscription')
            valid_records.append(record)
    return valid_records


def process_json_content(content):
    # Replace 'NULL' with 'null' and handle escape sequences
    content = (
        content.replace('NULL', 'null')
               .replace('\\n', '\\\\n')  # Correctly escape newlines
               .replace('\\"', '\\\\"')  # Escape double quotes
               .replace('\\\\', '\\\\\\\\')  # Escape backslashes
               .replace('\\t', '\\\\t')  # Escape tabs
               .replace('\\r', '\\\\r')  # Escape carriage returns
    )
    try:
        records = json.loads(content)
        if isinstance(records, list):
            return collect_records(records)
        elif isinstance(records, dict):
            return collect_records([records])
    except json.JSONDecodeError:
        raise
    return []


def process_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            content = data['choices'][0]['message']['content']
            content = content.replace(
                '```json\n', '').replace('\n```', '').strip()
            return process_json_content(content)
    except json.JSONDecodeError:
        print(f"JSON decode error in file: {file_path}")
        raise
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        raise
    except Exception as e:
        print(f"Unexpected error in file {file_path}: {e}")
        raise


def process_json_files(folder_path):
    all_records = []
    for json_file in glob.glob(os.path.join(folder_path, '*.json')):
        records = process_json_file(json_file)
        # Replace non-integer values in 'memorial_number' with a default value (e.g., 0)
        for record in records:
            try:
                record['memorial_number'] = int(record['memorial_number'])
            except ValueError:
                record['memorial_number'] = 0  # Replace with the default value
        all_records.extend(records)
    # Sort the records by 'memorial_number' after the replacement
    return sorted(all_records, key=lambda x: x['memorial_number'])


def write_to_csv(records, csv_path):
    with open(csv_path, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=[
                                'memorial_number', 'inscription'])
        writer.writeheader()
        writer.writerows(records)


def main(json_folder_path, csv_file_path):
    try:
        sorted_records = process_json_files(json_folder_path)
        write_to_csv(sorted_records, csv_file_path)
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    json_folder_path = '/Users/danieltierney/Desktop/HistoricGraves/Kiltullagh_Roscommon/kil_output_jsons'
    csv_file_path = '/Users/danieltierney/Desktop/Dev/openai-playground/HG_TextHarvest_v1/test_folder/output.csv'
    main(json_folder_path, csv_file_path)
