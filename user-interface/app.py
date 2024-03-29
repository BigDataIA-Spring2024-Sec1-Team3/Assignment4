import streamlit as st
import re
import upload_page
import query_data
import airflow_trigger
import main_page
import login_page
import register_page

# Main app logic starts here
PAGES = {
    "Main Page": main_page,
    "Upload Files": upload_page,
    "Airflow Trigger": airflow_trigger,
    "Query Data": query_data
}

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("Login/Register")
    tab1, tab2 = st.tabs(["Register", "Login"])

    with tab1:
        register_page.show_register()

    with tab2:
        login_page.show_login()

else:
    st.sidebar.title('Navigation')
    selection = st.sidebar.radio("Go to", list(PAGES.keys()))

    if st.sidebar.button('Logout'):
        st.session_state['logged_in'] = False
        st.experimental_rerun()

    if st.session_state['logged_in']:
        page = PAGES[selection]
        page_function = getattr(
            page, 'show_' + selection.lower().replace(' ', '_'))
        page_function()
