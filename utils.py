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


#def search_yelp(term, zip_code, radius_miles=10, price="1,2,3,4", attributes=None):
#    headers = {"Authorization": f"Bearer {YELP_API_KEY}"}
#    params = {
#        "term": term,
#        "location": zip_code,
#        "radius": int(radius_miles * 1609.34),
#        "limit": 10,
#        "price": price,
#        "open_now": True
#    }
#    if attributes and attributes != "Any":
#        params["attributes"] = attributes.lower()

#    response = requests.get("https://api.yelp.com/v3/businesses/search", headers=headers, params=params)
#    st.write("Yelp Status Code:", response.status_code)
#    if response.status_code != 200:
#        st.error(f"Yelp Error: {response.text}")
#    data = response.json()
#    return data.get("businesses", [])
import requests
import streamlit as st

def search_places(zip_code, radius_miles=10, keyword=None, price_level=None):
    api_key = st.secrets["GOOGLE_PLACES_API_KEY"]

    # Convert ZIP code to lat/lng
    geo_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={zip_code}&key={api_key}"
    geo_response = requests.get(geo_url).json()
    if not geo_response["results"]:
        st.error("Invalid ZIP code.")
        return []

    location = geo_response["results"][0]["geometry"]["location"]
    lat, lng = location["lat"], location["lng"]

    # Build Places API query
    radius = int(radius_miles * 1609.34)
    places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "type": "restaurant",
        "key": api_key
    }

    if keyword:
        params["keyword"] = keyword
    if price_level:
        params["maxprice"] = price_level  # Google uses 0 (cheapest) to 4 (most expensive)

    response = requests.get(places_url, params=params)
    st.write("Google Places Status Code:", response.status_code)
    if response.status_code != 200:
        st.error(f"Places API error: {response.text}")
        return []

    return response.json().get("results", [])

def get_recipe_steps(term):
    prompt = f"Suggest a fun and practical recipe someone could try at home using {term}. Write in 3-6 clear steps."

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful home cook sharing easy, fun recipe steps."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.7,
    )

    recipe = response.choices[0].message["content"]
    steps = [step.strip("• ").strip() for step in recipe.split("\n") if step.strip()]
    return steps



