import pandas as pd
import numpy as np
from utils.model_pdf_content import PDFContentClass
import re
import csv
import roman
from pydantic import ValidationError

def correct_topic_value(error_raised, topic_name):
    if error_raised=="Topic cannot be None or Empty":
        return topic_name
    if error_raised=="Topic name cannot start with a number or special character.":
        pattern = r'^[\d\W_]+'
        # Use re.sub to replace the matched pattern with an empty string
        stripped_topic_name = re.sub(pattern, '', topic_name)
        return stripped_topic_name
    if error_raised=="Invalid topic.":
        return
    
def correct_title_value(error_raised, title):
    if error_raised=="Title cannot be None or Empty":
        return title
    if error_raised=="Title name cannot start with a number or special character.":
        pattern = r'^[\d\W_]+'
        # Use re.sub to replace the matched pattern with an empty string
        stripped_title_name = re.sub(pattern, '', title)
        return stripped_title_name
    if error_raised=="Invalid title.":
        return

def correct_level(level):
    try:
        return roman.toRoman(level)
    except roman.InvalidRomanNumeralError:
        return level
    
def correct_learning_outcome(error_raised, learning_outcome):
    if error_raised == "Learning Outcome cannot be None or Empty":
        return learning_outcome

def content_validate_data(file_path, model):
    temp= []
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        # Assuming the delimiter is a comma, adjust if necessary
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                attempts=0
                while attempts<5:
                    try:
                        # passing the row to pydantic validation model
                        model_instance = model(**row)
                        
                        temp.append(model_instance.model_dump())
                        break
                    # if row couldn't bypass validation, we will try to correct the data based on the error raised
                    except Exception as e:
                        for error in e.errors():
                            column_name = error['loc'][0]
                            error_raised = error['msg']
                            if column_name=="topic_name":
                                modified_value=correct_topic_value(error_raised, row[column_name])
                                if not modified_value:
                                    break   
                            if column_name=="title":
                                modified_value=correct_title_value(error_raised, row[column_name])
                                if not modified_value:
                                    break
                            if column_name=="year":
                                row[column_name] = None
                            if column_name=="level":
                                row[column_name] = correct_level(row[column_name].strip())
                            if column_name == "learning_outcome":
                                modified_value = correct_learning_outcome(error_raised, row[column_name])
                                if not modified_value:
                                    break
                        attempts+=1
            except KeyError as e:
                print(f"Error processing row: {e}")
            except ValidationError as e:
                print(f"Validation error: {e}")

    return temp

def content_clean_csv_generate():
    file_path = 'data/input/csv-input-files/pdf_content.csv'
    list_dict = content_validate_data(file_path, PDFContentClass)
    df_clean = pd.DataFrame(list_dict)
    clean_csv_location = 'data/output/clean_pdf_content.csv'
    df_clean['level'] = df_clean['level'].replace({'1':'I','2':'II', '3':'III'})
    df_clean.to_csv(clean_csv_location, header=True, index=False, sep="|", float_format='%d')
    print("Clean CSV file generated successfully.")
if __name__ == '__main__':
    clean_csv_generate()