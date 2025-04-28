import streamlit as st
import json
import time

@st.dialog("Please Provide Jira Credentials")
def type_user_password():
    st.text_input("Jira Username", type="default", key="user")
    st.text_input("Password", type="password", key="password")
    if st.button("**Submit**"):
        if st.session_state.user and st.session_state.password:
            st.session_state.jira_auth_popup_actioned = True
            st.session_state.jira_user_authenticated = True
        else:
            st.error("Please enter your credentials.")

    

#@st.dialog("Please authenticate to work with Jira")
def jira_auth_confirm(jira, JIRA_ENDPOINT):
    # Initialize session state flags
    if "show_jira_login" not in st.session_state:
        st.session_state.show_jira_login = False
    if "jira_user_authenticated" not in st.session_state:
        st.session_state.jira_user_authenticated = False
    if "jira_auth_popup_actioned" not in st.session_state:
        st.session_state.jira_auth_popup_actioned = False
    st.markdown("""
    <style>
        .custom-title {
            font-size: 32px;
            color: white;
            background-color: red;
            padding: 10px 20px;
            border-radius: 10px;
            text-align: center;
        }
    </style>
            """, unsafe_allow_html=True)
    st.markdown("<h3 class='custom-title' style='color: white;'>Welcome to AI Helpers for QE</h3>", unsafe_allow_html=True)
    st.markdown("""------ """)
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        left_btn, right_btn = st.columns(2)
    #col = st.columns(2)

        with left_btn:
            if st.button("**Skip Jira Authentication**",use_container_width=True):
                st.session_state.jira_user_authenticated = False
                st.session_state.jira_auth_popup_actioned = True
                st.session_state.show_jira_login = False
                st.rerun()

        with right_btn:
            if st.button("**Authenticate with Jira**",use_container_width=True):
                st.session_state.show_jira_login = True

    # Show input fields only if Authenticate was clicked
    if st.session_state.show_jira_login:
        with st.container(border=True):
            user = st.text_input("Jira Username", key="jira_user_input")
            password = st.text_input("Password", type="password", key="jira_pass_input")

            if st.button("Submit Credentials"):
                if user and password:
                    jira.set_credentials(user, password)
                    try:
                        if not jira.authenticate_user():
                            st.session_state.jira_user_authenticated = False
                            st.session_state.jira_auth_popup_actioned = False
                            st.error("❌ Invalid credentials.")
                        else:
                            st.session_state.jira_user_authenticated = True
                            st.session_state.jira_auth_popup_actioned = True
                            st.success("✅ Authentication successful!")
                            time.sleep(1)
                            st.rerun()
                    except Exception as e:
                        st.error(f"Authentication failed: {str(e)}")
                else:
                    st.warning("Please enter both username and password.")





@st.dialog("Fill Survey Form")
def survey():
    st.write(f"Please provide feedback about what did you like about the Helper and what can be improved.")
    input = st.text_input("Input...")
    if st.button("Submit"):
        st.session_state.survey_form = {"input": input}

        #save the input as JSON
        with open("survey_form.json", "w") as f:
            st.info("Feedback submitted successfully!")
            json.dump(st.session_sate.survey_form, f)
        
        st.rerun()

@st.dialog("User Confirmation")        
def user_confirm():
    st.write(f"Are you sure you want to push the data to Jira?")
    col = st.columns(2)
    st.session_state.yes_clicked = False
    st.session_state.no_clicked = False

    with col[0]:
        if st.button("Yes", disabled=st.session_state.no_clicked):
            st.session_state.yes_clicked = True
            st.session_state.no_clicked = False
            st.success("Data pushed to Jira successfully!")
            time.sleep(2)
            st.rerun()

    with col[1]:
        if st.button("No", disabled=st.session_state.yes_clicked):
            st.session_state.no_clicked = True
            st.session_state.yes_clicked = False
            st.warning("Data push to Jira cancelled.")
            time.sleep(2)
            st.rerun()


