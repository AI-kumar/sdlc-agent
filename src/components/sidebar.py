import streamlit as st
from components.dialogs import survey
from components.buttons import button_container

def update_jira_selected():
    st.session_state.jira_selected = st.session_state.jira_multiselect

def sidebar_display(jira):
    with st.sidebar:
       
        with st.container(border=True):
            st.markdown("**Please select the QE helper**")
            
            if button_container("button_1", "Requirement Analysis & Standardization", "Helper"):
                st.session_state.selected_helper = "Requirement Analysis & Standardization"
                st.session_state.selected_input_type = False
                st.rerun()
            
            if button_container("button_2", "Test Case Generator", "Helper"):
                st.session_state.selected_helper = "Test Case Generator"
                st.session_state.selected_input_type = False
                st.rerun() 

        #select Input type
        if st.session_state.selected_helper:
            st.markdown(""" """)
            with st.container(border=True):
                if st.session_state.jira_user_authenticated:
                    st.markdown("**Please select the input type to helper**")
                    if button_container("button_4", "Free Text Requirement", "Input Type"):
                        st.session_state.selected_input_type = "Free Text Requirement"
                        st.session_state["free_text_input"] = None
                        st.rerun()
                                    
                    if button_container("button_3", "Jira ID", "Input Type"):
                        st.session_state.selected_input_type = "Jira ID"
                        st.session_state.show_multiselect = True
                        st.session_state.selected_options = []
                        st.session_state.show_all_options = False
                        st.rerun()
                else:
                    st.markdown("**Please select the input type to helper**")
                    if button_container("button_4", "Free Text Requirement", "Input Type"):
                        #st.markdown("**Please provide requirement as free text in main window**")
                        st.session_state.selected_input_type = "Free Text Requirement"
                        st.session_state["free_text_input"] = None
                        st.rerun()

                if st.session_state.selected_input_type == "Jira ID":
                     
                    if "jira_ids_all" not in st.session_state:
                        st.session_state.jira_ids_all = jira.get_accessible_issues(["Story", "Task", "Bug"])
                    if "jira_selected" not in st.session_state:
                        st.session_state.jira_selected = []
                    
                    
                    jira_ids_to_display = (st.session_state.jira_ids_all[:st.session_state.jira_display_count] 
                                           if len(st.session_state.jira_ids_all) >= st.session_state.jira_display_count 
                                           else st.session_state.jira_ids_all)
                    
                    selected = st.multiselect(
                            "Select Jira IDs:", 
                             options=jira_ids_to_display,
                             default=st.session_state.jira_selected,
                             key="jira_multiselect",
                             on_change=update_jira_selected
                            )
                    
                    #update the session state only if the selected changes
                    if selected != st.session_state.jira_selected:
                        st.session_state.jira_selected = selected

                    if st.session_state.jira_display_count < len(st.session_state.jira_ids_all):
                        if st.button("More..."):
                            st.session_state.jira_display_count += 5
                            st.rerun()
                            
                    print("Selected jira", st.session_state.jira_selected)    

        if "survey_form" not in st.session_state:
            with st.expander("***Survey Form***"):
                with st.container(border=True):
                    st.write("Fill the survey form \n -----")
                    if st.button("Survey Form"):
                        survey()
            