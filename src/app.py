import streamlit as st
import time
import json
from utils.css_loader import load_css
from utils.session_manager import initialize_session_state
from components.sidebar import sidebar_display
from components.buttons import button_container
from services.jira_client import JiraClient
from components.jira_auth import jira_auth
import requests
from dotenv import load_dotenv
import os
import openai
import re
import pyperclip
from streamlit_extras.stylable_container import stylable_container


load_dotenv()  # Load variables from .env into the environment
openai.api_key = os.getenv("OPENAI_API_KEY")

new_content=f"""*As a* Frontend Developer,
*I want* to integrate the .Net API with the React Js frontend,
*So that* I can effectively and efficiently manage and manipulate data across frontend and backend systems.

*Acceptance Criteria:*

- The React Js frontend must be capable of executing GET, POST, PUT, and DELETE requests to the .Net API successfully.
- The data fetched from the API must be accurately represented and visualized on the frontend.
- Any modifications or updates made on the frontend must be accurately reflected in the backend via the API.
- The integration process should not disrupt or compromise the existing frontend and backend code and should not introduce any new bugs or errors.
- The documentation of the integration process must be comprehensive, detailing the API endpoints and their corresponding frontend components.

**Title:** "Integration of .Net API with React Js Frontend for Enhanced Data Management"
**Priority:** "Low"
**Estimated Effort:** 2

"""


