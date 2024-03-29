from calendar import c
import streamlit as st
import re

# Assuming upload_page, query_data, airflow_trigger, and main_page are separate modules as before

# Placeholder functions for login and register validations from your given logic


def authenticate_user(email, password):
    # Implement your authentication logic here
    # For the sake of simplicity, using a static check
    users = {"abc@northeastern.edu": "Password@123"}
    return users.get(email) == password


def validate_email(email):
    return re.match(r"^[a-zA-Z0-9._%+-]+@northeastern\.edu$", email)


def validate_password(password):
    return re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", password)


def show_login():
    with st.form("login_form", clear_on_submit=True):
        email = st.text_input("Email", key="login_email")
        password = st.text_input(
            "Password", type="password", key="login_password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if not validate_email(email):
                st.error("Email must be a valid Northeastern University email.")
            elif not validate_password(password):
                st.error(
                    "Password must have at least 8 characters, including 1 uppercase, 1 lowercase, 1 number, and 1 special character.")
            elif authenticate_user(email, password):
                st.session_state['logged_in'] = True
                st.success("Login successful!")
                st.experimental_rerun()
            else:
                st.error("Incorrect email or password.")
