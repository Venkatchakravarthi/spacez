import streamlit as st
import pandas as pd
import json
from collections import Counter
import openai

st.set_page_config(page_title="Spacez Review Intelligence", layout="wide")

st.title("🏡 Spacez Review Intelligence — Caretaker Dashboard")

st.sidebar.header("Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload Reviews Excel File", type=["xlsx"])

openai.api_key = st.sidebar.text_input("Enter OpenAI API Key", type="password")

def normalize_rating(row):
    if row["Platform"] == "Booking.com":
        return row["Rating"] * 10
    else:
        return row["Rating"] * 20

def analyze_review(review_text):
    prompt = f"""
    You are a hospitality analyst.
    Analyze this review and return JSON:

    {{
        "themes": [],
        "controllability": "caretaker/property/vendor/policy/uncontrollable",
        "severity": 1-5,
        "caretaker_action_required": true/false,
        "recommended_action": ""
    }}

    Review:
    {review_text}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return json.loads(response["choices"][0]["message"]["content"])

if uploaded_file and openai.api_key:
    df = pd.read_excel(uploaded_file)

    df["Normalized Score"] = df.apply(normalize_rating, axis=1)

    st.subheader("Select Caretaker")
    caretaker = st.selectbox("Caretaker", df["Caretaker"].unique())

    caretaker_df = df[df["Caretaker"] == caretaker]

    results = []
    for _, row in caretaker_df.iterrows():
        analysis = analyze_review(row["Review"])
        analysis["Property"] = row["Property"]
        analysis["Normalized Score"] = row["Normalized Score"]
        results.append(analysis)

    result_df = pd.DataFrame(results)

    st.subheader("📊 Caretaker Influence Summary")

    controllable = result_df[result_df["controllability"] == "caretaker"]
    not_controllable = result_df[result_df["controllability"] != "caretaker"]

    st.metric("Total Reviews", len(result_df))
    st.metric("Caretaker-Controllable Issues", len(controllable))
    st.metric("Not Caretaker Responsibility", len(not_controllable))

    st.subheader("🔁 Recurring Controllable Themes")

    all_themes = []
    for themes in controllable["themes"]:
        all_themes.extend(themes)

    theme_counts = Counter(all_themes)
    recurring = {k: v for k, v in theme_counts.items() if v > 1}

    if recurring:
        st.write(recurring)
    else:
        st.write("No recurring caretaker-controlled issues.")

    st.subheader("🎯 Recommended Actions")
    for action in controllable["recommended_action"]:
        st.write("-", action)

    st.subheader("🛡 Not Your Responsibility")
    for theme in not_controllable["themes"]:
        st.write("-", theme)
