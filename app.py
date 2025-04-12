import streamlit as st
import random
import time
import openai
import re
import requests

# API KEYS
openai.api_key = st.secrets["OPENAI_API_KEY"]
YELP_API_KEY = st.secrets["YELP_API_KEY"]

st.set_page_config(page_title="What to Eat Spinner", page_icon="🥜", layout="centered")

# ------------------------------
# Styling
# ------------------------------
st.markdown("""
    <style>
    body { background-color: #6BA368; }
    .stApp { background-color: #6BA368; color: black; text-align: center; font-size: 18px; }
    h1, h2, h3, h4 { text-align: center; font-size: 32px; }
    .highlight-meal { color: #004AAD; font-weight: bold; }
    .stButton>button {
        background-color: #c1121f;
        color: white;
        font-size: 22px;
        border-radius: 16px;
        padding: 1em 2em;
        font-weight: bold;
        transition: 0.2s ease-in-out;
        margin-top: 1em;
    }
    .stButton>button:hover {
        background-color: white;
        color: #c1121f;
        transform: scale(1.05);
    }
    .result-card {
        background-color: #fff;
        color: black;
        border-radius: 12px;
        padding: 1em;
        margin: 1em;
        box-shadow: 0px 4px 8px rgba(0,0,0,0.2);
    }
    .runner-row {
        display: flex;
        justify-content: center;
        gap: 2em;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------------
# GPT Sass Generator
# ------------------------------
def get_carl_sass(term):
    prompt = (
        f"You are Cardinal Carl, a sarcastic but lovable bird. "
        f"Someone spun the wheel and landed on '{term}'. "
        f"Write one short, witty, sassy sentence to convince them it's the right choice. "
        f"Mention the term and make it under 30 words."
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=60
        )
        sass = response.choices[0].message["content"]
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        if not pattern.search(sass):
            sass = f"Yeah, just go with <span class='highlight-meal'>{term}</span>. Even I’d eat that."
        else:
            sass = pattern.sub(f"<span class='highlight-meal'>{term}</span>", sass)
        return sass
    except Exception as e:
        st.error(f"Carl Error: {e}")
        return "Carl lost his voice. Try again."

# ------------------------------
# Yelp Search
# ------------------------------
def search_yelp(term, zip_code, radius_miles=10, price="1,2,3,4", attributes=None):
    headers = {"Authorization": f"Bearer {YELP_API_KEY}"}
    params = {
        "term": term,
        "location": zip_code,
        "radius": int(radius_miles * 1609.34),
        "limit": 10,
        "price": price,
        "open_now": True
    }
    if attributes and attributes != "Any":
        params["attributes"] = attributes.lower()

    response = requests.get("https://api.yelp.com/v3/businesses/search", headers=headers, params=params)
    data = response.json()
    return data.get("businesses", [])

# ------------------------------
# App UI
# ------------------------------
st.title("What to Eat Spinner")
st.markdown("Guided by <strong>Cardinal Carl 🐦</strong>", unsafe_allow_html=True)

if "mode" not in st.session_state:
    st.session_state.mode = None

zip_code = st.text_input("Enter your ZIP code:", max_chars=10, value="02492")

if st.session_state.mode is None:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💬 I'll type in my choices"):
            st.session_state.mode = "typed"
    with col2:
        if st.button("🎯 Let Carl decide for me"):
            st.session_state.mode = "filtered"

elif st.session_state.mode == "typed":
    if st.button("🔙 Go Back"):
        st.session_state.mode = None

    if "typed_meals" not in st.session_state:
        st.session_state.typed_meals = []

    with st.form("typed_form", clear_on_submit=True):
        typed = st.text_input("Enter meal, cuisine, or restaurant:")
        if st.form_submit_button("Add") and typed:
            st.session_state.typed_meals.append(typed)
            st.success(f"Added: {typed}")

    if st.session_state.typed_meals:
        st.markdown("### Your entries:")
        st.markdown(" ".join([f"<code>{m}</code>" for m in st.session_state.typed_meals]), unsafe_allow_html=True)

        if st.button("🎯 Spin!"):
            winner = random.choice(st.session_state.typed_meals)
            sass = get_carl_sass(winner)
            st.markdown(f"<h2>🐦💬 {sass}</h2>", unsafe_allow_html=True)
            with st.spinner("Fetching real nearby spots..."):
                results = search_yelp(winner, zip_code)
            if results:
                st.markdown("### Nearby options:")
                for place in results[:3]:
                    name = place["name"]
                    rating = place["rating"]
                    address = ", ".join(place["location"]["display_address"])
                    st.markdown(f"<div class='result-card'>**{name}**<br>\n🌟 {rating} stars<br>\n🏬 {address}<br>\n<a href='{place['url']}' target='_blank'>View on Yelp</a></div>", unsafe_allow_html=True)
            else:
                st.warning("Carl came up empty. Try again!")

        if st.button("Clear List"):
            st.session_state.typed_meals = []

elif st.session_state.mode == "filtered":
    if st.button("🔙 Go Back"):
        st.session_state.mode = None

    cuisine_options = [
        "American", "BBQ", "Bakery", "Brazilian", "Breakfast", "Brunch", "Burgers", "Cafe", "Cajun",
        "Caribbean", "Chinese", "Colombian", "Cuban", "Deli", "Diner", "Ethiopian", "Fast Food",
        "Filipino", "French", "Gastropub", "German", "Greek", "Halal", "Hawaiian", "Healthy",
        "Indian", "Indonesian", "Irish", "Italian", "Japanese", "Jewish", "Korean", "Latin American",
        "Lebanese", "Malaysian", "Mediterranean", "Mexican", "Middle Eastern", "Nigerian", "Pakistani",
        "Peruvian", "Pizza", "Polish", "Portuguese", "Pub", "Ramen", "Russian", "Sandwiches", "Seafood",
        "Soul Food", "Southern", "Spanish", "Steak", "Sushi", "Taiwanese", "Tex-Mex", "Thai",
        "Turkish", "Vegan", "Vegetarian", "Vietnamese"
    ]
    selected_cuisines = st.multiselect("Pick cuisines (type to search):", options=cuisine_options)
    price_map = {"$": "1", "$$": "2", "$$$": "3", "$$$$": "4"}
    price = st.select_slider("Price range", options=["$", "$$", "$$$", "$$$$"], value="$$")
    delivery = st.selectbox("Dining method:", ["Any", "Delivery", "Pickup"])
    distance_label = st.selectbox("Distance:", ["30", "15", "10", "5", "2", "1"], index=2)
    distance = int(distance_label)

    if st.button("🎯 Let Carl Pick!"):
        search_term = ", ".join(selected_cuisines) if selected_cuisines else "restaurants"
        with st.spinner("Carl is flapping around Yelp..."):
            results = search_yelp(search_term, zip_code, distance, price_map[price], delivery)

        if results:
            best = results[0]
            runners_up = results[1:3]
            best_sass = get_carl_sass(best["name"])

            st.balloons()
            st.markdown(f"<h2>🐦💬 {best_sass}</h2>", unsafe_allow_html=True)
            name = best["name"]
            rating = best["rating"]
            address = ", ".join(best["location"]["display_address"])
            st.markdown(f"<div class='result-card'><strong>🏆 Top Pick: {name}</strong><br>\n🌟 {rating} stars<br>\n🏬 {address}<br>\n<a href='{best['url']}' target='_blank'>View on Yelp</a></div>", unsafe_allow_html=True)

            if runners_up:
                st.markdown("### Runners-up:")
                st.markdown("<div class='runner-row'>", unsafe_allow_html=True)
                for place in runners_up:
                    name = place["name"]
                    rating = place["rating"]
                    address = ", ".join(place["location"]["display_address"])
                    st.markdown(f"<div class='result-card'><strong>{name}</strong><br>\n🌟 {rating} stars<br>\n🏬 {address}<br>\n<a href='{place['url']}' target='_blank'>View on Yelp</a></div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("Carl couldn’t find any good spots. Try a wider search.")
