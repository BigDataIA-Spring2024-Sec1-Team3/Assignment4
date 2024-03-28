import streamlit as st

def show_airflow_trigger():

    st.title("Loading the Data into Snowflake")

    st.write("To load the data into Snowflake, please trigger the Airflow pipeline using the button below")

    st.button("Trigger Airflow Pipeline")

