import csv
import xml.etree.ElementTree as ET
import os
import pandas as pd
from pydantic import BaseModel, validator, field_validator
from typing import Optional
from datetime import datetime
import nltk
 
# Define the XML namespace
namespace = {'tei': 'http://www.tei-c.org/ns/1.0'}
input_directory = "data/input/grobid-files"
csv_data = []

try:
    for filename in os.listdir(input_directory):
        if filename.endswith('.xml'):
            # Parse the XML document
            tree = ET.parse(os.path.join(input_directory, filename))
            root = tree.getroot()
            year = filename.split('-')[0]
            level = filename.split('-')[1][1]

            # Initialize variables to store data
            title = ""
            topic_name = ""
            learning_outcome = ""

            title_element = root.find('.//tei:titleStmt/tei:title', namespace)

            # Iterate through each 'div' element in the XML
            for div in root.findall('.//tei:div', namespace):
                # Get the 'head' element inside the current 'div'
                head_element = div.find('.//tei:head', namespace)

                # Rule 1: Set main_part to the text of the 'head' element in the previous 'div'
                if head_element is not None and "LEARNING OUTCOMES" in head_element.text:
                    title = prev_head_text if prev_head_text else head_element.text
                    try:
                        csv_data.pop()
                    except:
                        continue

                # Rule 2: Set sub_part to the text of the 'head' element in the current 'div'
                topic_name = head_element.text if head_element is not None else ""

                # Rule 3: Concatenate all text content within <p> elements
                learning_outcome = ' '.join([p.text.strip() for p in div.findall('.//tei:p', namespace) if p.text is not None])

                try:
                    if title == '' and "LEARNING OUTCOMES" in title_element.text:
                        head = title_element.text.replace(' LEARNING OUTCOMES', '')
                        title = head
                except:
                    title = "N/A"

                if topic_name != "LEARNING OUTCOMES":
                    csv_data.append([title, level, year, topic_name, learning_outcome])

                # Save the 'head' text of the current 'div' for Rule 1 in the next iteration
                prev_head_text = head_element.text if head_element is not None else ""

    # Write data to CSV file
    file_path = 'data/input/csv-input-files/pdf_content.csv'
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['title', 'level', 'year', 'topic_name', 'learning_outcome'])
        csv_writer.writerows(csv_data)

    print("CSV file generated successfully.")
except Exception as e:
    print(f"An error occurred: {e}")

try:
    # Attempt to read the CSV with a specified delimiter (e.g., tab)
    data = pd.read_csv(file_path, delimiter='\t')
    print(data.tail())
except Exception as e:
    print("Error reading the CSV file:", e)
    
class PDFContentClass(BaseModel):
    title: str
    topic_name: str
    year: Optional[int]
    level: Optional[str]
    learning_outcome: Optional[str]

    # Title validation
    @field_validator("title")
    def validate_title(cls, title):
        if not title:
            raise ValueError("Title cannot be null or empty.")
        # If title name starts with number or special character, it will be invalid and raise error
        if not title[0].isalpha():
            raise ValueError("Title cannot start with a number or special character.")

        return title

    # Topic validation
    @field_validator("topic_name")
    def validate_topic_name(cls, topic):

        if not topic:
            raise ValueError("Topic cannot be null or empty.")
        # If topic name starts with number or special character, it will be invalid and raise error
        if not topic[0].isalpha():
            raise ValueError("Topic name cannot start with a number or special character.")

        # check if it is test refresher reading
        test_topic = topic.find("TEST RR")
        if test_topic != -1:    # if test topic found, it returns index
            raise ValueError("Invalid topic. Refresher reading is for test.")

        return topic
    
    # Year validation
    @field_validator('year')
    def year_must_not_be_from_future(cls, year):
        #Skip validation for None or empty strings
        if year in [None, '', 'NaN']:
            return None
        
        if not isinstance(year, int):
            raise TypeError("Year field must be an integer")

        # check if the year is future year
        current_year = datetime.now().year
        if not (year <= current_year):
            raise ValueError('Year field cannot have future year')
        return year

    # level validation
    @field_validator('level')
    def cfa_level_validation(cls, level):
        #Skip validation for None or empty strings
        if level in [None, '', 'Nan']:
            return None
        
        # if CFA level is not I, II or III, it is invalid
        if level not in ['1','2','3']:
            raise ValueError('Invalid CFA level')
        
        return level
    
    # Learning Outcome  validation
    @field_validator("learning_outcome")
    def sentence_completeness_check(cls, paragraph):
        #Skip validation for None or empty strings
        if paragraph in [None, '', 'Nan']:
            return None
        return paragraph