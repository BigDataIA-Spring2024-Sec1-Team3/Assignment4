import streamlit as st
import upload_page
import query_data
import login_page
import register_page
import airflow_trigger
import main_page

PAGES = {
    "Main Page": main_page,
    "Upload Files": upload_page,
    "Airflow Trigger": airflow_trigger,
    "Query Data": query_data
}

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'login'

# Show login or registration page if not logged in
if not st.session_state['logged_in']:
    if st.session_state['current_page'] == 'login':
        login_page.show_login()
    elif st.session_state['current_page'] == 'register':
        register_page.show_register()
else:
    # Main application logic
    st.sidebar.title('Navigation')
    selection = st.sidebar.radio("Go to", list(PAGES.keys()))
    page = PAGES[selection]
    page_function = getattr(
        page, 'show_' + selection.lower().replace(' ', '_'))
    page_function()
