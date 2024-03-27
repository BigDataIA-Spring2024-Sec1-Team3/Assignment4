import streamlit as st

def show_main_page():

    st.title(
        "Development of a Structured Database for Finance Professional Development Resources")

    st.write(
        '''
In this project, we built an end-to-end pipeline using Airflow to automate the data extraction and storing of meta-data and content of pdf files into Snowflake. Following were the requirements:

a. Building an API service using Fast API that will accept the location of the S3-file and kickoff an Airflow pipeline where the pipeline will perform the following tasks:

* Extraction
* Data validation using tools discussed earlier
* Loading of the data and metadata into Snowflake


b. Building another API service using FAST API that would interface with Snowflake and return back responses to queries.'''

    )
