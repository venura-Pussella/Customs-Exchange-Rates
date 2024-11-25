from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv()) # read local .env file
import os
import src.webscrape as webscrape
from src.get_table_image import get_table_image_from_pdfbytesio
from src.exceptions import TableImageException, DocIntelligenceCouldNotFindTableException
from src.ocr import extract_text_from_image
from src.output import upload_csvstring_to_blob, upload_csvstring_to_cosmos
from src.link_tracker import update_processed_links, get_processed_links
import logging # for use in Azure functions environment (replace all calls to logger object with python logging class)
from src import logHandling
from src.logHandling import log_messages, update_logs_in_AzStorage

def process_link(name,pdf_link):
        
    # download the PDF
    pdf_bytesio = webscrape.download_pdf_as_bytesio(pdf_link)

    # get the table image from the PDF
    try: image_bytes,_  = get_table_image_from_pdfbytesio(pdf_bytesio)
    except TableImageException as e:
        logging.error('Table image exception:')
        logging.error(e)
        logging.error(f'\033[31m{name} NOK!\033[0m')
        return
    
    # get the table data using OCR
    try: csv_string = extract_text_from_image(image_bytes)
    except DocIntelligenceCouldNotFindTableException: 
        logging.error('Azure document intelligence could not find a table')
        logging.error(f'\033[31m{name} NOK!\033[0m')
        return
    
    # upload the table data as a csv
    upload_csvstring_to_blob(csv_string,f'{name}.csv')
    logging.info('Creating items in cosmos')
    upload_csvstring_to_cosmos(csv_string, name)
    

def main():
    # collect links
    check_older_pages_when_webscraping = os.getenv('check_older_pages_when_webscraping')
    if check_older_pages_when_webscraping == 'True':
        check_older_pages_when_webscraping = True
    else: check_older_pages_when_webscraping = False
    logging.info(f'Check_older_pages_when_webscraping set to {check_older_pages_when_webscraping}')
    logging.info('Getting processed links.')
    processed_links = get_processed_links()
    logging.info('Getting new links')
    new_links = webscrape.collect_new_links(check_older_pages_when_webscraping)

    # process each link
    for name,pdf_link in new_links:
        logging.info(f'Processing {name}')
        process_link(name,pdf_link)   
        processed_links.add(f'{name},{pdf_link}') 
        update_processed_links(processed_links)   

    update_logs_in_AzStorage() 

try: main()
except Exception as e:
    logging.error('Main function crashed! :')
    logging.error(e)
    update_logs_in_AzStorage() 

