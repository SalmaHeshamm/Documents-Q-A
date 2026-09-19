from enum import Enum

class ResponseSignal(Enum):

    FILE_TYPE_NOT_SUPPORTED = "File type not supported"
    FILE_SIZE_EXCEEDED = "File size exceeded"
    FILE_UPLOAD_SUCCESS = "File uploaded successfully"
    FILE_UPLOAD_FAILED = "File upload failed"
    FILE_VALIDATION_SUCCESS = "File validation successful"
    FILE_VALIDATION_FAILED = "File validation failed"
    FILE_PROCESSING_FAILED = "File processing failed"
    FILE_PROCESSING_SUCCESS = "File processing successful"
    NO_FILES_FOUND_FOR_PROCESSING = "No files found for processing"
    FILE_NOT_FOUND = "File not found"
    PROJECT_NOT_FOUND = "Project not found"
    INSERT_INTO_VECTOR_DB_FAILED = "Failed to insert into vector database"
    INSERT_INTO_VECTOR_DB_SUCCESS = "Successfully inserted into vector database"
    VECTOR_DB_COLLECTION_RETRIEVED = "Vector database collection retrieved successfully"
    QUERY_VECTOR_DB_FAILED = "Failed to query vector database"
    QUERY_VECTOR_DB_SUCCESS = "Successfully queried vector database"
