import streamlit as st
import requests

from database import init_db, save_results, load_history

API_URL = "http://127.0.0.1:8000/analyze"

init_db()

st.set_page_config(page_title="Customer Feedback Analyzer", page_icon="📊")
st.title("📊 Customer Feedback Analyzer")
st.write("Paste customer reviews below (one review per line) and click **Analyze**.")

if "results" not in st.session_state:
    st.session_state.results = []

reviews_text = st.text_area("Reviews", height=200, placeholder="One review per line...")

if st.button("Analyze"):
    reviews = [line.strip() for line in reviews_text.splitlines() if line.strip()]

    if not reviews:
        st.warning("Please enter at least one review.")
    else:
        results = []
        with st.spinner(f"Analyzing {len(reviews)} review(s)..."):
            for review in reviews:
                response = requests.post(API_URL, json={"text": review})
                if response.status_code == 200:
                    analysis = response.json()
                    results.append(
                        {
                            "review": review,
                            "label": analysis["label"],
                            "score": analysis["score"],
                            "theme": analysis["theme"],
                        }
                    )
                else:
                    st.error(f"Failed to analyze review: {review}")
        st.session_state.results = results

if st.session_state.results:
    st.subheader("Results")
    st.table(st.session_state.results)

    total = len(st.session_state.results)
    avg_score = sum(r["score"] for r in st.session_state.results) / total
    positive_pct = (
        sum(1 for r in st.session_state.results if r["label"] == "positive") / total * 100
    )

    st.subheader("Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total reviews", total)
    col2.metric("Average score", f"{avg_score:.1f}")
    col3.metric("Positive %", f"{positive_pct:.0f}%")

    if st.button("Save to database"):
        save_results(st.session_state.results)
        st.success("Saved to database!")

st.divider()
st.subheader("Saved history")

if st.button("Load history"):
    history = load_history()
    if history:
        st.table(history)
    else:
        st.info("No saved reports yet.")
