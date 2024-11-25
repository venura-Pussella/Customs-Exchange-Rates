import os
from azure.storage.blob import BlobServiceClient, BlobProperties
import config
from azure.core.exceptions import ServiceRequestError, ResourceNotFoundError, ResourceExistsError
import io
import logging

class AzureBlobObjects:
    """Singleton class to hold blob-service-client and container clients. Contains methods to retrieve them, and the getListOfFilenamesInContainer(cls, containerName: str) -> list[str]:
    """

    __blob_service_client = None
    __csvstore_container_client = None
    __linkTracker_container_client = None
    __logstore_container_client = None

    containerClientToNameMapping = {
        config.csvstore_container_name: __csvstore_container_client,
        config.linkTracker_container_name: __linkTracker_container_client,
        config.logstore_container_name: __logstore_container_client
    }

    @classmethod
    def get_blob_service_client(cls):
        if cls.__blob_service_client == None:
            connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
            cls.__blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        return cls.__blob_service_client
    
    @classmethod
    def get_container_client(cls, containerName: str):
        relevantPrivateContainerClient = cls.containerClientToNameMapping[containerName]

        try:
            if relevantPrivateContainerClient == None:
                blob_service_client = cls.get_blob_service_client()
                relevantPrivateContainerClient = blob_service_client.get_container_client(container=containerName)
                if not relevantPrivateContainerClient.exists():
                    relevantPrivateContainerClient = blob_service_client.create_container(name=containerName)
        except ServiceRequestError:
            logging.error('Service Request Error. Also check if the server is connected to the internet.')

        return relevantPrivateContainerClient
    
    @classmethod
    def getListOfFilenamesInContainer(cls, containerName: str) -> list[str]:
        containerClient = cls.get_container_client(containerName)
        blobName_list = containerClient.list_blob_names()
        return list(blobName_list)
    
    @classmethod
    def getListOfBlobsInContainer(cls, containerName: str) -> list[BlobProperties]:
        containerClient = cls.get_container_client(containerName)
        blob_list = containerClient.list_blobs()
        return list(blob_list)
    
    @classmethod
    def upload_blob_file(cls, filepath: str, containerName: str):
        """Upload file specified in filepath to the specified container in Azure storage.
        """
        container_client = cls.get_container_client(containerName)
        filename = filepath.rsplit("/")[-1]
        print("filename about to be uploaded to blob: " + filename)
        with open(filepath, mode="rb") as data:
            blob_client = container_client.upload_blob(name=filename, data=data, overwrite=True)

    @classmethod
    def upload_blob_stream(cls, stream: io.BytesIO, filename: str, containerName: str):
        """Upload file specified in filepath to the specified container in Azure storage.
        """
        container_client = cls.get_container_client(containerName)
        try:
            blob_client = container_client.get_blob_client(filename)
            blob_client.upload_blob(stream, blob_type="BlockBlob")
        except ResourceExistsError as e:
            print(f'{filename} already exists, overwriting...')
            blob_client.delete_blob()
            stream.seek(0) # important
            blob_client.upload_blob(stream, blob_type="BlockBlob")


    @classmethod
    def download_blob_file(cls, filename: str, containerName: str) -> bytes:
        """Downloads the given filename from the given azure storage container and returns as bytes
        """
        container_client = cls.get_container_client(containerName)
        blob_client = container_client.get_blob_client(blob=filename)
        download_stream = blob_client.download_blob()
        return download_stream.readall()


    @classmethod
    def delete_blob_file(cls, filename: str, containerName: str):
        container_client = cls.get_container_client(containerName)
        blob_client = container_client.get_blob_client(blob=filename)
        blob_client.delete_blob()

