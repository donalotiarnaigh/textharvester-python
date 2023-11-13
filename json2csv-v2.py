import os
import json
import csv
import glob


def append_to_csv(records, csv_path):
    file_exists = os.path.isfile(csv_path)

    with open(csv_path, 'a', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=[
                                'memorial_number', 'name', 'date', 'location'])

        if not file_exists:
            writer.writeheader()

        for record in records:
            if isinstance(record, dict):
                # Skip records with unexpected fields
                if 'error' in record:
                    print(f"Skipping record with error: {record}")
                    continue
                writer.writerow(record)
            else:
                print(f"Skipping invalid record: {record}")


def process_json_files(folder_path, csv_path):
    for json_file in glob.glob(os.path.join(folder_path, '*.json')):
        try:
            with open(json_file, 'r') as file:
                try:
                    data = json.load(file)

                    content = data['choices'][0]['message']['content']
                    content = content.replace(
                        '```json\n', '').replace('\n```', '').strip()

                    try:
                        records = json.loads(content)
                        if isinstance(records, list):
                            append_to_csv(records, csv_path)
                        elif isinstance(records, dict):
                            append_to_csv([records], csv_path)
                        else:
                            print(
                                f"Invalid format in file {json_file}: Records is not a list or a dict")
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error in file {json_file}: {e}")

                except json.JSONDecodeError as e:
                    print(f"JSON decode error in file {json_file}: {e}")

        except FileNotFoundError:
            print(f"File not found: {json_file}")
        except Exception as e:
            print(f"Unexpected error in file {json_file}: {e}")


json_folder_path = 'PATH_TO_JSON_FOLDER'  # Replace with actual folder path
csv_file_path = 'PATH_TO_CSV_FILE'  # Replace with actual file path

process_json_files(json_folder_path, csv_file_path)
