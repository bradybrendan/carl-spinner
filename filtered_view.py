import streamlit as st
import random
from utils import get_carl_sass, search_places

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
    price_map = {"$": 0, "$$": 1, "$$$": 2, "$$$$": 3}
    price_symbol = st.select_slider("Price range", options=["$", "$$", "$$$", "$$$$"], value="$$")
    price_level = price_map[price_symbol]

    delivery = st.selectbox("Dining method:", ["Any", "Delivery", "Pickup"])  # Currently unused with Google API
    distance_label = st.selectbox("Distance (miles):", ["30", "15", "10", "5", "2", "1"], index=2)
    distance = int(distance_label)

    if st.button("🎯 Let Carl Pick!"):
        keyword = ", ".join(selected_cuisines) if selected_cuisines else "restaurants"

        with st.spinner("Carl is flapping around the web..."):
            results = search_places(
                zip_code=zip_code,
                radius_miles=distance,
                keyword=keyword,
                price_level=price_level
            )
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
            st.session_state.result_sass = get_carl_sass(best["name"])
            st.session_state.mode = "results"
            st.rerun()
        else:
            st.warning("Carl couldn’t find any good spots. Try a wider search.")
