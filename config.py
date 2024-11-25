import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv()) # read local .env file

csvstore_container_name = os.getenv("csv_store")
linkTracker_container_name = os.getenv("link_tracker_store")
logstore_container_name = os.getenv("log_store")

cosmosNoSQLDBName = os.getenv("Cosmos_db_name")
cosmosNoSQLContainerName = os.getenv("Cosmsos_container_name")
