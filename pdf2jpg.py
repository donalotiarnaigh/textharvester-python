from PyPDF2 import PdfReader
from pdf2image import convert_from_path
import os


def convert_pdf_to_jpg(pdf_path, output_folder):
    # Create a folder to store the images
    os.makedirs(output_folder, exist_ok=True)

    # Read the PDF
    reader = PdfReader(pdf_path)
    num_pages = len(reader.pages)

    # Convert each page to an image (JPEG)
    for i in range(num_pages):
        images = convert_from_path(pdf_path, first_page=i+1, last_page=i+1)
        img_path = f'{output_folder}/page_{i+1}.jpg'
        images[0].save(img_path, 'JPEG')
        print(f'Page {i+1} saved as {img_path}')


if __name__ == '__main__':
    # Path to the PDF file
    pdf_path = 'PATH_TO_PDF'
    # Output folder path
    output_folder = 'PATH_TO_OUTPUT_FOLDER'

    convert_pdf_to_jpg(pdf_path, output_folder)
