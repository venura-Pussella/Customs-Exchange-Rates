class TableImageException(Exception):
    """Raised if PDF has no pages or the page has no image, so we can't extract the table image.

    Args:
        Can pass in a string message.
    """
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class DocIntelligenceCouldNotFindTableException(Exception):
    """Raised Azure document intelligence could not find a table in the image

    Args:
        Can pass in a string message.
    """
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)