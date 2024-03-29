import streamlit as st
import requests
def show_airflow_trigger():

    fastapi_url = "http://localhost:8000/trigger-airflow-pipeline/"
    file_location = "s3://your-bucket-name/your-file.csv"

    st.title("Loading the Data into Snowflake")

    st.write("To load the data into Snowflake, please trigger the Airflow pipeline using the button below")

    if st.button('Trigger Airflow Pipeline'):
        response = requests.post(fastapi_url, json={"file_location": file_location})
        if response.status_code == 200:
            st.success("Pipeline triggered successfully.")
        else:
            st.error("Failed to trigger pipeline.")

