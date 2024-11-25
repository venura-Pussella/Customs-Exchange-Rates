import logging
import sys
import io
import config
from data_stores.AzureBlobObjects import AzureBlobObjects as abo
import os
from datetime import datetime

format_string = "[%(asctime)s: %(levelname)s: %(module)s: %(message)s]"

log_messages: list[str] = []

# make custom logging.Handler inherited class to store log messages in the log_messages list
class ListHandler(logging.Handler):

    def emit(self, record):
        log_entry = self.format(record)
        log_messages.append(log_entry)


list_handler = ListHandler()


logging.basicConfig(
    level = logging.INFO,
    format = format_string,

    handlers=[
        logging.StreamHandler(sys.stdout),    # To send logs to terminal output
        list_handler
        # logging.FileHandler(log_filepath)
    ]
)



logging.getLogger('azure').setLevel('WARNING') # otherwise Azure info logs are too numerous

def update_logs_in_AzStorage():
    """Uploads the collected logs in this run as a text file to azure storage.
    Removes old log files as specified in the env file.
    """
    log_bytes = io.BytesIO()
    for line in log_messages:
        log_bytes.write(line.encode('utf-8'))
        log_bytes.write('\n'.encode('utf-8'))
    log_bytes.seek(0)

    files = abo.getListOfBlobsInContainer(config.logstore_container_name)
    sorted_files = sorted(files, key=lambda x: x.creation_time, reverse=True)
    try: logs_to_keep_in_log_store = int(os.getenv('logs_to_keep_in_log_store'))
    except:
        logs_to_keep_in_log_store = 10
        logging.warning('logs_to_keep_in_log_store not found from env file, defaulting to 10.')
    if logs_to_keep_in_log_store > 0:
        files_to_delete = sorted_files[logs_to_keep_in_log_store-1:]
        for file in files_to_delete:
            logging.info(f'Deleting old log file {file.name}')
            abo.delete_blob_file(file.name, config.logstore_container_name)

    current_datetime = datetime.now()
    new_log_file_name = 'LOG_' + str(current_datetime.year) + str(current_datetime.month) + str(current_datetime.day) + str(current_datetime.hour) + str(current_datetime.minute) + str(current_datetime.second) + '.' + 'txt'
    abo.upload_blob_stream(log_bytes, new_log_file_name, config.logstore_container_name)
