import os
import json
import base64
import requests
import sys
import csv
import glob
import logging

# Configure logging
logging.basicConfig(filename='vision_ndl.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s:%(message)s')


def encode_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            logging.info(f"Encoding image: {image_path}")
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        logging.error(f"File not found: {image_path}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error encoding image {image_path}: {e}")
        sys.exit(1)


def process_images(image_paths, api_key, output_directory, batch_number):
    logging.info(f"Processing images in batch {batch_number}")
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
                    "text": "You're an expert in OCR and are working in a heritage/genealogy context assisting in data processing post graveyard survey..."
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

    logging.info("Sending request to OpenAI...")
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()

        logging.info("Received response from OpenAI, writing to file...")
        output_file_name = f"output_batch_{batch_number}.json"
        output_path = os.path.join(output_directory, output_file_name)

        with open(output_path, "w") as json_file:
            json.dump(response.json(), json_file, indent=4)

        logging.info(f"Output saved to {output_path}")
        return response.json()

    except requests.exceptions.HTTPError as err:
        logging.error(f"HTTP Error during API request: {err}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Request Exception during API request: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")


def main(folder_path, api_key, output_directory):
    logging.info(f"Searching for image files in {folder_path}...")
    image_files = glob.glob(os.path.join(folder_path, '*.jpg'))
    batch_size = 3

    if not image_files:
        logging.error("No JPG files found in the specified directory.")
        return

    for i in range(0, len(image_files), batch_size):
        batch = image_files[i:i + batch_size]
        batch_number = i // batch_size + 1
        logging.info(f"Processing batch {batch_number}...")
        process_images(batch, api_key, output_directory, batch_number)


if __name__ == "__main__":
    logging.info("Script started")
    if len(sys.argv) != 2:
        logging.error("Usage: python script.py <path_to_folder>")
        sys.exit(1)

    folder_path = sys.argv[1]
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        logging.error("OPENAI_API_KEY not set.")
        sys.exit(1)

    output_directory = "PATH_TO_OUTPUT_FOLDER"
    logging.info("Starting the image processing script...")
    main(folder_path, api_key, output_directory)
    logging.info("Script finished")

# To run this script, type 'python3 vision_ndl.py PATH/TO/INPUT/FOLDER' in the terminal
