import pandas as pd
import streamlit as st
import requests

def show_query_data():

    # Initialize session state for the DataFrame if it's not already set
    if 'df' not in st.session_state:
        st.session_state.df = pd.DataFrame()

    st.title("Query Data")
    df = pd.DataFrame()

    def fetch_data_from_snowflake(query):
        '''
        # Replace 'YOUR_API_ENDPOINT_HERE' with the actual endpoint of your API
        api_endpoint = "YOUR_API_ENDPOINT_HERE/fetch_data"

        try:
            # Make a POST request to your API, sending the SQL query as JSON
            response = requests.post(api_endpoint, json={'query': query})

            # Check if the response status code is 200 (OK)
            if response.status_code == 200:
                # Convert the JSON response to a DataFrame
                df = pd.DataFrame(response.json())
                return df
            else:
                # Handle the case where the API call wasn't successful
                st.error("Failed to fetch data from API.")
                return pd.DataFrame()  # Return an empty DataFrame on failure
        except Exception as e:
            st.error(f"Failed to fetch data: {e}")
            return pd.DataFrame()  # Return an empty DataFrame on exceptions
        '''

    # User input for SQL query
    query = st.text_area("Enter your SQL query",
                         value="SELECT * FROM TABLE LIMIT 10", height=150)
    submit_query = st.button("Execute Query")

    if submit_query:
        if query:
            # Fetch and display the data
            try:
                # Fetch data only if the DataFrame is empty or on explicit user request
                st.session_state.df = fetch_data_from_snowflake(query)
                st.dataframe(st.session_state.df)
            except Exception as e:
                st.error(f"Error executing query: {e}")
        else:
            st.error("Please enter a SQL query.")

    # Apply filters only if the DataFrame is not empty
    if not st.session_state.df.empty:
        # Filtering UI
        st.title("Filter options:")
        selected_filters = {}
        for column in st.session_state.df.columns:
            unique_values = pd.unique(st.session_state.df[column])
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
