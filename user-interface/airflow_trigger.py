import streamlit as st
import requests
def show_airflow_trigger():

    fastapi_url = "http://backend:8000/trigger-airflow-pipeline"

    access_token = st.session_state['access_token']

    # Define the headers with the Authorization header containing the access token
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    st.title("Loading the Data into Snowflake")

    st.write("To load the data into Snowflake, please trigger the Airflow pipeline using the button below")

    if st.button('Trigger Airflow Pipeline'):
        response = requests.post(fastapi_url, st.session_state['s3_file_location'], headers=headers)
        if response.status_code == 200:
            st.success("Pipeline triggered successfully.")
        else:
            error_message = response.json().get("detail", "Unknown error")
            st.error(f"Failed to fetch data: {error_message}")

