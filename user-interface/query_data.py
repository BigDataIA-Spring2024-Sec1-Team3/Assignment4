import pandas as pd
import streamlit as st


def show_query_data():

    # Initialize session state for the DataFrame if it's not already set
    if 'df' not in st.session_state:
        st.session_state.df = pd.DataFrame()

    st.title("Query Data")
    df = pd.DataFrame()

    def fetch_data_from_snowflake(query):

        try:
            '''
            conn = snowflake.connector.connect(
                user='YOUR_USER',
                password='YOUR_PASSWORD',
                account='YOUR_ACCOUNT',
                warehouse='YOUR_WAREHOUSE',
                database='YOUR_DATABASE',
                schema='YOUR_SCHEMA'
            )

            # Using pandas' read_sql to simplify fetching into DataFrame
            df = pd.read_sql(query, conn)

            conn.close()
            return df
            '''
            return df
        except Exception as e:
            st.error(f"Failed to fetch data: {e}")
            df = pd.DataFrame()

        return df

    # User input for SQL query
    query = st.text_area("Enter your SQL query",
                         value="SELECT * FROM YOUR_TABLE LIMIT 10", height=150)
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
