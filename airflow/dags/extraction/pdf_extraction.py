import boto3
import configparser
from PyPDF2 import PdfReader
import pandas as pd
from io import BytesIO, StringIO
import re
from difflib import SequenceMatcher
import configparser

config = configparser.RawConfigParser()
config.read('../../../configuration.properties')

def aws_s3_connection():
    access_key = config['AWS']['access_key']
    secret_key = config['AWS']['secret_key']
    bucket_name = config['s3-bucket']['bucket']
    s3_client = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    return s3_client


def find_bucket_key(s3_path):
    """
    This is a helper function that given an s3 path such that the path is of
    the form: bucket/key
    It will return the bucket and the key represented by the s3 path
    """
    s3_components = s3_path.split('/')
    bucket = s3_components[0]
    s3_key = ""
    if len(s3_components) > 1:
        s3_key = '/'.join(s3_components[1:])
    return bucket, s3_key

def split_s3_bucket_key(s3_path):
    """Split s3 path into bucket and key prefix.
    This will also handle the s3:// prefix.
    :return: Tuple of ('bucketname', 'keyname')
    """
    if s3_path.startswith('s3://'):
        s3_path = s3_path[5:]
    return find_bucket_key(s3_path)
  
def extract_information(pdfReader):
  # Getting the text from the first page
  first_page_text = pdfReader.pages[0].extract_text()

  # Using regular expression to find the pattern to extract Year and Level
  pattern = r'(\d{4})\s*Level\s*((\w)+)'
  match = re.search(pattern, first_page_text)

  if match:
    year = match.group(1)
    level = match.group(2)
    return level, year
  else:
    return None, None

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def find_similar_strings(strings, threshold):
    similar_strings = []
    for i in range(len(strings)):
        for j in range(i+1, len(strings)):
            sim_score = similarity(strings[i], strings[j])
            if sim_score >= threshold:
                similar_strings.append((strings[i], strings[j], sim_score))
    return similar_strings

def get_pdf_from_s3(s3_client, bucket, key_s3):
    response = s3_client.get_object(Bucket=bucket, Key=key_s3)
    
    object_content = response['Body'].read()
    
    pdfFileObj = BytesIO(object_content)
    
    return pdfFileObj

def process_pdf_content(s3_uri):
  """ function to read and extract data from pdf file.
  input is a s3 uri
  """
  print("---------------Starting Extraction---------------")
  
  # s3 client
  print("Loading file from S3")
  
  s3_client = aws_s3_connection()
  
  bucket, key_s3 = split_s3_bucket_key(s3_uri)

  pdfFileObj= get_pdf_from_s3(s3_client, bucket, key_s3)
  
  pdfReader = PdfReader(pdfFileObj)
  print("File loaded successfully")
  print("Total number of pages:", len(pdfReader.pages))

  # Extracting level and year information
  level, year = extract_information(pdfReader)

  # Initializing dictionaries to store extracted content
  content = dict()
  topic = ""
  topic_dict = dict()

  print("starting content extraction")
  # Iterating through each page of the PDF and extracting text
  for page_num in range(len(pdfReader.pages)):
    t = pdfReader.pages[page_num].extract_text().split('\n')
    line_num = 0

    # Extracting topic names
    while line_num < len(t):
      if line_num == 0:
        if 'topic outlines' in t[line_num].strip().lower():
          line_num += 1
        topic_new = re.sub(r'[^A-Za-z ]+', '', t[line_num]).strip()

        # Checking if the topic already exists in the content dictionary
        all_keys = [x.lower().strip().replace(" ", "") for x in content.keys()]
        if topic_new.lower().strip().replace(" ", "") in all_keys:
          topic_new = list(filter(lambda x: x.lower().strip().replace(" ", "") == topic_new.lower().strip().replace(" ", ""), content.keys()))[0]

        # Updating the topic if it has changed
        if topic == topic_new:
          pass
        else:
          subtopic = ""
          subtopic_dict = []
          topic = topic_new
      topic_dict = content.get(topic, dict())

      # Identifying subtopics i.e. Learning outcoomes for Topics
      subtopic_loc = t[line_num].find("The candidate should be able to:")
      if subtopic_loc != -1:
        subtopic = t[line_num - 1] if subtopic_loc == 0 else t[line_num][:subtopic_loc + 1]
        subtopic_dict = topic_dict.get(subtopic, [])
        tab_loc = t[line_num].find("\t")

        # Extracting learning outcomes and appending to the subtopic dictionary
        append_list = t[line_num][tab_loc + 1:] + t[line_num + 1]
        if append_list.find("\t") == -1:
          subtopic_dict.append(append_list)

          line_num += 2
        if line_num >= len(t):
          break
      # Handeling corner cases, extract learning outcomes from lines with tabs
      tab_loc = t[line_num].find("\t")

      if tab_loc != -1:
        subtopic_dict.append(t[line_num][tab_loc + 1:])

      # Updating the topic dictionary
      topic_dict[subtopic] = subtopic_dict
      content[topic] = topic_dict

      line_num += 1

  # merge values with same Curriculum Topic
  threshold = 0.75
  similar_strings = find_similar_strings(list(content.keys()), threshold)
  for sim in similar_strings:
    merged_dict = {}
    for key, value in content[sim[0]].items():
      merged_dict[key] = value

    for key, value in content[sim[1]].items():
      merged_dict[key] = value
      
    content[sim[1]] = merged_dict
    del content[sim[0]]
  
  print("content extraction completed")
  
  print("Loading extracted csv to S3")
  raw_data_list  = []
  # Curriculum Topic
  for curr_topic, sub_topics in content.items():
    for sub_topic, learning in sub_topics.items():
      if sub_topic == "":
        continue
      data_dict = {'curriculum_year': year, 'cfa_level': level, 'curriculum_topic': curr_topic, 'curriculum_refresher_reading': sub_topic, 'learning_outcomes': learning}
      raw_data_list.append(data_dict)

  df_raw = pd.DataFrame(raw_data_list)
  
  csv_buffer = StringIO()
  df_raw.to_csv(csv_buffer, sep="\t", index=False)
  
  s3_key = "CSV_Data/" + str(key_s3.split("/")[1].split(".")[0]) + ".csv"
  
  csv_buffer_encode = BytesIO(csv_buffer.getvalue().encode())

  s3_client.upload_fileobj(csv_buffer_encode, bucket, s3_key)
  
  s3_uri_csv = "s3://" + bucket + s3_key
  
  print("Successfully loaded csv to S3")
  
  print("---------------Ending Extraction---------------")

  return s3_uri_csv

process_pdf_content(s3_uri)
