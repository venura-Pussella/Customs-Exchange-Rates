import os
from data_stores.AzureBlobObjects import AzureBlobObjects as abo
from azure.core.exceptions import ResourceNotFoundError
import io
import logging

def get_processed_links() -> set:
    try: file = abo.download_blob_file('processed_links.csv',os.getenv('link_tracker_store'))
    except ResourceNotFoundError:
        logging.warning('Warning: link tracker file not found')
        return set()
    all_text = file.decode('utf-8')
    all_text.replace('\r','') # we don't like carriage returns
    lines = all_text.rsplit('\n')
    return set(lines)

def update_processed_links(links: set):
    text = ''
    for item in links:
        text += item
        text += '\n'
    byte_data = text.encode('utf-8')
    byte_stream = io.BytesIO(byte_data)
    abo.upload_blob_stream(byte_stream,'processed_links.csv',os.getenv('link_tracker_store'))