# Function: Rewrite with OpenAI GPT
def rewrite_with_gpt(content):
    prompt = f"""
You are an expert Business Analyst with extensive Jira experience.
Please rewrite the following Jira ticket description into a user story using Gherkin syntax and aligned with the INVEST principle (Independent, Negotiable, Valuable, Estimable, Small, Testable).

Original Content contains the following information:
\"\"\"{content}\"\"\"

Use the format:
**As a** [role],  
**I want** [goal],  
**So that** [reason].

Then add:
**Acceptance Criteria:**  
- **Given**: [initial condition or precondition] \n
  **Then**: [expected outcome] \n
  **When**: [user or system action] \n

- (Repeat as needed for additional scenarios)  


Add:
**Title:** [concise title for the story]
**Priority:** [High / Medium / Low]  
**Estimated Effort:** [in story points or hours]
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional Jira expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"OpenAI API error: {str(e)}")
        return None

#configuration streamlit page settings
st.set_page_config(page_title="AI Helper", layout="centered")

sentiment_mapping = ["one","two","three","four","five"]
# Jira API Endpoint
JIRA_ENDPOINT = os.getenv("JIRA_ENDPOINT")

#initialize session state
initialize_session_state()

if "jira" not in st.session_state:
    st.session_state.jira = JiraClient(JIRA_ENDPOINT) 

jira = st.session_state.jira

#jira authentication
jira_auth(jira, JIRA_ENDPOINT)



def star_rating(label, key):
    #st.markdown("### Rate the response")
    stars = ["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"]
    rating = st.select_slider(
        label,
        options=[1, 2, 3, 4, 5],
        format_func=lambda x: "⭐" * x,
        key=key
    )
    return rating    

def fetch_issue_details(jira_id):
        """
        Fetch issue details from Jira API
        """
        issue_url = f"{JIRA_ENDPOINT}rest/api/2/issue/{jira_id}"
        response = requests.get(issue_url, headers=jira.headers)
        if response.status_code == 200:
            issue_data = response.json()
            #print(issue_data)
            issue_type = issue_data["fields"]["issuetype"]["name"]
            if issue_type.lower() != "story":
                raise ValueError(f"Issue {jira_id} is not a 'Story'. It is a '{issue_type}'.")
            project_name = issue_data["fields"]["project"]["name"]
            description = issue_data["fields"].get("description", "No Description Available")
            summary = issue_data["fields"]["summary"]
            acceptance_criteria = issue_data["fields"].get("customfield_12077", "Not Given")
            return {
                "key": issue_data["key"],
                "project_name": project_name,
                "description": description,
                "summary": summary,
                "acceptance_criteria": acceptance_criteria
            }
        else:
            raise Exception(f"Failed to fetch issue details: {response.status_code} - {response.text}")

def parse_rewritten_content(content: str):
    title_match = re.search(r"\*\*Title:\*\*\s*(.+)", content)
    priority_match = re.search(r"\*\*Priority:\*\*\s*(.+)", content)
    effort_match = re.search(r"\*\*Estimated Effort:\*\*\s*(.+)", content)
    
    # Extract Description block
    description_match = re.search(r"\*\*Description:\*\*\s*(.*?)(?=\n\*\*Acceptance Criteria:\*\*)", content, re.DOTALL)
    
    # Extract Acceptance Criteria block
    acceptance_match = re.search(r"\*\*Acceptance Criteria:\*\*\s*(.*?)(?=\n\*\*Priority:\*\*)", content, re.DOTALL)

    effort_text = effort_match.group(1).strip() if effort_match else "N/A"
    effort_number = re.search(r"\d+", effort_text)
    effort_value = effort_number.group() if effort_number else "N/A"

    return {
        "title": title_match.group(1).strip() if title_match else "N/A",
        "description": description_match.group(1).strip() if description_match else "N/A",
        "acceptance_criteria": acceptance_match.group(1).strip() if acceptance_match else "N/A",
        "priority": priority_match.group(1).strip() if priority_match else "N/A",
        "estimated_effort": effort_value
    } 

def escape_jira_formatting(text: str):
    return text.replace("**", "*")



def update_jira_issue(headers,jira_id, agent_title, agent_description):
        """Update the Jira issue with the refined title and description."""
        issue_url = f"{JIRA_ENDPOINT}rest/api/3/issue/{jira_id}"
        parsed = parse_rewritten_content(agent_description)

        payload = {
            "fields": {
                "summary": parsed["title"],
                "description": escape_jira_formatting(parsed["description"]),
                #"customfield_12077": escape_jira_formatting(parsed["acceptance_criteria"]),
                #"customfield_12078": parsed["priority"],
                #"customfield_12079": parsed["estimated_effort"]

            }
        }

        response = requests.put(issue_url, headers=headers, data=json.dumps(payload))
        if response.status_code == 204:
            success_msg=(f"\n🔹Jira issue: {jira_id} updated successfully! {JIRA_ENDPOINT}browse/{jira_id}")
            return response.status_code,success_msg
        else:
            print(f"Failed to update issue ({response.status_code}): {response.text}")
            error_msg = f"Failed to update issue ({response.status_code}): {response.text}"
            return response.status_code, error_msg

if st.session_state.jira_auth_popup_actioned:
    #Display header
    st.logo("static/image.jpg")
    st.markdown("<h3 class='custom-title' style='color: white;'>AI Helpers for QE</h3>", unsafe_allow_html=True)

    #Load CSS styles
    load_css("static/styles.css") 

    #Welcome message
    if not st.session_state.welcome_message:
        st.markdown(f"<h4>Welcome, \n\n Please select one of the listed AI Helpers for QE in sidebar to proceed.</h4>", unsafe_allow_html=True)
        st.session_state.welcome_message = True
  
    #display sidebar options
    sidebar_display(jira)
    button_css_style = [
        """
        button {
            background-color: white !important;
            color: black !important;
            font-weight: bold !important;
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 16px;
            border: 2px solid red !important;
        }
        """,
        """
        button:hover {
            background-color: darkred !important;
            color: white !important;
        }
        """
    ]
    if st.session_state.selected_helper and not st.session_state.selected_input_type:
         st.markdown(f"Please select the Input type to proceed with **{st.session_state.selected_helper}** helper.")

    elif st.session_state.selected_helper and st.session_state.selected_input_type:
        #clear rewritten content and pushed status if input type changes
        if "previous_input_type" not in st.session_state or st.session_state.previous_input_type != st.session_state.selected_input_type:
            st.session_state.rewritten_content = {}
            st.session_state.pushed_status = {}
            st.session_state.previous_input_type = st.session_state.selected_input_type
        
        if st.session_state.selected_input_type == "Jira ID":
            st.markdown(f"Once done with selecting Jira ID in sidebar, please click on Run Helper Agent to generate response")
            jira_ids_input = st.session_state.jira_selected
            print("jira_ids_input:", jira_ids_input)
            jira_ids = [id for id in jira_ids_input]
            print("jira_ids:", jira_ids)
        
            jira_content = {}
            if jira_ids:
                for jira_id in jira_ids:
                    try:
                        details = fetch_issue_details(jira_id)
                        content = f"**Summary**: {details['summary']} \n\n **Description**:\n\n {details['description']}\n\n **Acceptance Criteria**:\n\n {details['acceptance_criteria']}"
                        with st.expander(f"{details['key']} - {details['summary']}"):
                            st.markdown( content)
                        jira_content[jira_id] = content
                        
                    except Exception as e:
                        st.error(f"{jira_id}: {str(e)}")

        elif st.session_state.selected_helper and st.session_state.selected_input_type == "Free Text Requirement" :
            st.session_state.jira_selected = []
            if not st.session_state["free_text_input"]:
                st.markdown(f"Please provide the requirement in the user input box below to proceed with **{st.session_state.selected_helper}** helper.")
        
            selected_helper = st.session_state.get("selected_helper")
            selected_input_type = st.session_state.get("selected_input_type")
            message = "Type a requirement as per the specified format."
            user_input = st.chat_input(message )

            if user_input:
                st.session_state["free_text_input"] = user_input
                st.session_state["free_text_response"] = None
                st.session_state["rewritten_content"] = {}
                
            free_text_input = st.session_state.get("free_text_input")
            #print("free_text_input:", free_text_input)
            if free_text_input is not None and selected_input_type == "Free Text Requirement":
                with st.expander(f"**Requirement**"):
                    st.text_area("Issue Details", value=free_text_input, height=250)
                with stylable_container(key="run_helper_btn",css_styles=button_css_style):
                    if st.button("Run Helper Agent", key="run_helper_agent"):
                        #print("test")
                        response = rewrite_with_gpt(free_text_input)
                        #response = new_content
                        st.session_state["free_text_response"] = response

                if "free_text_response" in st.session_state and st.session_state["free_text_response"]:
                    response = st.session_state["free_text_response"]
                    if "edit_mode_free_text" not in st.session_state:
                        st.session_state["edit_mode_free_text"] = False
                    if response:
                        with st.expander(f"**Agent Response**"):
                            with st.container(border=True):
                                st.markdown(f"""{response.replace('\n','<br>')}""",unsafe_allow_html=True)
                                col1,col2 = st.columns(2)
                                with col1:
                                    if st.button(f"Copy to Clipboard", key="copy_free_text"):
                                        pyperclip.copy(response)
                                        st.success(f"Copied content to clipboard!")
                                            
                                #with col2:
                                #    toggle_btn_label = "Save Edit" if st.session_state["edit_mode_free_text"] else "Edit"
                                #    if st.button(toggle_btn_label, key=f"edit_toggle_free_text"):
                                #        st.session_state["edit_mode_free_text"] = not st.session_state["edit_mode_free_text"]
                                #        st.rerun()
                                #st.markdown(rating, unsafe_allow_html=True)
                                star_rating("Rate the response:", "star_rating_1")


    if "rewritten_content" not  in st.session_state:
        st.session_state.rewriten_content = {}   
    if "pushed_status" not in st.session_state:
        st.session_state.pushed_status = {}

    #Remove rewritten content for Jira IDs that are no longer selected
    current_selected_ids = set(st.session_state.jira_selected)
    previous_selected_ids = set(st.session_state.get("previous_jira_selected",[]))
    removed_ids = previous_selected_ids - current_selected_ids

    for jira_id in removed_ids:
        if jira_id in st.session_state.rewritten_content:
            del st.session_state.rewritten_content[jira_id]
        if jira_id in st.session_state.pushed_status:
            del st.session_state.pushed_status[jira_id]

    #update the previous selection state            
    
    if st.session_state.jira_selected:
        with stylable_container(key="run_helper_btn",css_styles=button_css_style):
            if st.button("Run Helper Agent"):
                for jira_id in st.session_state.jira_selected:
                    #print("After Helper Agent Run jira_id:", jira_id)
                    original_description = jira_content.get(jira_id, None)
                    #print("original_description:", original_description)
                    with st.spinner("Processing..."):
                        time.sleep(2)
                        new_content = rewrite_with_gpt(original_description)
                        print("new_content:", new_content)                
                        title_match = re.search(r"\*\*Title:\*\*\s*(.+)", new_content)
                        priority_match = re.search(r"\*\*Priority:\*\*\s*(.+)", new_content)
                        effort_match = re.search(r"\*\*Estimated Effort:\*\*\s*(.+)", new_content)
                        #acceptance_match = re.search(r"\*\*Acceptance Criteria:\*\*\s*(.+)", new_content, re.DOTALL)

                        title = title_match.group(1) if title_match else "N/A"
                        priority = priority_match.group(1) if priority_match else "N/A"
                        effort = effort_match.group(1) if effort_match else "N/A"
                        #acceptance_criteria = acceptance_match.group(1).strip() if acceptance_match else "N/A"
    
                        # Remove trailing metadata fields from description
                        description_md = re.sub(r"\n?\*\*Title:\*\*.*", "", new_content).strip()
                        description_md = re.sub(r"\n?\*\*Priority:\*\*.*", "", description_md)
                        description_md = re.sub(r"\n?\*\*Estimated Effort:\*\*.*", "", description_md)
                        #description_md = re.sub(r"\n?\*\*Acceptance Criteria:\*\*.*", "", description_md)
                        
                        rewritten_content = f"**Title:** {title} \n\n**Description:** {description_md}  \n\n**Priority:** {priority} \n\n**Estimated Effort:** {effort}"
                        #print("rewritten_content:", rewritten_content)
                        st.session_state.rewritten_content[jira_id]  = rewritten_content
                        st.session_state.pushed_status[jira_id] = False

                        st.session_state[f"title_{jira_id}"] = title
                        st.session_state[f"priority{jira_id}"] = priority
                        st.session_state[f"effort_{jira_id}"] = effort
                        st.session_state[f"description_md_{jira_id}"] = description_md

            if any(jira_id in st.session_state.rewritten_content for jira_id in st.session_state.jira_selected):
                for jira_id in st.session_state.jira_selected:
                        #print("rewritten jira_id:", jira_id)
                        rewritten_text = st.session_state.rewritten_content.get(jira_id)
                        #print("rewritten_text:", rewritten_text)
                        
                        if rewritten_text:
                            with st.expander(f"Refined Content for {jira_id}"):
                                text_area_key = f"rewritten_text_{jira_id}"
                                edit_mode_key = f"edit_mode_{jira_id}"

                                if edit_mode_key not in st.session_state:
                                    st.session_state[edit_mode_key] = False
                                #updated_text = st.text_area(
                                #    label="Content",
                                #    value=rewritten_text,
                                #    height=250,
                                #    key=text_area_key
                                #)
                                if st.session_state[edit_mode_key]:
                                    edited_text = st.text_area(
                                    label="Edit Content",
                                    value=rewritten_text,
                                    height=250,
                                    key=text_area_key
                                    )
                                    st.session_state.rewritten_content[jira_id] = edited_text
                                else:
                                    st.markdown(rewritten_text, unsafe_allow_html=True)
                                
                                #st.markdown(rating, unsafe_allow_html=True)
                                col1,col2,col3 = st.columns(3)
                                with col1:
                                    if st.button(f"Copy to Clipboard", key=f"copy_{jira_id}"):
                                        pyperclip.copy(rewritten_text)
                                        st.success(f"Copied content to clipboard!")
                                        
                                with col2:
                                    toggle_btn_label = "Save Edit" if st.session_state[edit_mode_key] else "Edit"
                                    if st.button(toggle_btn_label, key=f"edit_toggle_{jira_id}"):
                                        st.session_state[edit_mode_key] = not st.session_state[edit_mode_key]
                                        st.rerun()
                                with col3:  
                                    if st.button("Approve and Push to Jira", key=f"push_{jira_id}"):
                                        st.session_state[f"show_confirmation_{jira_id}"] = True
                                
                                # Confirmation logic
                                if st.session_state.get(f"show_confirmation_{jira_id}", False):
                                    st.write(f"Are you sure you want to push the content of {jira_id} to Jira?")
                                    confirm_col1, confirm_col2, _ = st.columns(3)

                                    with confirm_col1:
                                        print(st.session_state.rewritten_content[jira_id])
                                        if st.button("Yes", key=f"confirm_{jira_id}"):
                                            title = st.session_state.get(f"title_{jira_id}", "Default Title")
                                            description = st.session_state.rewritten_content[jira_id]
                                            #print("description:", description)
                                            status_code, success_msg = update_jira_issue(jira.headers, jira_id, title, description)
                                            st.session_state.pushed_status[jira_id] = True
                                            st.success(f"Content pushed to Jira for {jira_id}: {success_msg}")
                                            st.session_state[f"show_confirmation_{jira_id}"] = False
                                            st.rerun()

                                    with confirm_col2:
                                        if st.button("No", key=f"cancel_{jira_id}"):
                                            st.info(f"Push to Jira for {jira_id} was cancelled.")
                                            st.session_state[f"show_confirmation_{jira_id}"] = False
                                            st.rerun()

                                # Show Jira link if already pushed
                                if st.session_state.pushed_status.get(jira_id, False):
                                    jira_url = f"{JIRA_ENDPOINT}browse/{jira_id}"
                                    st.info(f"✅ Content for {jira_id} has been pushed to Jira: [View in Jira]({jira_url})")
                                star_rating("Rate the response:", f"star_rating_{jira_id}")