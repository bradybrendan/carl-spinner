# typed_view.py

import streamlit as st
from utils import get_carl_sass


def show_typed_input():
    if "typed_meals" not in st.session_state:
        st.session_state.typed_meals = []

    if "spin_history" not in st.session_state:
        st.session_state.spin_history = []

    if st.session_state.result_mode != "typed":
        if st.button("🔙 Go Back"):
            st.session_state.mode = None
            st.rerun()

        with st.form("typed_form", clear_on_submit=True):
            typed = st.text_input("Enter a meal or cuisine:")
            if st.form_submit_button("Add") and typed:
                st.session_state.typed_meals.append(typed)
                st.success(f"Added: {typed}")

        if st.session_state.typed_meals:
            st.markdown("### Your entries:")
            st.markdown(" ".join([f"<code>{m}</code>" for m in st.session_state.typed_meals]), unsafe_allow_html=True)

            if st.button("🎯 Spin with Carl!"):
                if len(st.session_state.typed_meals) < 2:
                    st.warning("Please add at least two meal options for better randomness.")
                else:
                    import random
                    meal_options = st.session_state.typed_meals.copy()
                    random.shuffle(meal_options)
                    new_result = meal_options[0]
                    attempts = 0
                    while (
                        "last_result" in st.session_state
                        and new_result == st.session_state.last_result
                        and attempts < 5
                    ):
                        random.shuffle(meal_options)
                        new_result = meal_options[0]
                        attempts += 1

                    st.session_state.last_result = new_result
                    st.session_state.spin_history.insert(0, new_result)
                    st.session_state.spin_history = st.session_state.spin_history[:5]
                    st.session_state.result_mode = "typed"
                    st.session_state.result_sass = get_carl_sass(new_result)
                    st.session_state.mode = "results"  # 👈 NEW LINE to trigger results page
                    st.rerun()

            if st.button("Clear List"):
                st.session_state.typed_meals = []
