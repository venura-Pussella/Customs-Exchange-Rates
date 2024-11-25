import fitz # pymupdf
import io
import os
from src.exceptions import TableImageException

def get_table_image_from_pdfbytesio(pdf_bytesio: io.BytesIO) -> tuple[bytes,str]:
    """Gets image of the table from the PDF.
    Image is expected to be in page 1 of 1 page PDFs and page 2 of other PDFs.
    If more than 1 image is found, largest image is taken.

    Args:
        pdf_bytesio (io.BytesIO): PDF as BytesIO

    Raises:
        TableImageException: If cannot extract table image due to PDF having no pages or images in the target page.

    Returns:
        tuple[bytes,str]: tuple of bytes representing the image, and its extension without the dot(eg: jpeg, not .jpeg)
    """

    fitz_file = fitz.open("pdf", pdf_bytesio)

    # if PDF has 1 page, search that page, else search 2nd page
    if fitz_file.page_count >= 2:
        interested_page_index = 1
    elif fitz_file.page_count == 1:
        interested_page_index = 0
    else:
        raise TableImageException('PDF file has no pages!')
    page = fitz_file.load_page(interested_page_index) 

    # get images from the target page
    image_list = page.get_images(full=True) 
    if len(image_list) == 0: raise TableImageException('Found no image in PDF target page.')

    # we will assume the largest page in the PDF is the image of the table
    largest_image_size = 0
    for image in image_list:

        image_ref = image[0] # XREF
        base_image = fitz_file.extract_image(image_ref)
        image_size = base_image["height"] * base_image["width"]
        if image_size > largest_image_size:
            largest_image_size = image_size
            image_bytes: bytes = base_image["image"]
            image_ext = base_image["ext"]

    return (image_bytes,image_ext)

