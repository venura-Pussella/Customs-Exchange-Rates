#### Python Version
3.11

#### Additional config
After installing requirements.txt, need to run the command "playwright install chromium"

#### Environmental Variables
- check_older_pages_when_webscraping = True - If not true, program will only read the links on the first page of the customs exchange rates website. This is desirable once all the links have been scraped and we are only waiting for the weekly update.
- csv_store = "" - Azure storage container name to store the extracted tables as CSVs
- link_tracker_store = "" - Azure storage container name holding the processed_links.csv tracker file.
- log_store = "" - Azure storage container name holding log files stored after each program run.
- csvs_to_keep_in_csv_store = - Enter a number here, eg: 2 will hold the 2 most recent extracted CSVs. Enter -1 to not enforce a limit.
- logs_to_keep_in_log_store = - Enter a number here, eg: 2 will hold the 2 most recent logs. Enter -1 to not enforce a limit.
- AZURE_STORAGE_CONNECTION_STRING
- AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT
- AZURE_DOCUMENT_INTELLIGENCE_KEY
- COSMOS_ENDPOINT
- COSMOS_KEY
- Cosmos_db_name
- Cosmsos_container_name