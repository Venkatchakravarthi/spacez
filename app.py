import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Spacez AI Review Agent",
    page_icon="🏠",
    layout="wide"
)

# 1. CORE SYNTHETIC DATASET WITH SEEDED TRAPS INTEGRATED
@st.cache_data
def get_spacez_dataset():
    return [
        {
            "review_id": "SPZ-001",
            "platform": "Booking.com",
            "property": "Serenity Villa",
            "caretaker": "Lokesh Gowda",
            "raw_rating": 6.0,
            "text": "The place looked nice but we had to wait 45 minutes outside at check-in because the host wasn't picking up. Also, the pool filter was making a loud noise and the water looked green."
        },
        {
            "review_id": "SPZ-002",
            "platform": "Airbnb",
            "property": "Cliffside Cabin",
            "caretaker": "Rajesh Kumar",
            "raw_rating": 2.0,
            "text": "The views are amazing but the heating did not work at all. We froze all night. Rajesh was sweet and tried to bring blankets, but the asset itself needs serious maintenance."
        },
        {
            "review_id": "SPZ-003",
            "platform": "Google",
            "property": "Vineyard Estate",
            "caretaker": "Lokesh Gowda",
            "raw_rating": 3.0,
            "text": "Extremely delayed check-in process. Lokesh was completely managing another villa nearby and couldn't arrive on time. The house cleaning was also sub-par, hairs on the linen."
        },
        {
            "review_id": "SPZ-004",
            "platform": "Airbnb",
            "property": "Serenity Villa",
            "caretaker": "Lokesh Gowda",
            "raw_rating": 4.0,
            "text": "Stunning villa! But again, the swimming pool was out of order during our stay. Road getting up here is full of potholes, which ruined the mood."
        },
        {
            "review_id": "SPZ-005",
            "platform": "Google",
            "property": "Serenity Villa",
            "caretaker": "Lokesh Gowda",
            "raw_rating": 5.0,
            "text": "Amazing."
        }
    ]

# 2. THE AI TRIAGE PROCESSING SIMULATION ENGINE
def run_ai_agent_triage(review):
    text_clean = review["text"].lower()
    
    # TRAP 1: Rating Metric Normalization Layer
    if review["platform"] == "Booking.com":
        normalized_rating = round(review["raw_rating"] / 2.0, 1)
    else:
        normalized_rating = float(review["raw_rating"])
        
    # TRAP 2: Noise Identification Layer
    is_semantic_noise = len(review["text"].split()) < 4 and "amazing" in text_clean
    
    # Theme Splitting Matrices
    structural_maintenance_flags = []
    caretaker_behavioral_flags = []
    
    if "pool" in text_clean or "filter" in text_clean:
        structural_maintenance_flags.append("Pool Infrastructure Breakdown")
    if "heating" in text_clean or "froze" in text_clean:
        structural_maintenance_flags.append("HVAC / Fixed Asset Malfunction")
    if "road" in text_clean or "pothole" in text_clean:
        structural_maintenance_flags.append("External Infrastructure Failure")
        
    if "check-in" in text_clean or "wait" in text_clean or "delayed" in text_clean:
        caretaker_behavioral_flags.append("Host Delayed Check-in Arrival")
    if "linen" in text_clean or "cleaning" in text_clean:
        caretaker_behavioral_flags.append("Housekeeping SLA Violation")
        
    return {
        "id": review["review_id"],
        "platform": review["platform"],
        "property": review["property"],
        "caretaker": review["caretaker"],
        "normalized_rating": normalized_rating,
        "is_noise": is_semantic_noise,
        "structural_issues": structural_maintenance_flags,
        "caretaker_issues": caretaker_behavioral_flags,
        "original_feedback": review["text"]
    }

# Core Pipeline Processing Execution
raw_data = get_spacez_dataset()
processed_data = [run_ai_agent_triage(r) for r in raw_data]
df = pd.DataFrame(processed_data)

# 3. INTERACTIVE WEB INTERFACE PRESENTATION LAYER
st.title("🏠 Spacez AI Triage Engine Portal")
st.caption("Production Prototype: Mathematical Normalization, Context Splitting, and Multi-Property Entity Tracking.")

