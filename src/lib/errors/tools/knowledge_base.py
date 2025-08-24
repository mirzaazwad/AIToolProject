"""
Knowledge base tool specific exceptions.
"""


class RetrievalError(Exception):
    """Exception raised for errors in the retrieval process."""

    def __init__(self, message="Error retrieving data from knowledge base"):
        self.message = message
        super().__init__(self.message)


class QueryError(Exception):
    """Exception raised for errors in the query process."""

    def __init__(self, message="Error querying knowledge base"):
        self.message = message
        super().__init__(self.message)


class InsertionError(Exception):
    """Exception raised for errors in the insertion process."""

    def __init__(self, message="Error inserting data into knowledge base"):
        self.message = message
        super().__init__(self.message)


class LoadingError(Exception):
    """Exception raised for errors in the loading process."""

    def __init__(self, message="Error loading knowledge base"):
        self.message = message
        super().__init__(self.message)
