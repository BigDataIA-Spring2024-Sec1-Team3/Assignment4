import pandas as pd
import streamlit as st
import requests

def fetch_data_from_snowflake(query):
        try:
            access_token = st.session_state['access_token']
            # Define the headers with the Authorization header containing the access token
            headers = {
                "Authorization": f"Bearer {access_token}"
            }

            response = requests.post("http://backend:8000/execute/?query=" + query, headers=headers)
            if response.status_code == 200:
                # Convert the JSON response to a DataFrame
                result = response.json()
                df = pd.DataFrame(result['result'])
                return df
            else:
                error_message = response.json().get("detail", "Unknown error")
                st.error(f"Failed to fetch data: {error_message}")
                return pd.DataFrame()  # Return an empty DataFrame on failure
        except Exception as e:
            st.error(f"An error occured: {e}")
            return pd.DataFrame()  # Return an empty DataFrame on exceptions

def show_query_data():

    # Initialize session state for the DataFrame if it's not already set
    if 'df' not in st.session_state:
        st.session_state.df = pd.DataFrame()

    st.title("Query Data")
    df = pd.DataFrame()

    # User input for SQL query
    query = st.text_area("Enter your SQL query", height=150)
    submit_query = st.button("Execute Query")

    if submit_query:
        if query:
            # Call the function to fetch data from the API
            st.session_state.df  = fetch_data_from_snowflake(query)
            st.dataframe(st.session_state.df)
            if not df.empty:
                st.write("Data fetched successfully:")
        else:
            st.warning("Please enter a query.")

    # Apply filters only if the DataFrame is not empty
    if not st.session_state.df.empty:
        # Filtering UI
        st.title("Filter options:")
        selected_filters = {}
        for column in st.session_state.df.columns:
            unique_values = pd.unique(st.session_state.df[column].astype(str))
            selected_values = st.multiselect(
                f"Filter {column} by:", options=unique_values, key=column)
            if selected_values:
                selected_filters[column] = selected_values

        # Apply filters to DataFrame if any filters are selected
        if selected_filters:
            filtered_df = st.session_state.df.copy()
            for column, values in selected_filters.items():
                filtered_df = filtered_df[filtered_df[column].isin(values)]

            st.write("Filtered Data:")
            st.dataframe(filtered_df)
        else:
            st.write("No filters applied.")
    else:
        if submit_query:
            st.error("No data to filter.")
