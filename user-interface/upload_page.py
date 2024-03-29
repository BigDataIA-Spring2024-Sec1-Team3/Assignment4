import pandas as pd
import requests
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile


def show_upload_files():

    st.title("Upload Files")

    def upload_files_to_s3(files):
        # The URL of your FastAPI endpoint that handles the upload
        # Replace with your actual endpoint URL
        api_endpoint = "your_fastapi_endpoint/upload"

        # Prepare the files in the format expected by the FastAPI (and most APIs accepting file uploads)
        files_to_upload = [('files', (file.name, file, 'application/pdf'))
                           for file in files]

        try:
            # Make the POST request to upload the files
            response = requests.post(api_endpoint, files=files_to_upload)

            # Check if the request was successful
            if response.status_code == 200:
                print("Files uploaded successfully.")
            else:
                print(
                    f"Failed to upload files. Status code: {response.status_code}, Message: {response.text}")
        except Exception as e:
            print(f"An error occurred: {e}")

    # Initialize session state for uploaded files if not already done
    if 'uploaded_files' not in st.session_state:
        st.session_state['uploaded_files'] = []

    # Function to sync session state with uploaded files

    def sync_uploaded_files():
        uploaded_files = st.file_uploader(
            "Choose files", accept_multiple_files=True, type=['pdf'])

        # Sync session state with the file_uploader's current state
        if uploaded_files is not None:
            # Clear the session state list before adding current uploads to avoid duplicates
            st.session_state['uploaded_files'] = uploaded_files

    # Call the sync function to update session state with the current uploader state
    sync_uploaded_files()

    # Display the stored files from session state in a table
    if st.session_state['uploaded_files']:
        st.write("Following Files are ready to Upload:")
        # Create a list of dictionaries, each representing an uploaded file
        files_info = [{"Filename": file.name, "Size (KB)": file.size / 1024}
                      for file in st.session_state['uploaded_files']]
        # Convert the list of dictionaries into a DataFrame
        df = pd.DataFrame(files_info)
        # Display the DataFrame as a table
        st.table(df)

        # Button to upload files to S3
        if st.button('Upload'):
            if st.session_state['uploaded_files']:
                upload_files_to_s3(st.session_state['uploaded_files'])
                st.success("Files Uploaded Successfully")
            else:
                st.error("No files to upload. Please choose files first.")
    else:
        st.write("No files uploaded yet.")
