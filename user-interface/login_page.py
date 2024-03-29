from calendar import c
import streamlit as st
import re
import requests

def authenticate_user(email, password):
    try:
        # Make a POST request to the FastAPI /token endpoint
        response = requests.post("http://backend:8000/token", data={"username": email, "password": password})

        # Check if the request was successful
        if response.status_code == 200:
            access_token = response.json().get("access_token")
            if "access_token" not in st.session_state:
                st.session_state['access_token'] = access_token
            return True
        else:
            return False
    except requests.RequestException as e:
        st.error(f"Error occurred during authentication: {e}")
        return False


def show_login():
    with st.form("login_form", clear_on_submit=True):
        email = st.text_input("Email", key="login_email")
        password = st.text_input(
            "Password", type="password", key="login_password")
        submitted = st.form_submit_button("Login")

        if submitted:
            response = authenticate_user(email, password)
            if response:
                st.session_state['logged_in'] = True
                st.success("Login successful!")
                st.experimental_rerun()
            else:
                st.error("Incorrect email or password.")
