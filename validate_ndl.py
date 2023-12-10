import json
from jsonschema import validate, ValidationError

# Define the schema
schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "memorial_number": {"type": ["integer", "null"]},
            "name": {"type": ["string", "null"]},
            "date": {"type": ["string", "null"]},
            "location": {"type": ["string", "null"]}
        },
        "required": ["memorial_number", "name", "date", "location"]
    }
}

# Load and validate the JSON file


def validate_json(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            content = data['choices'][0]['message']['content']
            # Remove markdown code block syntax if present
            content = content.replace(
                '```json\n', '').replace('\n```', '').strip()
            records = json.loads(content)
            validate(instance=records, schema=schema)
            print(f"JSON file {file_path} is valid according to the schema.")
    except ValidationError as e:
        print(f"Validation error in file {file_path}: {e.message}")
        print("JSON file is not valid according to the schema.")
    except json.JSONDecodeError as e:
        print(f"JSON parsing error in file {file_path}: {e}")
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Unexpected error occurred in file {file_path}: {e}")


# Path to the JSON file
file_path = 'PATH_TO_YOUR_JSON_FILE'

# Call the validation function
validate_json(file_path)
