import streamlit as st
import re

def validate_email(email):
    # Email must end with @northeastern.edu
    return re.match(r"^[a-zA-Z0-9._%+-]+@northeastern\.edu$", email)

def validate_password(password):
    # Password must have at least 8 characters, 1 uppercase, 1 lowercase, 1 number, and 1 special character
    return re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", password)

def show_register():
    st.title("Register")

    with st.form("register_form"):
        email = st.text_input("Email", key="register_email")
        password = st.text_input(
            "Password", type="password", key="register_password")
        password_confirm = st.text_input(
            "Confirm Password", type="password", key="register_password_confirm")
        submitted = st.form_submit_button("Register")

        if submitted:
            if not validate_email(email):
                st.error("Email must be a valid Northeastern University email.")
            elif not validate_password(password):
                st.error(
                    "Password must have at least 8 characters, including 1 uppercase, 1 lowercase, 1 number, and 1 special character.")
            elif password != password_confirm:
                st.error("Passwords do not match.")
            else:
                # Here, implement your logic to register the user, such as adding them to a database
                st.success("Registration successful!")
                st.session_state['current_page'] = 'login'
                st.rerun()
