import streamlit as st
from streamlit_extras.stylable_container import stylable_container

def button_container(key, label, type):
    is_selected = st.session_state.get(f"{type}_{key}_selected", False)
    with stylable_container(
            key=key,
            css_styles=[
                f"""
                button{{
                    border: { 'solid .3em red' if is_selected else 'solid .1em red'};
                    border-radius: 10px;
                    color: {'red' if is_selected else 'black' };
                    background-color: 'white';
                    padding: 5px 15px;
                    font-weight: {'bold' if is_selected else 'normal'};
                    margin: -2px 0;
                }}
                """,
                f"""
                button:hover {{
                    background-color: white;    
                    border: solid .2em red;
                    border-radius: 10px;
                    color: black;
                }}
                """,
            ],
    ):
        if st.button(label, use_container_width=True):
            for k in st.session_state.keys():
                if k.endswith(f"_selected") and k.startswith(f"{type}_"):
                    st.session_state[k] = False
            
            #clear input type and related state when switching helpers
            if type == "Helper":
                st.session_state["selected_input_type"] = None
                for k in st.session_state.keys():
                    if k.endswith("_selected") and k.startswith("Input Type_"):
                        st.session_state[k] = False
                st.session_state["free_text_input"] = None
                st.session_state["jira_selected"] = []
                st.session_state["rewritten_content"] = {}
                st.session_state["pushed_status"] = {}

            st.session_state[f'{type}_{key}_selected'] = True
            st.session_state[type] = label
            return True