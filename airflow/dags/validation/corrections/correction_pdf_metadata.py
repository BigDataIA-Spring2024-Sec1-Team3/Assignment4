import pandas as pd
import numpy as np
from utils.model_pdf_metadata import PDFMetadataClass
import re
import csv
import roman
from pydantic import ValidationError

def metadata_validate_data(file_path, model):
    temp = []
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            attempts = 0
            while attempts < 5:
                try:
                    # Attempt to create a model instance
                    model_instance = model(**row)
                    temp.append(model_instance.model_dump())
                    break
                except Exception as e:
                    # Handle validation errors and attempt corrections
                    for error in e.errors():
                        column_name = error['loc'][0]
                        if column_name in row:
                            row[column_name] = None
                    attempts += 1
            else:
                # If all attempts fail, append the row with None values
                temp.append(row)
    return temp

def metadata_clean_csv_generate():
    file_path = 'data/input/csv-input-files/pdf_metadata.csv'
    list_dict = metadata_validate_data(file_path, PDFMetadataClass)
    df_clean = pd.DataFrame(list_dict)
    clean_csv_location = 'data/output/clean_pdf_metadata.csv'
    df_clean.to_csv(clean_csv_location, header=True, index=False, sep="|", float_format='%d')
    print("Clean CSV file generated successfully.")

if __name__ == '__main__':
    metadata_clean_csv_generate()