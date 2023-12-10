import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError

# Define the JSON schema
schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            # Allows integers or null
            "memorial_number": {"type": ["integer", "null"]},
            # Allows strings or null
            "inscription": {"type": ["string", "null"]},
        },
        "required": ["memorial_number", "inscription"]
    }
}


def validate_json(json_data, schema):
    try:
        validate(instance=json_data, schema=schema)
        print("Validation successful.")
    except ValidationError as ve:
        print("Validation error:", ve)
        return False
    return True


def extract_json_content(file_data):
    try:
        # Extract the JSON array from the nested structure
        content = file_data['choices'][0]['message']['content']
        content = content.replace('```json\n', '').replace('\n```', '').strip()
        return json.loads(content)
    except (KeyError, json.JSONDecodeError) as e:
        print(f"Error extracting JSON content: {e}")
        return None


def main(json_file_path):
    try:
        with open(json_file_path, 'r') as file:
            file_data = json.load(file)
            json_data = extract_json_content(file_data)
            if json_data is not None and validate_json(json_data, schema):
                print(
                    f"JSON file {json_file_path} is valid according to the schema.")
            else:
                print(
                    f"JSON file {json_file_path} is not valid according to the schema.")
    except FileNotFoundError:
        print(f"File not found: {json_file_path}")
    except json.JSONDecodeError as e:
        print(f"Error reading JSON file: {e}")


if __name__ == "__main__":
    # Replace with the path to your JSON file
    json_file_path = 'PATH_TO_YOUR_JSON_FILE'
    main(json_file_path)
