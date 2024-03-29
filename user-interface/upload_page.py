import pandas as pd
import requests
import streamlit as st

def upload_file_to_s3(file):
    try:
        # Prepare the file to be uploaded
        files = {"file": (file.name, file)}
        access_token = st.session_state['access_token']

        # Define the headers with the Authorization header containing the access token
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        # Make the POST request to upload the file
        response = requests.post("http://127.0.0.1:8000/upload", files=files, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            st.success("File uploaded successfully")
        else:
            error_message = response.json().get("detail", "Unknown error")
            st.error(f"Upload failed: {error_message}")
    except Exception as e:
        st.error(f"An error occurred: {e}")

def show_upload_files():
    st.title("Upload File")

    # Display file uploader
    uploaded_file = st.file_uploader("Choose a PDF file", type='pdf')

    if uploaded_file is not None:
        # Upload the file if it's not None
        upload_file_to_s3(uploaded_file)

