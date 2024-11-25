from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult, AnalyzeDocumentRequest
import os
from src.exceptions import DocIntelligenceCouldNotFindTableException

def extract_text_from_image(image: bytes) -> str:
    """OCRs a csv string from the image.

    Args:
        image (bytes): Image of the table

    Raises:
        DocIntelligenceCouldNotFindTableException: raised if azure document intelligence could not detect a table

    Returns:
        str: csv string
    """
    document_intelligence_client = DocumentIntelligenceClient(
        endpoint=os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT'), credential=AzureKeyCredential(os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY'))
    )

    poller = document_intelligence_client.begin_analyze_document(
        "prebuilt-layout", AnalyzeDocumentRequest(bytes_source=image
    ))

    result: AnalyzeResult = poller.result()

    if not result.tables: raise DocIntelligenceCouldNotFindTableException

    tables = result.tables

    if len(tables) == 0: raise DocIntelligenceCouldNotFindTableException

    if len(tables) > 1:
        # LOG WARNING
        pass
    
    csv_string = ''
    cells = tables[0].cells
    for i in range (0,len(cells)):
        cell = cells[i]
        current_row = cell.row_index
        content = cell.content
        content = content.replace(',','') # some currency codes 
        csv_string += content
        next_index = i + 1
        if next_index == len(cells):
            csv_string += '\n'
        elif cells[next_index].row_index > current_row:
            csv_string += '\n'
        else:
            csv_string += ','
        
        

    return csv_string