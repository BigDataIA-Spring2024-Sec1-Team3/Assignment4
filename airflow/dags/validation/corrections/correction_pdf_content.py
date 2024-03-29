import pandas as pd
import numpy as np
from utils.model_pdf_content import PDFContentClass
import re
import configparser
import boto3
from io import BytesIO, StringIO
from pydantic import ValidationError

def correct_topic_value(error_raised, topic_name):
    if error_raised=="Topic name cannot start with a number or special character.":
        pattern = r'^[\d\W_]+'
        # Use re.sub to replace the matched pattern with an empty string
        stripped_topic_name = re.sub(pattern, '', topic_name)
        return stripped_topic_name
    if error_raised=="Invalid topic.":
        return
    
def correct_title_value(error_raised, title):
    print(error_raised, "--",title)
    if error_raised=="Title cannot be None or Empty":
        return ' '
    elif error_raised=="Title name cannot start with a number or special character.":
        pattern = r'^[\d\W_]+'
        # Use re.sub to replace the matched pattern with an empty string
        stripped_title_name = re.sub(pattern, '', title)
        return stripped_title_name
    elif error_raised=="Invalid title.":
        return
    else:
        return

# function to separate bucket and key from S3 path 
def separate_bucket_key(s3_path):
    # removing s3:// prefix if it exists
    if s3_path.startswith('s3://'):
        s3_path = s3_path[5:]
    s3_values = s3_path.split('/')
    bucket = s3_values[0]
    s3_key = ""
    
    # if key(csv) exists in the S3 path, then update s3_key path
    if len(s3_values) > 1:
        s3_key = '/'.join(s3_values[1:])
    return bucket, s3_key

# Function to validate data using PyDantic functions and correcting values if wrong
def content_validate_data(model, **row):
    temp= []
    try:
        attempts=0
        while attempts<3:
            try:
                # passing the row to pydantic validation model
                model_instance = model(**row)
                return model_instance.model_dump()
            # if row couldn't bypass validation, we will try to correct the data based on the error raised
            except Exception as e:
                for error in e.errors():
                    column_name = error['loc'][0]
                    error_raised = error['msg']
                    if column_name=="topic_name":
                        if "Invalid topic. Refresher reading is for test." in error_raised:
                            break
                        else:
                            row["topic_name"] = row["topic_name"]
                    if column_name=="year":
                        row[column_name] = None
                    if column_name=="level":
                        pass
                    if column_name == "learning_outcome":
                        temp = row[column_name].strip(" ")
                        temp_list = [s.strip() for s in temp.split("\n")]
                        temp = ' '.join(temp_list)
                        temp = re.sub(r'\s+', ' ', temp)
                        temp = temp.replace("□", "", 1)
                        temp = temp.replace("□", ";")
                        row[column_name]=temp
                attempts+=1
    except KeyError as e:
        print(f"Error processing row: {e}")
    except ValidationError as e:
        print(f"Validation error: {e}")

    return temp

# Main function to fetch raw csv file and uploading corrected/validated CSV files
def content_clean_csv_generate(s3_uri):
    
    # Accessing CSV file to be validated from S3
    config = configparser.ConfigParser()
    config.read('configuration.properties')
    
    # s3 client
    s3_boto3_client = boto3.client('s3', aws_access_key_id=config['AWS']['access_key'], aws_secret_access_key=config['AWS']['secret_key'])
    bucket, csv_key = separate_bucket_key(s3_uri)
    
    # fetching raw csv
    response = s3_boto3_client.get_object(Bucket=bucket, Key=csv_key)
    csv_obj_content = response['Body'].read()
    
    # file like object creation
    pdfFileObj = BytesIO(csv_obj_content)
    pdf_df = pd.read_csv(pdfFileObj, sep="\t")
    pdf_df = pdf_df.replace(np.nan, None)
    
    print(pdf_df.head())
    # iterating over CSV and validating data
    clean_data_list = []
    for _, row in pdf_df.iterrows():
        res = content_validate_data(PDFContentClass, **row.to_dict())
        if res:
            clean_data_list.append(res)
    
    clean_data_df = pd.DataFrame(clean_data_list, columns=['title','level', 'year', 'topic_name', 'learning_outcome'])
    
    # Create a StringIO object to hold the CSV data
    csv_buffer = StringIO()
    
    # Write the DataFrame to the StringIO object as a tab-separated CSV file
    clean_data_df['level'] = clean_data_df['level'].replace({'1':'I','2':'II', '3':'III'})
    clean_data_df.to_csv(csv_buffer, sep="\t", index=False, header=True)
    
    clean_csv_file_name = str(csv_key.split("/")[2])
    s3_clean_key = "Validated_CSV/PDF_Content/" + clean_csv_file_name
    
    encoded_csv = BytesIO(csv_buffer.getvalue().encode())
  
    # uploading clean CSV to Validated_CSV folder in S3
    s3_boto3_client.upload_fileobj(encoded_csv, bucket, s3_clean_key)
    
    print(clean_data_df.head())
    print("Clean CSV file generated successfully.")
    
    return clean_csv_file_name