from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import GrobidParser
import csv
from typing import List, Optional, Tuple, Any, Union
import re
import ast
from pydantic import BaseModel, validator

# Define the loader using GenericLoader
loader = GenericLoader.from_filesystem(
    "data/input/grobid-files",
    glob="*",
    suffixes=[".pdf"],
    parser=GrobidParser(segment_sentences=False),
)

# Load documents
docs = loader.load()

# Extract metadata from docs
metadata_list = [doc.metadata for doc in docs]

# Define the fields for the CSV file
fields = ['text', 'para', 'bboxes', 'pages', 'section_title', 'section_number', 'paper_title', 'file_path']

# Define the file path for the output CSV file
file_path = 'data/input/csv-input-files/pdf_metadata.csv'

# Write metadata to CSV file
with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fields)
    
    # Write header
    writer.writeheader()
    
    # Write metadata for each document
    for metadata in metadata_list:
        writer.writerow(metadata)

print("Metadata written to:", file_path)
 
class PDFMetadataClass(BaseModel):
    text: str
    para: int
    bboxes: List[List[dict]]
    pages: str
    section_title: str
    section_number: Optional[float]
    paper_title: Optional[Union[str, float]]
    file_path: str
 
    @validator("text")
    def validate_text(cls, value):
        if value is None or not isinstance(value, str):
            raise ValueError("Text must not be null and should be a string.")
        return value
 
    @validator("para")
    def validate_para(cls, value):
        if not str(value).isdigit():
            raise ValueError("Para must only be integers and not contain anything else.")
        return value
 
    @validator("bboxes", pre=True, always=True)
    def convert_and_validate_bboxes(cls, value: Any):
        if isinstance(value, str):
            try:
                # Convert string to list of lists of dictionaries
                bboxes_list = ast.literal_eval(value)
                if not isinstance(bboxes_list, list):
                    raise ValueError("Invalid format for bboxes.")
                return bboxes_list
            except (ValueError, SyntaxError):
                raise ValueError("Invalid format for bboxes.")
        return value
    
    @validator("pages")
    def validate_pages(cls, value):
        if not isinstance(ast.literal_eval(value), tuple):
            raise ValueError("Pages should be a tuple containing exactly two string values.")
        return value
 
    @validator("section_number")
    def validate_section_number(cls, value):
        if value is not None and not isinstance(value, (int, float)):
            raise ValueError("Section number must be a valid number.")
        return value
 
    @validator("paper_title")
    def validate_paper_title(cls, value):
        if value is not None and not isinstance(value, (str, float)):
            raise ValueError("Paper title can be either text, a number, or null.")
        return value
 
    @validator("file_path")
    def validate_file_path(cls, value):
        expected_prefix = 'data/input/'
        if not value.startswith(expected_prefix):
            raise ValueError(f"File path must start with '{expected_prefix}'")
        
        # Additional pattern check
        pattern = re.compile(r'^20[1-4][0-9]-(l[1-3])-topics-combined-\d+\.pdf$')
        if not pattern.match(value[len(expected_prefix):]):
            raise ValueError("File name must match the specified format.")
        
        return value
 