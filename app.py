import streamlit as st
import random
import openai
import re
import requests
from PIL import Image

# Modular components
# Modular components
from typed_view import show_typed_input
from filtered_view import show_filtered_input
from results_view import show_results_view


# API KEYS
openai.api_key = st.secrets["OPENAI_API_KEY"]


st.set_page_config(page_title="Carl's Cravings", page_icon="🐦", layout="centered")

# ------------------------------
# Styling
# ------------------------------
st.markdown("""
    <style>
    body { background-color: #000000; }
    .stApp {
        background-color: #000000;
        color: white;
        font-family: 'Arial', sans-serif;
        text-align: center;
    }
    h1, h2, h3, h4 {
        color: #ffffff;
        text-align: center;
    }
    .highlight-meal {
        color: #ff4d4d;
        font-weight: bold;
    }
    .stButton>button {
        background-color: #c1121f;
        color: white;
        font-size: 22px;
        border-radius: 16px;
        padding: 1em 2em;
        font-weight: bold;
        transition: 0.2s ease-in-out;
        margin-top: 1em;
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    .stButton>button:hover {
        background-color: white;
        color: #c1121f;
        border: 2px solid #c1121f;
        transform: scale(1.05);
    }
    .result-card {
        background-color: #1a1a1a;
        color: white;
        border-radius: 12px;
        padding: 1em;
        margin: 1em auto;
        max-width: 600px;
        box-shadow: 0px 4px 12px rgba(255,255,255,0.1);
    }
    .runner-row {
        display: flex;
        justify-content: center;
        gap: 2em;
        flex-wrap: wrap;
    }
    label, .stTextInput > div > label, .stSelectbox > div > label, .stMultiSelect > div > label {
        color: white !important;
    }
    .stForm button {
        background-color: #c1121f !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: bold;
        font-size: 18px;
        margin-top: 10px;
    }
    .stForm button:hover {
        background-color: white !important;
        color: #c1121f !important;
        border: 2px solid #c1121f;
    }
    .spin-history-box {
        background-color: rgba(193, 18, 31, 0.75);
        color: white;
        border-radius: 12px;
        padding: 1.2em 1.5em;
        margin-top: 2em;
        margin-bottom: 1em;
        max-width: 380px;
        margin-left: auto;
        margin-right: auto;
        box-shadow: 0 0 10px rgba(255, 255, 255, 0.1);
        text-align: center;
    }
    .spin-history-box .history-title {
        font-weight: bold;
        font-size: 1.1em;
        margin-bottom: 0.6em;
        display: block;
    }
    .spin-history-box ul {
        list-style-type: disc;
        list-style-position: inside;
        padding-left: 0;
        margin: 0 auto;
        display: block;
        text-align: left;
        max-width: 300px;
    }
    .spin-history-box li {
        margin: 3px 0;
    }
    .recipe-box {
    background-color: rgba(193, 18, 31, 0.75); /* soft red */
    color: white;
    border-radius: 12px;
    padding: 1.5em 2em;
    margin-top: 2em;
    margin-bottom: 1em;
    max-width: 100%;
    width: 100%;
    box-shadow: 0 0 12px rgba(255, 255, 255, 0.1);
    text-align: left;
}
.recipe-box ul {
    list-style-position: inside;
    padding-left: 0;
}
.recipe-box li {
    margin: 0.3em 0;
}


    </style>
""", unsafe_allow_html=True)

st.title("Tell Me What to Eat")
st.markdown(
    "<div style='margin-top: -10px; font-size: 16px; font-weight: 500; color: white;'>"
    "Guided by <strong>Carl 🐦</strong>, your sarcastic food spirit guide."
    "</div>",
    unsafe_allow_html=True
)

# Show Carl Banner Image at the top of the home page
# Remove excess space above
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 3rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)

#from PIL import Image
#banner = Image.open("images/carl-banner.png")
#st.image(banner, use_container_width=True)


# Initialize state
if "mode" not in st.session_state:
    st.session_state.mode = None
if "spin_history" not in st.session_state:
    st.session_state.spin_history = []
if "result_mode" not in st.session_state:
    st.session_state.result_mode = None
if "result_sass" not in st.session_state:
    st.session_state.result_sass = None

if "result_data" not in st.session_state:
    st.session_state.result_data = None


if "zip_code" not in st.session_state:
    st.session_state.zip_code = "02108"

if st.session_state.mode != "results":
    st.session_state.zip_code = st.text_input("Enter your ZIP code:", max_chars=10, value=st.session_state.zip_code)


# Routing
# Routing
if st.session_state.mode is None:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("I'm Cooking"):
            st.session_state.mode = "typed"
            st.session_state.result_mode = None
            st.session_state.result_data = None
            st.session_state.recipe_suggestion = None
            st.session_state.show_recipe = False
            st.rerun()

    with col2:
        if st.button("Find Me A Restaurant"):
            st.session_state.mode = "filtered"
            st.session_state.result_mode = None
            st.session_state.result_data = None
            st.session_state.recipe_suggestion = None
            st.session_state.show_recipe = False
            st.rerun()

elif st.session_state.mode == "typed":
    show_typed_input()

elif st.session_state.mode == "filtered":
    show_filtered_input(st.session_state.zip_code)

elif st.session_state.mode == "results":
    show_results_view()

st.markdown("---")
st.markdown(
    "💬 Got thoughts for Carl? [Leave feedback here](https://docs.google.com/forms/d/e/1FAIpQLSdR4Dz0U0FNw0fEs_ufRxy2nqHNvTbQkA-gNs-hnA3F8pA1zA/viewform?usp=dialog)",
    unsafe_allow_html=True
)


