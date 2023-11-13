import os
import json
import base64
import requests
import sys
import csv
import glob


def encode_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: The file '{image_path}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


def append_to_csv(records, csv_path):
    # Check if the file exists to write headers accordingly
    file_exists = os.path.isfile(csv_path)

    with open(csv_path, 'a', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=[
                                'memorial_number', 'name', 'date', 'location'])

        if not file_exists:
            writer.writeheader()

        for record in records:
            writer.writerow(record)


def process_image(image_path, api_key, output_directory):
    base64_image = encode_image(image_path)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "You're an expert in OCR and are working in a heritage/genealogy context assisting in data processing post graveyard survey. Examine this image and extract the names, dates and suspected location names for each memorial number - no other fields.. Respond in json format only. e.g {memorial_number: 69, name: John Doe, date: Jan 1, 1800, location: Springfield}. If no memorial number, name, date or location is visible in an image, return a json with NULL in each field"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 500
    }

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()

        # Unique JSON file for each image
        output_file_name = f"output_{os.path.basename(image_path).split('.')[0]}.json"
        output_path = os.path.join(output_directory, output_file_name)

        with open(output_path, "w") as json_file:
            json.dump(response.json(), json_file, indent=4)

        print(f"Output saved to {output_path}")
        return response.json()

    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error occurred: {err}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error during requests to OpenAI: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def main(folder_path, api_key, output_directory):
    # List all jpg images in the folder
    for image_file in glob.glob(os.path.join(folder_path, '*.jpg')):
        print(f"Processing {image_file}...")
        process_image(image_file, api_key, output_directory)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_folder>")
        sys.exit(1)

    folder_path = sys.argv[1]
    api_key = os.getenv('OPENAI_API_KEY')
    # Change to your output directory path
    output_directory = "PATH_TO_OUTPUT_JSON_FOLDER"
    main(folder_path, api_key, output_directory)


# To run this script, type 'python3 vision-v3.py {{path/to/input/folder}}' in terminal
