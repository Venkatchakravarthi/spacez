import streamlit as st
import pandas as pd
import re
from collections import Counter

st.set_page_config(page_title="Spacez Review Intelligence", layout="wide")
st.title("🏡 Spacez Review Intelligence — Caretaker Control Dashboard")

uploaded_file = st.sidebar.file_uploader("Upload Reviews Excel File", type=["xlsx"])

# ---------------------------
# NORMALIZATION
# ---------------------------

def normalize_rating(platform, rating):
    if platform.lower() == "booking.com":
        return rating * 10
    else:
        return rating * 20

# ---------------------------
# THEME RULE ENGINE
# ---------------------------

THEME_RULES = {
    "cleanliness": ["dirty", "unclean", "dust", "stain", "smell", "filthy"],
    "check_in": ["late", "delay", "waited", "check in", "check-in"],
    "pool": ["pool", "water temperature"],
    "heating": ["heater", "heating", "cold"],
    "wifi": ["wifi", "internet", "connection"],
    "road_access": ["road", "approach", "difficult to reach"],
    "policy_issue": ["policy", "rules", "occupancy"],
    "noise_low_signal": ["amazing", "great stay", "nice place"]
}

CARETAKER_CONTROLLED = [
    "cleanliness",
    "check_in"
]

PROPERTY_CONTROLLED = [
    "pool",
    "heating",
    "wifi",
    "road_access"
]

POLICY_CONTROLLED = [
    "policy_issue"
]

# ---------------------------
# ANALYSIS ENGINE
# ---------------------------

def extract_themes(review):
    review_lower = review.lower()
    themes_found = []
    for theme, keywords in THEME_RULES.items():
        for word in keywords:
            if word in review_lower:
                themes_found.append(theme)
                break
    return list(set(themes_found))

def classify_controllability(themes):
    controllable = []
    not_controllable = []
    for theme in themes:
        if theme in CARETAKER_CONTROLLED:
            controllable.append(theme)
        else:
            not_controllable.append(theme)
    return controllable, not_controllable

def severity_score(normalized_score):
    if normalized_score >= 80:
        return 1
    elif normalized_score >= 60:
        return 2
    elif normalized_score >= 40:
        return 3
    elif normalized_score >= 20:
        return 4
    else:
        return 5

# ---------------------------
# MAIN LOGIC
# ---------------------------

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    df["Normalized Score"] = df.apply(
        lambda row: normalize_rating(row["Platform"], row["Rating"]), axis=1
    )

    caretaker = st.selectbox("Select Caretaker", df["Caretaker"].unique())
    caretaker_df = df[df["Caretaker"] == caretaker]

    results = []

    for _, row in caretaker_df.iterrows():
        themes = extract_themes(row["Review"])
        controllable, not_controllable = classify_controllability(themes)
        severity = severity_score(row["Normalized Score"])

        results.append({
            "Property": row["Property"],
            "Themes": themes,
            "Controllable": controllable,
            "Not Controllable": not_controllable,
            "Severity": severity
        })

    result_df = pd.DataFrame(results)

    # ---------------------------
    # DASHBOARD OUTPUT
    # ---------------------------

    st.header("📊 Caretaker Influence Summary")

    total_reviews = len(result_df)
    total_controllable = sum(len(x) for x in result_df["Controllable"])
    total_not_controllable = sum(len(x) for x in result_df["Not Controllable"])

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Reviews", total_reviews)
    col2.metric("Caretaker-Controllable Mentions", total_controllable)
    col3.metric("Not Your Responsibility Mentions", total_not_controllable)

    # Recurring controllable themes
    st.subheader("🔁 Recurring Caretaker-Controlled Issues")

    all_controllable = []
    for themes in result_df["Controllable"]:
        all_controllable.extend(themes)

    theme_counts = Counter(all_controllable)
    recurring = {k: v for k, v in theme_counts.items() if v > 1}

    if recurring:
        st.write(recurring)
    else:
        st.write("No recurring caretaker-controlled patterns detected.")

    # Pattern following caretaker across properties
    st.subheader("🧠 Cross-Property Pattern Detection")

    pattern_property_map = {}
    for _, row in result_df.iterrows():
        for theme in row["Controllable"]:
            if theme not in pattern_property_map:
                pattern_property_map[theme] = set()
            pattern_property_map[theme].add(row["Property"])

    cross_property_patterns = {
        theme: props
        for theme, props in pattern_property_map.items()
        if len(props) > 1
    }

    if cross_property_patterns:
        for theme, props in cross_property_patterns.items():
            st.warning(f"{theme} appears across properties: {list(props)}")
    else:
        st.success("No cross-property behavioral pattern detected.")

    # Not your responsibility section
    st.subheader("🛡 Not Your Responsibility")

    all_not_controllable = []
    for themes in result_df["Not Controllable"]:
        all_not_controllable.extend(themes)

    not_counts = Counter(all_not_controllable)

    if not_counts:
        st.write(dict(not_counts))
    else:
        st.write("No external issues detected.")

    # Raw view
    with st.expander("See Detailed Breakdown"):
        st.dataframe(result_df)
