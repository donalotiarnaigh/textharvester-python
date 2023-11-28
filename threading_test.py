import os
import json
import base64
import requests
import sys
import csv
import glob
import logging
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import time

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


def send_request_with_retry(payload, headers, max_retries=5):
    retry_delay = 1  # Initial delay of 1 second
    for attempt in range(max_retries):
        try:
            response = requests.post("https://api.openai.com/v1/chat/completions",
                                     headers=headers, json=payload)
            response.raise_for_status()

            # Log rate limit info
            logging.info(f"Rate Limit Info: {response.headers}")

            return response
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 429:
                # Extract rate limit information from response headers
                rate_limit_requests = err.response.headers.get(
                    'x-ratelimit-limit-requests')
                remaining_requests = err.response.headers.get(
                    'x-ratelimit-remaining-requests')
                rate_limit_reset_requests = err.response.headers.get(
                    'x-ratelimit-reset-requests')
                rate_limit_tokens = err.response.headers.get(
                    'x-ratelimit-limit-tokens')
                remaining_tokens = err.response.headers.get(
                    'x-ratelimit-remaining-tokens')
                rate_limit_reset_tokens = err.response.headers.get(
                    'x-ratelimit-reset-tokens')

                logging.warning(
                    f"Rate limited. Requests remaining: {remaining_requests}, Reset in: {rate_limit_reset_requests}")
                logging.warning(
                    f"Rate limited. Tokens remaining: {remaining_tokens}, Reset in: {rate_limit_reset_tokens}")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                raise
    raise Exception("Max retries reached")


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
                    "text": "You're an expert in OCR and are working in a heritage/genealogy context assisting in data processing post graveyard survey.Examine these images and extract the names,dates and suspected location names for each memorial number-no other fields..Respond in JSON format only.e.g {memorial_number: 69, name: John Doe, date: Jan 1, 1800, location: Springfield}. If no memorial number,name, date or location is visible in an image,return a json with NULL in each field"
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
        response = send_request_with_retry(payload, headers)

        # Extract and log rate limit information from response headers
        rate_limit_requests = response.headers.get(
            'x-ratelimit-limit-requests')
        remaining_requests = response.headers.get(
            'x-ratelimit-remaining-requests')
        rate_limit_reset_requests = response.headers.get(
            'x-ratelimit-reset-requests')
        rate_limit_tokens = response.headers.get('x-ratelimit-limit-tokens')
        remaining_tokens = response.headers.get('x-ratelimit-remaining-tokens')
        rate_limit_reset_tokens = response.headers.get(
            'x-ratelimit-reset-tokens')

        logging.info(
            f"Rate Limit (Requests): {rate_limit_requests}, Remaining: {remaining_requests}, Reset in: {rate_limit_reset_requests}")
        logging.info(
            f"Rate Limit (Tokens): {rate_limit_tokens}, Remaining: {remaining_tokens}, Reset in: {rate_limit_reset_tokens}")

        logging.info("Received response from OpenAI, writing to file...")
        output_file_name = f"output_batch_{batch_number}.json"
        output_path = os.path.join(output_directory, output_file_name)

        with open(output_path, "w") as json_file:
            json.dump(response.json(), json_file, indent=4)

        logging.info(f"Output saved to {output_path}")
        return response.json()

    except Exception as e:
        logging.error(f"Error during API request: {e}")


def process_batch(batch_data):
    image_paths, api_key, output_directory, batch_number = batch_data
    process_images(image_paths, api_key, output_directory, batch_number)


def main(folder_path, api_key, output_directory):
    logging.info(f"Searching for image files in {folder_path}...")
    image_files = glob.glob(os.path.join(folder_path, '*.jpg'))
    image_files.sort()

    # Adaptive batch size based on token limit
    token_limit_per_request = 4000
    token_rate_limit_per_minute = 10000
    max_batch_size = token_rate_limit_per_minute // token_limit_per_request

    # Limit the number of concurrent threads
    thread_pool_size = 2  # Adjust based on rate limits

    batches = [(image_files[i:i + max_batch_size], api_key, output_directory, i // max_batch_size + 1)
               for i in range(0, len(image_files), max_batch_size)]

    total_batches = len(batches)

    with ThreadPoolExecutor(max_workers=thread_pool_size) as executor:
        list(tqdm(executor.map(process_batch, batches),
             total=total_batches, desc="Processing Batches"))


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

    # Ensure to update this path to an existing directory
    output_directory = "/Users/danieltierney/Desktop/WebDev/openai-playground/HG_TextHarvest_v1/test_folder/json_outputs"
    logging.info("Starting the image processing script...")
    main(folder_path, api_key, output_directory)
    logging.info("Script finished")

# To run this script, type 'python3 vision_ndl.py PATH/TO/INPUT/FOLDER' in the terminal
