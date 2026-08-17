import streamlit as st
import re
from datetime import datetime
import pandas as pd
import os
from PIL import Image

try:
    from streamlit_gsheets import GSheetsConnection
except ImportError:
    GSheetsConnection = None

# ==========================================
# PAGE CONFIGURATION & THEMING
# ==========================================
st.set_page_config(
    page_title="BuildWithNin | Zero-Code AI",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom Cyberpunk / Tech Minimalist Theme matching the logo
st.markdown("""
    <style>
    /* Global Page Background & Text */
    .stApp {
        background-color: #16191D;
        color: #E0E6ED;
        font-family: 'Segoe UI', Roboto, Helvetica, sans-serif;
    }
    
    /* Hide Default Streamlit Chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Accent Text & Headers */
    .brand-title {
        text-align: center;
        font-size: 2.8rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #8AE917;
        margin-bottom: 0px;
        text-shadow: 0 0 20px rgba(138, 233, 23, 0.2);
    }
    .brand-subtitle {
        text-align: center;
        font-size: 1.1rem;
        color: #9BA3AF;
        margin-top: 5px;
        margin-bottom: 1.5rem;
    }
    
    /* Form Inputs & Placeholders */
    .stTextInput input {
        background-color: #20252B !important;
        color: #FFFFFF !important;
        border: 1px solid #333D48 !important;
        border-radius: 8px !important;
    }
    .stTextInput input::placeholder {
        color: #A3AEBA !important; /* Brighter gray for better mobile visibility */
        opacity: 1 !important;
    }
    .stTextInput input:focus {
        border: 1px solid #8AE917 !important;
        box-shadow: 0 0 10px rgba(138, 233, 23, 0.3) !important;
    }

    /* Standard Buttons (Social Links) */
    div[data-testid="stLinkButton"] > a {
        background-color: #20252B !important;
        color: #8AE917 !important;
        border: 1.5px solid #8AE917 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.25s ease-in-out !important;
    }
    div[data-testid="stLinkButton"] > a:hover {
        background-color: #8AE917 !important;
        color: #16191D !important;
        box-shadow: 0 0 15px rgba(138, 233, 23, 0.4) !important;
        transform: translateY(-1px);
    }
    
    /* Highlight the Form Submit Button (Aggressive Overrides) */
    div[data-testid="stFormSubmitButton"] button {
        background-color: #8AE917 !important;
        border: 1px solid #8AE917 !important;
        border-radius: 8px !important;
        transition: all 0.25s ease-in-out !important;
    }
    /* Force the text inside the button to be dark */
    div[data-testid="stFormSubmitButton"] button p, 
    div[data-testid="stFormSubmitButton"] button span {
        color: #16191D !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
    }
    /* Hover effects for the submit button */
    div[data-testid="stFormSubmitButton"] button:hover {
        background-color: #9DF72C !important;
        border: 1px solid #9DF72C !important;
        box-shadow: 0 0 15px rgba(138, 233, 23, 0.6) !important;
        transform: translateY(-1px);
    }

    /* Expanders (Prompt Vault) */
    div[data-testid="stExpander"] {
        background-color: #1B1F24 !important;
        border: 1px solid #2B333C !important;
        border-radius: 10px !important;
        margin-bottom: 12px;
    }
    div[data-testid="stExpander"] summary {
        color: #E0E6ED !important;
        font-weight: 600 !important;
    }
    div[data-testid="stExpander"] summary:hover {
        color: #8AE917 !important;
    }

    /* Horizontal Divider */
    hr {
        border-color: #2B333C !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# SECTION 1: THE HERO & BRAND LOGO
# ==========================================
col1, col2, col3 = st.columns([1, 4, 1])
with col2:
    try:
        # Looking for logo.png
        st.image("logo.png")
    except:
        st.markdown("<h1 class='brand-title'>Build With Nin</h1>", unsafe_allow_html=True)
        st.warning("Make sure your image is named exactly 'logo.png' and is in the same folder as app.py")
    
    st.markdown("<p class='brand-subtitle'>Zero-code AI tools & automated workflows.</p>", unsafe_allow_html=True)

    # Social Channels
    sc1, sc2 = st.columns(2)
    with sc1:
        st.link_button("📸 Instagram", "https://instagram.com/buildwithnin", use_container_width=True)
    with sc2:
        st.link_button("🎵 TikTok", "https://tiktok.com/@buildwithnin", use_container_width=True)

st.write("")
st.divider()

# ==========================================
# SECTION 2 & 3: EMAIL CAPTURE & DB INTEGRATION
# ==========================================
col_e1, col_e2, col_e3 = st.columns([1, 6, 1])
with col_e2:
    st.markdown("<h3 style='text-align: center; color: #FFFFFF;'>⚡ Join the Newsletter</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #9BA3AF;'>Get the newest zero-code AI tool sent to your inbox every Sunday.</p>", unsafe_allow_html=True)
    
    with st.form("email_capture_form", clear_on_submit=True):
        email_input = st.text_input("Email Address", placeholder="your.email@example.com", label_visibility="collapsed")
        
        # Anti-Spam Bot Check
        bot_check = st.text_input("Bot Check", placeholder="Prove you're human: What is 3 + 4?", label_visibility="collapsed")
        
        submit_button = st.form_submit_button("Get Free Prompts Weekly", use_container_width=True)
        
        if submit_button:
            # 1. Check if they passed the bot test
            if bot_check.strip() != "7":
                st.error("🚨 Bot check failed. Please answer the math question correctly to join.")
            
            # 2. Check if the email is valid
            elif email_input and re.match(r"[^@]+@[^@]+\.[^@]+", email_input):
                if GSheetsConnection is not None:
                    try:
                        conn = st.connection("gsheets", type=GSheetsConnection)
                        existing_data = conn.read(worksheet="Sheet1", usecols=[0, 1])
                        
                        new_row = pd.DataFrame([{
                            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "Email": email_input
                        }])
                        
                        updated_data = pd.concat([existing_data, new_row], ignore_index=True)
                        conn.update(worksheet="Sheet1", data=updated_data)
                        
                        st.success("You're on the list! Welcome to the crew. 🎉")
                        st.balloons()
                    except Exception:
                        st.error("Could not write to Google Sheets. Check your .streamlit/secrets.toml config.")
                else:
                    st.warning("Google Sheets library not detected. Install `st-gsheets-connection` to enable live logging.")
            else:
                st.warning("Please enter a valid email address.")

st.write("")
st.divider()

# ==========================================
# SECTION 4: THE PROMPT VAULT
# ==========================================
st.markdown("<h3 style='text-align: center; color: #FFFFFF;'>The Prompt Vault 🔐</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #9BA3AF; margin-bottom: 1.8rem;'>Copy the exact prompts I use to build my AI tools.</p>", unsafe_allow_html=True)

# Vault Item 1: The Finance Tracker
with st.expander("💸 Low-Stress Finance Tracker (Streamlit + .bat)", expanded=False):
    st.markdown("**Tool Description:** A zero-code local dashboard that automatically funnels income into goal buckets and launches with one click.")
    st.markdown("**The Prompt:**")
    prompt_1 = """Role: You are an expert Python developer and UX/UI designer specializing in automated, low-stress financial tools.
Task: Write a Python script for a "Low-Stress Finance Tracker" using Streamlit, and provide a Windows Batch (.bat) file to run it.
Requirements:
* Tech Stack: Python, Streamlit, and Pandas/JSON for persistent data handling.
* Data Persistence: All entered goals, income, and transactions must be saved automatically to a local file and load on startup.
* Core Features: Clean input forms, automated goal allocation across user-defined buckets, and visual progress with positive reinforcement (use st.progress and st.balloons).
* One-Click Execution: Provide a run_tracker.bat file so users can launch it with a double-click without opening a terminal.
* Design Philosophy: Welcoming, clean, and focused on progress rather than strict restrictions.
Please provide the complete app.py code, the run_tracker.bat code, and brief step-by-step setup instructions."""
    st.code(prompt_1, language="markdown")

# Vault Item 2: Subscriptions Tracker
with st.expander("💳 Zombie Bills & Subscription Killer", expanded=False):
    st.markdown("**Tool Description:** A clean dashboard to track recurring subscriptions and flag upcoming renewal cutoffs.")
    st.markdown("**The Prompt:**")
    prompt_2 = """Role: You are an expert Python and Streamlit developer.
Task: Build a "Subscription & Recurring Expense Tracker" dashboard.
Requirements:
* Show total monthly and yearly recurring costs in prominent metrics.
* List all subscriptions with next billing date and a countdown badge.
* Save all entries to a local JSON file so data persists across sessions.
* Provide a one-click .bat launch file."""
    st.code(prompt_2, language="markdown")

# Vault Item 3: Auto Desktop Organizer
with st.expander("📁 Desktop & Downloads Auto-Organizer", expanded=False):
    st.markdown("**Tool Description:** A single-click script that cleans messy desktop folders into organized categories.")
    st.markdown("**The Prompt:**")
    prompt_3 = """Role: You are a Python automation specialist.
Task: Write a Python script and a .bat file to automatically organize a user's Desktop or Downloads folder.
Requirements:
* Sort files by extension into subfolders: /Images, /Documents, /Spreadsheets, /Installers, /Archives.
* Ignore shortcut files (.lnk, .url) and existing directories.
* Execute silently in under 2 seconds when double-clicking organize.bat."""
    st.code(prompt_3, language="markdown")

# Vault Item 4: Website Generator Prompt
with st.expander("💻 The 5-Minute AI Website Prompt", expanded=False):
    st.markdown("**Tool Description:** The exact prompt used to generate the sleek, dark-mode BuildWithNin landing page with an email capture form.")
    st.markdown("**The Prompt:**")
    prompt_4 = """Role: You are an expert Python developer and UI/UX designer.
Task: Write a single-page website using Python and Streamlit.
Requirements:
* Design: Dark mode background (#16191D) with cyber-neon green accents (#8AE917). Hide default Streamlit menus using CSS. 
* Sections: A hero section with an image logo and social links. An email capture form that drops balloons on success. A "Prompt Vault" using st.expander to hide/reveal text.
* Database: Include the boilerplate code to connect the email form to a Google Sheet using st.connection."""
    st.code(prompt_4, language="markdown")

st.write("")
st.markdown("<p style='text-align: center; color: #556070; font-size: 0.8rem;'>© 2026 BuildWithNin. All rights reserved.</p>", unsafe_allow_html=True)
