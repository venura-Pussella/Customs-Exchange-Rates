import io
from data_stores.AzureBlobObjects import AzureBlobObjects as abo
from data_stores.CosmosObjects import CosmosObjects as co
import config
import os
import logging
import uuid
import concurrent.futures
from datetime import datetime

def upload_csvstring_to_blob(csv_string: str, filename: str):
    """Uploads a csv string to Azure blob as a file. 
    Considers the specified number of csvs_to_keep_in_csv_store in environment variables and 
    deletes excess files if required.

    Args:
        csv_string (str): _description_
        filename (str): _description_
    """
    print(f'Attempting to upload csv with filename {filename}')
    csv_bytes = io.BytesIO()
    csv_bytes.write(csv_string.encode('utf-8'))
    csv_bytes.seek(0)

    files = abo.getListOfBlobsInContainer(config.csvstore_container_name)
    sorted_files = sorted(files, key=lambda x: x.creation_time, reverse=True)
    try: csvs_to_keep_in_csv_store = int(os.getenv('csvs_to_keep_in_csv_store'))
    except:
        csvs_to_keep_in_csv_store = 10
        logging.warning('Cannot get csvs_to_keep_in_csv_store from env file. Defaulting to 10.')
    if csvs_to_keep_in_csv_store > 0:
        files_to_delete = sorted_files[csvs_to_keep_in_csv_store-1:]
        for file in files_to_delete:
            logging.info(f'Deleting old CSV file {file.name}')
            abo.delete_blob_file(file.name, config.csvstore_container_name)

    abo.upload_blob_stream(csv_bytes, filename, config.csvstore_container_name)

def __convert_csvstring_to_list_of_dict(csv_string: str, link_name: str):
    all_records_as_dicts: list[dict] = []

    records_as_string = csv_string.rsplit('\n')
    records_as_string = records_as_string[1:] # skip header row
    for record_as_string in records_as_string:
        items = record_as_string.rsplit(',')
        dictionary = None
        try:
            if len(items) == 6:
                dictionary = {
                    'id': str(uuid.uuid4()),
                    'Extracted datetime': datetime.now().strftime("%Y/%m/%d, %H:%M:%S"),
                    'Extracted link name': link_name,
                    '#': items[0],
                    'Country': items[1],
                    'Country Code': items[2],
                    'Currency': items[3],
                    'Currency Code': items[4],
                    'Rate of Exchange (Rs.)': float(items[5])
                }
            elif len(items) == 5: # high chance the row number column and country column have merged
                dictionary = {
                    'id': str(uuid.uuid4()),
                    'Extracted datetime': datetime.now().strftime("%Y/%m/%d, %H:%M:%S"),
                    'Country': items[0],
                    'Country Code': items[1],
                    'Currency': items[2],
                    'Currency Code': items[3],
                    'Rate of Exchange (Rs.)': float(items[4])
                }
            else:
                if record_as_string != '': # if condition otherwise the warning will be logged for the last line which is blank
                    logging.warning(f'A CSV line has been skipped: {record_as_string}')
            
            if dictionary: all_records_as_dicts.append(dictionary)
        except ValueError:
            logging.warning(f'ValueError raised. Most likely exchange rate could not be converted to a float. Line: {record_as_string}')

    return all_records_as_dicts

def upload_csvstring_to_cosmos(csv_string: str, link_name: str):
    all_records_as_dicts = __convert_csvstring_to_list_of_dict(csv_string, link_name)

    # calling these so that the items gets cached in the CosmosObjects singleton class (before they get called multiple times at once in the below concurrent futures)
    co.getCosmosClient()
    co.getCosmosDatabase()
    co.getCosmosContainer() 

    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     futures = []
    #     for record_dict in all_records_as_dicts:
    #         futures.append(executor.submit(co.create_item_in_cosmos_container, record_dict))
    #     concurrent.futures.wait(futures)

    for record_dict in all_records_as_dicts:
        co.create_item_in_cosmos_container(record_dict)
