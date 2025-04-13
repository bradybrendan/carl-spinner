# filtered_view.py
import streamlit as st
import random
from utils import get_carl_sass, search_yelp  # make sure this is correct in your setup

def show_filtered_input(zip_code):
    if st.button("🔙 Go Back"):
        st.session_state.mode = None
        st.session_state.result_mode = None
        st.rerun()

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

    st.markdown("### What’s your vibe today?")
    selected_cuisines = st.multiselect("Pick cuisines (type to search):", options=cuisine_options)
    price_map = {"$": "1", "$$": "2", "$$$": "3", "$$$$": "4"}
    price = st.select_slider("Price range", options=["$", "$$", "$$$", "$$$$"], value="$$")
    delivery = st.selectbox("Dining method:", ["Any", "Delivery", "Pickup"])
    distance_label = st.selectbox("Distance (miles):", ["30", "15", "10", "5", "2", "1"], index=2)
    distance = int(distance_label)

    if st.button("🎯 Let Carl Pick!"):
        search_term = ", ".join(selected_cuisines) if selected_cuisines else "restaurants"
        zip_code = st.session_state.get("zip_code", "02492")
        with st.spinner("Carl is flapping around Yelp..."):
            results = search_yelp(search_term, zip_code, distance, price_map[price], delivery)
            random.shuffle(results)

        if results:
            best = results[0]
            runners_up = results[1:3]

            st.session_state.last_result = best["name"]
            st.session_state.spin_history.insert(0, best["name"])
            st.session_state.spin_history = st.session_state.spin_history[:5]
            st.session_state.result_data = {
                "best": best,
                "runners_up": runners_up,
            }
            st.session_state.result_mode = "filtered"
            st.session_state.result_sass = get_carl_sass(best["name"])  # <--- Add this
            st.session_state.mode = "results"
            st.rerun()


        else:
            st.warning("Carl couldn’t find any good spots. Try a wider search.")
