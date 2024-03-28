import streamlit as st
import re
import register_page

# This is a placeholder function. You need to implement actual authentication logic here.

def authenticate_user(email, password):
    '''
    try:
        # Make a POST request to your authentication API endpoint
        response = requests.post('YOUR_API_ENDPOINT_HERE/login', json={'email': email, 'password': password})

        # Check if the response status code is 200 (OK), indicating successful authentication
        if response.status_code == 200:
            # You might want to add additional checks here based on the response content
            # For example, check if the API returns a specific message or token indicating successful authentication
            return True
        else:
            # Handle unsuccessful authentication
            return False
    except Exception as e:
        # Handle any exceptions, such as network errors
        print(f"An error occurred: {e}")
        return False
    '''

    # Example: A dictionary of users
    users = {
        # User's email as key, password as value
        "abc@northeastern.edu": "Password@123"
    }
    return users.get(email) == password


def validate_email(email):
    # Email must end with @northeastern.edu
    return re.match(r"^[a-zA-Z0-9._%+-]+@northeastern\.edu$", email)


def validate_password(password):
    # Password must have at least 8 characters, 1 uppercase, 1 lowercase, 1 number, and 1 special character
    return re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", password)


def show_login():
    st.title("Login")

    with st.form("login_form"):
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
            # Implement this function to check credentials
            elif authenticate_user(email, password):
                st.session_state['logged_in'] = True
                st.session_state['current_page'] = None
            # Instead of rerunning, consider redirecting or showing a success message
                st.success("Login successful!")
                st.rerun()
            # Redirect or change view here
            else:
                st.error("Incorrect email or password.")

    if st.button("New user? Please sign up"):
        st.session_state['show_registration_page'] = True
        st.session_state['registration_submitted'] = False
        st.rerun()

