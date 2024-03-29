import csv
import xml.etree.ElementTree as ET
import os
import pandas as pd
from pydantic import BaseModel, validator, field_validator
from typing import Optional
from datetime import datetime
    
class PDFContentClass(BaseModel):
    title: str
    topic_name: str
    year: Optional[int]
    level: Optional[int]
    learning_outcome: Optional[str]

    # # Title validation
    # @field_validator("title")
    # def validate_title(cls, title):
    #     if not title:
    #         raise ValueError("Title cannot be null or empty.")
    #     # If title name starts with number or special character, it will be invalid and raise error
    #     if not title[0].isalpha():
    #         raise ValueError("Title cannot start with a number or special character.")

    #     return title

    # # Topic validation
    # @field_validator("topic_name")
    # def validate_topic_name(cls, topic):
    #     # If topic name starts with number or special character, it will be invalid and raise error
    #     if not topic[0].isalpha():
    #         raise ValueError("Topic name cannot start with a number or special character.")

    #     # check if it is test refresher reading
    #     test_topic = topic.find("TEST RR")
    #     if test_topic != -1:    # if test topic found, it returns index
    #         raise ValueError("Invalid topic. Refresher reading is for test.")

    #     return topic
    
    # # Year validation
    # @field_validator('year')
    # def year_must_not_be_from_future(cls, year):
    #     #Skip validation for None or empty strings
    #     if year in [None, '', 'NaN']:
    #         return None
        
    #     if not isinstance(year, int):
    #         raise TypeError("Year field must be an integer")

    #     # check if the year is future year
    #     current_year = datetime.now().year
    #     if not (year <= current_year):
    #         raise ValueError('Year field cannot have future year')
    #     return year

    # # level validation
    # @field_validator('level')
    # def cfa_level_validation(cls, level):
    #     #Skip validation for None or empty strings
    #     if level in [None, '', 'Nan']:
    #         return None
        
    #     # if CFA level is not I, II or III, it is invalid
    #     if level not in [1, 2, 3]:
    #         raise ValueError('Invalid CFA level')
        
    #     return level
    
    # # Learning Outcome  validation
    # @field_validator("learning_outcome")
    # def sentence_completeness_check(cls, paragraph):
    #     #Skip validation for None or empty strings
    #     if paragraph in [None, '', 'Nan']:
    #         return None
    #     return paragraph