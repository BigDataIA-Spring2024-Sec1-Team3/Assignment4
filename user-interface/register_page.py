import streamlit as st
import re
import requests
from pymongo import MongoClient
import configparser
from pydantic import BaseModel

config = configparser.RawConfigParser()
config.read('../configuration.properties')

class User(BaseModel):
    userid: int
    username: str
    password: str
    email: str

def validate_email(email):
    # Email must end with @northeastern.edu
    return re.match(r"^[a-zA-Z0-9._%+-]+@northeastern\.edu$", email)


def validate_password(password):
    # Password must have at least 8 characters, 1 uppercase, 1 lowercase, 1 number, and 1 special character
    return re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", password)

def get_last_user_id(collection):
    last_user = collection.find_one(sort=[("userid", -1)])
    if last_user:
        return last_user["userid"]
    else:
        return 0
               
def show_register():
    with st.form("register_form", clear_on_submit=True):
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
                try:
                    client = MongoClient(config['MONGODB']['MONGODB_URL'])
                    db = client[config['MONGODB']["DATABASE_NAME"]]
                    collection = db[config['MONGODB']["COLLECTION_USER"]]
                    last_user_id = get_last_user_id(collection)
                    new_user_id = last_user_id + 1

                    # Call the FastAPI signup endpoint
                    user = User(userid=new_user_id, password=password, username=email, email=email)
                    user_data = user.dict()

                    response = requests.post("http://backend:8000/signup", json=user_data)
                    if response.status_code == 200:
                        # If the request was successful, display a success message
                        st.success("Registration successful!")
                    else:
                        # If the request failed, display the error message from the response content
                        error_message = response.json().get("detail", "Unknown error")
                        st.error(f"Registration failed: {error_message}")
                except Exception as e:
                    print(e)
                
