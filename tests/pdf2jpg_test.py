import pytest
import os
# Update this line with the correct module name
from pdf2jpg import convert_pdf_to_jpg


@pytest.fixture
def setup_pdf_and_output():
    # Setup a test PDF path and output folder
    # Ensure you have a test PDF at this location
    pdf_path = 'PATH_TO_PDF'
    output_folder = 'PATH_TO_OUTPUT_FOLDER'
    yield pdf_path, output_folder
    # Teardown after tests
    if os.path.exists(output_folder):
        for f in os.listdir(output_folder):
            os.remove(os.path.join(output_folder, f))
        os.rmdir(output_folder)


def test_convert_pdf_to_jpg(setup_pdf_and_output):
    pdf_path, output_folder = setup_pdf_and_output
    convert_pdf_to_jpg(pdf_path, output_folder)

    # Add your test assertions here

# Additional test functions can be added here
