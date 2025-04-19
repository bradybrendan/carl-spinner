# results_view.py

import streamlit as st
import random
from utils import get_carl_sass, search_yelp
import openai



def show_results_view():

    # Slightly smaller buttons in aligned row
    button_cols = st.columns([1, 1])
    with button_cols[0]:
        spin = st.button("🔁 Spin Again", key="spin_top")
    with button_cols[1]:
        back = st.button("🔙 Back", key="back_top")

    if spin:
        if st.session_state.result_mode == "typed":
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
            st.session_state.show_recipe = False

            st.rerun()

        elif st.session_state.result_mode == "filtered":
            search_term = ", ".join(st.session_state.get("last_filters", {}).get("cuisines", [])) or "restaurants"
            zip_code = st.session_state.zip_code
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

    if back:
        st.session_state.mode = None
        st.session_state.result_mode = None
        st.rerun()

    if back:
        st.session_state.mode = None
        st.session_state.result_mode = None
        st.rerun()

    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("images/carl-mascot.png", width=160)
    with col2:
        sass = st.session_state.get("result_sass", "Carl's speechless...")
        st.markdown(f"<p style='font-size: 22px; text-align: left; font-weight: 500;'>{sass}</p>", unsafe_allow_html=True)

        if st.session_state.result_mode == "typed":
            if "show_recipe" not in st.session_state:
                st.session_state.show_recipe = False

            if not st.session_state.show_recipe:
                if st.button("🧑‍🍳 Want a recipe for this?", key="recipe_prompt"):
                    from utils import get_recipe_steps
                    try:
                        steps = get_recipe_steps(st.session_state.last_result)
                        st.session_state.recipe_suggestion = steps
                        st.session_state.show_recipe = True
                        st.rerun()
                    except Exception as e:
                        st.error("Carl forgot the cookbook — try again later.")
            else:
                steps = st.session_state.get("recipe_suggestion", [])
                if steps:
                    formatted_steps = []
                    for step in steps:
                        if step.strip().endswith(":") or step.lower().startswith("recipe:"):
                            # Render bold, unbulleted section headers
                            formatted_steps.append(f"<p><strong>{step.strip()}</strong></p>")
                        else:
                            # Regular bullet point
                            formatted_steps.append(f"<p style='margin: 6px 0;'>{step.strip()}</p>")



                    st.markdown(
                        """
                        <div style='
                            background-color: #8b1f1f;
                            padding: 25px;
                            border-radius: 12px;
                            margin: 25px 0;
                            max-width: 90%;
                            width: 100%;
                            color: white;
                            font-size: 17px;
                            text-align: left;
                        '>
                            <div style='text-align: center; font-weight: 600; font-size: 20px; margin-bottom: 15px;'>
                                👨‍🍳 Carl’s Recipe Suggestion
                            </div>
                            {}
                        </div>
                        """.format("".join(formatted_steps)),
                        unsafe_allow_html=True
                    )


                else:
                    st.warning("Carl couldn't find a recipe. Try again?")

        # Only show restaurant results if we're in filtered mode and result_data exists
        if st.session_state.result_mode == "filtered" and "result_data" in st.session_state:
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

    if st.session_state.spin_history:
        st.markdown(
            "<div class='spin-history-box'>"
            "<span class='history-title'>🕘 Recent Spins:</span>"
            "<ul>" +
            "".join([f"<li>{item}</li>" for item in st.session_state.spin_history]) +
            "</ul></div>", unsafe_allow_html=True
        )
