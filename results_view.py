# results_view.py
import streamlit as st

def show_results_view():
    st.markdown("### Carl’s Pick")
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("images/carl-mascot.png", width=160)
    with col2:
        sass = st.session_state.get("result_sass", "Carl's speechless...")
        st.markdown(f"<p style='font-size: 22px; text-align: left; font-weight: 500;'>{sass}</p>", unsafe_allow_html=True)

    if st.session_state.result_mode == "typed":
        st.markdown(f"<div class='result-card'><strong>{st.session_state.last_result}</strong></div>", unsafe_allow_html=True)

    elif st.session_state.result_mode == "filtered":
        data = st.session_state.result_data
        best = data["best"]
        runners_up = data["runners_up"]

        name = best["name"]
        rating = best["rating"]
        address = ", ".join(best["location"]["display_address"])
        st.markdown(
            f"<div class='result-card'><strong>🏆 Top Pick: {name}</strong><br>🌟 {rating} stars<br>🏬 {address}<br><a href='{best['url']}' target='_blank'>View on Yelp</a></div>",
            unsafe_allow_html=True)

        if runners_up:
            st.markdown("### Runners-up:")
            st.markdown("<div class='runner-row'>", unsafe_allow_html=True)
            for place in runners_up:
                name = place["name"]
                rating = place["rating"]
                address = ", ".join(place["location"]["display_address"])
                st.markdown(
                    f"<div class='result-card'><strong>{name}</strong><br>🌟 {rating} stars<br>🏬 {address}<br><a href='{place['url']}' target='_blank'>View on Yelp</a></div>",
                    unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔁 Spin Again"):
            if st.session_state.result_mode == "typed":
                import random
                from utils import get_carl_sass

                meal_options = st.session_state.typed_meals.copy()
                random.shuffle(meal_options)
                new_result = meal_options[0]
                attempts = 0
                while new_result == st.session_state.last_result and attempts < 5:
                    random.shuffle(meal_options)
                    new_result = meal_options[0]
                    attempts += 1

                st.session_state.last_result = new_result
                st.session_state.spin_history.insert(0, new_result)
                st.session_state.spin_history = st.session_state.spin_history[:5]
                st.session_state.result_sass = get_carl_sass(new_result)
                st.rerun()

            elif st.session_state.result_mode == "filtered":
                import random
                from utils import get_carl_sass, search_yelp

                search_term = ", ".join(st.session_state.get("last_filters", {}).get("cuisines", [])) or "restaurants"
                zip_code = st.session_state.get("last_filters", {}).get("zip_code", "02492")
                distance = st.session_state.get("last_filters", {}).get("distance", 10)
                price = st.session_state.get("last_filters", {}).get("price", "2")
                delivery = st.session_state.get("last_filters", {}).get("delivery", "Any")

                results = search_yelp(search_term, zip_code, distance, price, delivery)
                random.shuffle(results)

                if results:
                    best = results[0]
                    runners_up = results[1:3]
                    st.session_state.last_result = best["name"]
                    st.session_state.spin_history.insert(0, best["name"])
                    st.session_state.spin_history = st.session_state.spin_history[:5]
                    st.session_state.result_data = {
                        "best": best,
                        "runners_up": runners_up
                    }
                    st.session_state.result_sass = get_carl_sass(best["name"])
                    st.rerun()

    with col2:
        if st.button("🔙 Back"):
            st.session_state.mode = None
            st.session_state.result_mode = None
            st.rerun()

    if st.session_state.spin_history:
        st.markdown(
            "<div class='spin-history-box'>"
            "<span class='history-title'>🕘 Recent Spins:</span>"
            "<ul>" +
            "".join([f"<li>{item}</li>" for item in st.session_state.spin_history]) +
            "</ul></div>", unsafe_allow_html=True
        )
