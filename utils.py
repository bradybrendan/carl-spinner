# utils.py
import openai
import re
import requests
import streamlit as st

openai.api_key = st.secrets["OPENAI_API_KEY"]
YELP_API_KEY = st.secrets["YELP_API_KEY"]

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
