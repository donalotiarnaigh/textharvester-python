# This script will attempt to extract names dates and locations for each memorial_number

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


def process_images(image_paths, api_key, output_directory, batch_number):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "You're an expert in OCR and are working in a heritage/genealogy context assisting in data processing post graveyard survey.Examine these images and extract the names,dates and suspected location names for each memorial number-no other fields..Respond in json format only.e.g {memorial_number: 69, name: John Doe, date: Jan 1, 1800, location: Springfield}. If no memorial number,name, date or location is visible in an image,return a json with NULL in each field"
                }
            ]
        }
    ]

    for image_path in image_paths:
        base64_image = encode_image(image_path)
        messages[0]["content"].append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
        })

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": messages,
        "max_tokens": 1500  # Adjust based on requirements and token limits
    }

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()

        # Handle response for each image separately if needed
        # For simplicity, saving one combined output file for the batch
        output_file_name = f"output_batch_{batch_number}.json"
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
    image_files = glob.glob(os.path.join(folder_path, '*.jpg'))
    batch_size = 3

    for i in range(0, len(image_files), batch_size):
        batch = image_files[i:i + batch_size]
        batch_number = i // batch_size + 1
        print(f"Processing batch {batch_number}...")
        process_images(batch, api_key, output_directory, batch_number)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_folder>")
        sys.exit(1)

    folder_path = sys.argv[1]
    api_key = os.getenv('OPENAI_API_KEY')
    # Change to your output directory path
    output_directory = "PATH_TO_OUTPUT_JSONS_FOLDER"
    main(folder_path, api_key, output_directory)

# To run this script, type 'python3 vision-v4.py {{path/to/input/folder}}' in terminal
