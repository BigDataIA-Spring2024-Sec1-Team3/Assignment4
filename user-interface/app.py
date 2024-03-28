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

# Initialize session state variables
if 'show_registration_page' not in st.session_state:
    st.session_state['show_registration_page'] = False
if 'registration_submitted' not in st.session_state:
    st.session_state['registration_submitted'] = False
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'login'
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Show login or registration page if not logged in
if not st.session_state.get('logged_in', False):
    if st.session_state.get('current_page', 'login') == 'login' and not st.session_state['show_registration_page']:
        login_page.show_login()
    elif st.session_state['show_registration_page'] and not st.session_state['registration_submitted']:
        register_page.show_register()
        st.session_state['show_registration_page'] = False  # Prevent loop


else:
    # Main application logic
    st.sidebar.title('Navigation')
    selection = st.sidebar.radio("Go to", list(PAGES.keys()))

    # Logout functionality
    if st.sidebar.button('Logout'):
        st.session_state['logged_in'] = False
        st.session_state['current_page'] = 'login'
        st.rerun()

    # Display the selected page
    if st.session_state['logged_in']:
        page = PAGES[selection]
        page_function = getattr(
            page, 'show_' + selection.lower().replace(' ', '_'))
        page_function()
