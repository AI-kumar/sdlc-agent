# sdlc-agent

.env                     # Environment variables file
.streamlit/              # Streamlit configuration folder
    config.toml          # Streamlit configuration file
requirements.txt         # Python dependencies file
src/                     # Source code folder
    __pycache__/         # Compiled Python files (ignored in most cases)
    app.py               # Main application entry point
    components/          # UI components and related logic
        __pycache__/     
        buttons.py       # Button-related components
        dialogs.py       # Dialog-related components
        jira_auth.py     # Jira authentication logic
        rating.py        # Rating-related components
        response_gpt.py  # GPT response handling
        response_options.py # Response options logic
        sidebar.py       # Sidebar-related components
    landingpage.py       # Landing page logic
    services/            # Service-related logic
        __pycache__/     
        jira_client.py   # Jira client implementation
    utils/               # Utility functions and helpers
        __pycache__/     
        css_loader.py    # CSS loading utility
        excel_read.py    # Excel reading utility
        session_manager.py # Session management utility
static/                  # Static assets
    styles.css           # CSS styles for the application