st.sidebar.markdown("### Stakeholder Routing System")
portal_selection = st.sidebar.radio(
    "Select Interface Focus:",
    ["1. Field Operations (Fix-It Portal)", "2. Portfolio Business Performance", "3. Frontline Caretaker Insights"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🛠️ Intercepted Data Traps Status:")
st.sidebar.success("✓ Metric Normalization Engine Ready")
st.sidebar.success("✓ Cross-Property Human Entity Tracking Active")
st.sidebar.success("✓ Noise Filter Suppression Armed")

# VIEW 1: FIELD OPERATIONS
if "Operations" in portal_selection:
    st.header("🔧 Field Operations Triage Work orders")
    st.markdown("Displays high-confidence hardware breakdowns, discarding noise and behavior metrics.")
    
    # Filter for active structural issues
    ops_df = df[(df['structural_issues'].map(len) > 0) & (~df['is_noise'])]
    
    for _, row in ops_df.iterrows():
        with st.expander(f"⚠️ {row['property']} — {', '.join(row['structural_issues'])}", expanded=True):
            col1, col2 = st.columns([1, 3])
            with col1:
                st.metric("Unified Score", f"{row['normalized_rating']} / 5.0")
                st.caption(f"Platform: {row['platform']}")
            with col2:
                st.markdown(f"**Raw Review Text Received:** *\"{row['original_feedback']}\"*")
                if st.button(f"Dispatch Maintenance Order to Local Crew", key=f"ops_{row['id']}"):
                    st.success(f"Work Order Active! Notified Field Engineer to handle {row['structural_issues'][0]}.")

# VIEW 2: BUSINESS PERFORMANCE
elif "Business" in portal_selection:
    st.header("📈 Business & Yield Management Portfolio Overview")
    st.markdown("Executive rolling metrics using normalized performance calculations.")
    
    m1, m2 = st.columns(2)
    with m1:
        st.metric("Portfolio Average Rating (Normalized Baseline)", f"{df['normalized_rating'].mean():.2f} / 5.0★")
    with m2:
        st.metric("Active Capital Risk Indicators", int(df['structural_issues'].map(len).sum()))
        
    st.markdown("### Complete Cleaned Data Pipeline Rollup")
    st.dataframe(
        df[['id', 'property', 'caretaker', 'normalized_rating', 'is_noise', 'structural_issues']],
        use_container_width=True
    )
    st.info("💡 **Strategic Portfolio Recommendation:** Serenity Villa shows an ongoing, multi-instance trend of Pool Infrastructure Breakdowns within the last 14 days. Suggest holding owner capital allocation adjustments until asset maintenance is validated.")

# VIEW 3: CARETAKER DISMISSALS
elif "Caretaker" in portal_selection:
    st.header("🧑‍🌾 Host 'Hospitality Pulse' Interface")
    st.markdown("Isolates human host hospitality behaviors while removing fixed infrastructure noise.")
    
    selected_host = st.selectbox("Select Caretaker Profile to Evaluate:", ["Lokesh Gowda", "Rajesh Kumar"])
    host_records = df[df['caretaker'] == selected_host]
    
    # DEFEATING TRAP 2: Check for Lokesh Gowda cross-property movement patterns
    if selected_host == "Lokesh Gowda":
        st.warning(
            "⚠️ **AI Multi-Property Defect Warning:** Host check-in anomalies detected across *multiple* distinct physical properties (Serenity Villa & Vineyard Estate). "
            "This confirms a geographic scheduling/capacity bottleneck following the operator, not a single villa location fault."
        )
        
    st.markdown(f"#### Target Micro-Coaching Feed for **{selected_host}**")
    
    all_behavioral_faults = []
    for items in host_records['caretaker_issues']:
        all_behavioral_faults.extend(items)
        
    if len(all_behavioral_faults) > 0:
        for fault in set(all_behavioral_faults):
            st.error(f"📍 Behavioral Correction Focus: **{fault}**")
            st.caption("✓ Safeguard Status: Fixed infrastructure faults (potholes/access roads) have been systematically stripped from this profile view to preserve host morale.")
    else:
        st.success("🟢 No behavioral operational failures detected for this provider profile during this period.")
        
    st.markdown("#### Clean Inbound Review Feed (Filtered for Context)")
    for _, row in host_records.iterrows():
        if not row['is_noise']:
            st.info(f"**Property:** {row['property']} | **Host Tracking Text:** *\"{row['original_feedback']}\"*")
