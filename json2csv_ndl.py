import os
import json
import csv
import glob


def collect_records(records):
    valid_records = []
    for record in records:
        if isinstance(record, dict):
            if 'error' not in record:
                valid_records.append(record)
                print(f"Record added: {record}")
            else:
                print(f"Skipping record with error: {record}")
        else:
            print(f"Skipping invalid record: {record}")
    return valid_records


def process_json_files(folder_path):
    all_records = []
    print(f"Starting to process JSON files in folder: {folder_path}")
    for json_file in glob.glob(os.path.join(folder_path, '*.json')):
        print(f"Processing file: {json_file}")
        try:
            with open(json_file, 'r') as file:
                try:
                    data = json.load(file)
                    print("JSON data successfully loaded")

                    content = data['choices'][0]['message']['content']
                    content = content.replace(
                        '```json\n', '').replace('\n```', '').strip()
                    print("Content extracted and cleaned")

                    try:
                        records = json.loads(content)
                        print("Content converted to JSON")

                        if isinstance(records, list):
                            all_records.extend(collect_records(records))
                            print(
                                f"Records from {json_file} added to collection")
                        elif isinstance(records, dict):
                            all_records.extend(collect_records([records]))
                            print(
                                f"Single record from {json_file} added to collection")
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

    print(f"Total records collected: {len(all_records)}")
    # Sort all records by 'memorial_number'
    sorted_records = sorted(all_records, key=lambda x: x['memorial_number'])
    print("Records sorted by memorial number")
    return sorted_records


def write_to_csv(records, csv_path):
    print(f"Writing records to CSV file: {csv_path}")
    with open(csv_path, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=[
                                'memorial_number', 'name', 'date', 'location'])
        writer.writeheader()
        writer.writerows(records)
    print("CSV file writing complete")


# Replace with actual folder path
json_folder_path = 'PATH_TO_JSON_FOLDER'
# Replace with actual file path
csv_file_path = 'PATH_TO_OUTPUT_CSV'

print("Script started")
sorted_records = process_json_files(json_folder_path)
write_to_csv(sorted_records, csv_file_path)
print("Script finished")
