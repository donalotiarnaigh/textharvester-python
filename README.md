# User Guide for HG TextHarvester

## Introduction

HG TextHarvester is a basic toolkit designed for digitizing and extracting textual data from historic graves' documents. This guide provides step-by-step instructions on how to use HG TextHarvester to convert PDFs to images, perform OCR (Optical Character Recognition) to extract text, and compile the data into CSV files for easy analysis and record-keeping.

## System Requirements

- Python 3.x
- Required Libraries: `PIL`, `requests`, `csv`, `glob`, `os`, `json`, `base64`
- OpenAI API Key (for OCR)

## Setup

1. **Install Python**: Ensure Python 3.x is installed on your system.
2. **Install Libraries**: Install necessary Python libraries using pip:

```
pip install pillow requests csv glob json base64

```

3. **API Key**: Set your OpenAI API key as an environment variable:

- On Windows: `set OPENAI_API_KEY=your_api_key`
- On Unix/Mac: `export OPENAI_API_KEY=your_api_key`

API key can be requested from dtcurragh if not already provided.

## Usage

HG TextHarvester comprises three main scripts:

1. **PDF to JPG Conversion (`pdf2jpg.py`)**:

- Converts each page of a PDF document into separate JPG images.
- Usage: open `pdf2jpg.py` in vscode, replace filepath placeholders with actual filepaths within the scripts. Save the file and run the script using the `run` button in vscode or `python pdf2jpg.py`

2. **OCR and Text Categorization (`vision-v3.py`)**:

- Processes JPG images using OCR to extract text.
- Saves OCR results in JSON format.
- Usage: type `python vision-v3.py <input_folder_path>` in your temrinal before pressing enter. Monitor the progress in the terminal, looking out for error codes returned by openai

3. **JSON to CSV Conversion (`json2csv-v2.py`)**:

- Parses JSON files to extract data.
- Compiles data into a CSV file.
- Usage: `json2csv-v2.py` in vscode, replace filepath placeholders with actual filepaths within the scripts. Save the file and run the script using the `run` button in vscode or `python json2csv-v2.py`

## Workflow

1. **Prepare your PDFs**: Place your PDFs in an accessible folder.
2. **Convert PDFs to JPGs**: Run `pdf2jpg.py` for each PDF.
3. **Process Images with OCR**: Run `vision-v3.py` on the folder containing JPGs.
4. **Compile Data to CSV**: Run `json2csv-v2.py` to collate all OCR data into a CSV file.

## Troubleshooting

- **API Limitations**: If you hit API rate limits, try processing in smaller batches.
- **Data Quality**: For best OCR results, ensure images are clear and well-lit. Block capitals preferred for handwriting
- **Error Handling**: If scripts encounter errors, check the console output for specific error messages.
