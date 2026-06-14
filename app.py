import os
import json
import pandas as pd
import streamlit as st
import ollama

# Set page config for a clean, professional dashboard
st.set_page_config(
    page_title="Corvus Bio – Scientific Synthesis & Contradiction Dashboard",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Clean premium styling
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@500;600;700&display=swap" rel="stylesheet">

<style>
    .stApp {
        background: #0E1117;
        color: #E6EDF3;
        font-family: 'Inter', sans-serif;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #D6DCE5;
    }

    h1, h2, h3, h4 {
        font-family: 'Poppins', sans-serif !important;
        color: #F4F7FA !important;
        letter-spacing: -0.5px;
        margin-bottom: 8px;
    }

    h1 {
        font-size: 2.3rem !important;
        font-weight: 700 !important;
    }

    h2 {
        font-size: 1.6rem !important;
        font-weight: 600 !important;
    }

    h3 {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
    }

    p, span, div {
        line-height: 1.7;
    }

    .card {
        background: #161B22;
        border: 1px solid #2B313C;
        border-radius: 18px;
        padding: 24px;
        margin-bottom: 20px;
        transition: all 0.2s ease;
    }

    .card:hover {
        border-color: #3B82F6;
        transform: translateY(-2px);
    }

    .metric-value {
        font-family: 'Poppins', sans-serif;
        font-size: 2.3rem;
        font-weight: 700;
        color: #58A6FF;
        margin-bottom: 4px;
    }

    .metric-label {
        font-size: 0.9rem;
        color: #8B949E;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }

    [data-testid="stSidebar"] {
        background: #11161F !important;
        border-right: 1px solid #222B36;
    }

    [data-testid="stSidebar"] * {
        color: #DDE3EA;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        margin-bottom: 15px;
    }

    .stTabs [data-baseweb="tab"] {
        background: #161B22;
        border: 1px solid #2B313C;
        border-radius: 12px;
        padding: 12px 20px;
        color: #9AA4B2 !important;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        transition: all 0.2s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: #1D2430;
        color: #FFFFFF !important;
    }

    .stTabs [aria-selected="true"] {
        background: #1E293B !important;
        border: 1px solid #3B82F6 !important;
        color: #58A6FF !important;
    }

    .streamlit-expanderHeader {
        font-weight: 600;
        font-size: 1rem;
    }

    [data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid #2B313C;
    }

    .stTextInput input,
    .stSelectbox div,
    .stMultiSelect div {
        border-radius: 10px !important;
        background-color: #161B22 !important;
        color: #E6EDF3 !important;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar - Settings & Actions
st.sidebar.title("🧬 Corvus Bio Controls")
st.sidebar.markdown("---")

DATASET_DIR = "dataset"
CLINICAL_PAPERS_PATH = os.path.join(DATASET_DIR, "ranked_papers.csv")
CLAIMS_PATH = os.path.join(DATASET_DIR, "claims.csv")
CONTRADICTION_PATH = os.path.join(DATASET_DIR, "contradictions.json")
SYNTHESIS_PATH = os.path.join(DATASET_DIR, "final_synthesis.md")

# Load existing datasets safely
def load_data():
    ranked_df = pd.read_csv(CLINICAL_PAPERS_PATH) if os.path.exists(CLINICAL_PAPERS_PATH) else None
    claims_df = pd.read_csv(CLAIMS_PATH) if os.path.exists(CLAIMS_PATH) else None

    contradictions = {}
    if os.path.exists(CONTRADICTION_PATH):
        try:
            with open(CONTRADICTION_PATH, "r", encoding="utf-8") as f:
                contradictions = json.load(f)
        except Exception:
            pass

    synthesis_text = ""
    if os.path.exists(SYNTHESIS_PATH):
        try:
            with open(SYNTHESIS_PATH, "r", encoding="utf-8") as f:
                synthesis_text = f.read()
        except Exception:
            pass

    return ranked_df, claims_df, contradictions, synthesis_text

ranked_df, claims_df, contradictions, synthesis_text = load_data()

st.title("🧬 Corvus Bio Dashboard")
st.caption("Scientific evidence synthesis, contradiction detection, and research exploration")

# 1. Dashboard Overview Metrics
if ranked_df is not None or claims_df is not None:
    st.markdown("### 📊 Metrics Summary")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_papers = len(ranked_df) if ranked_df is not None else 0
        st.markdown(
            f'<div class="card"><div class="metric-value">{total_papers}</div><div class="metric-label">Analyzed Papers</div></div>',
            unsafe_allow_html=True
        )

    with col2:
        total_claims = len(claims_df) if claims_df is not None else 0
        st.markdown(
            f'<div class="card"><div class="metric-value">{total_claims}</div><div class="metric-label">Extracted Claims</div></div>',
            unsafe_allow_html=True
        )

    with col3:
        num_contradictions = len(contradictions.get("contradictions", [])) if isinstance(contradictions, dict) else 0
        st.markdown(
            f'<div class="card"><div class="metric-value" style="color: #FF7B72;">{num_contradictions}</div><div class="metric-label">Contradictions</div></div>',
            unsafe_allow_html=True
        )

    with col4:
        confidence = contradictions.get("overall_confidence", "N/A").upper() if isinstance(contradictions, dict) else "N/A"
        st.markdown(
            f'<div class="card"><div class="metric-value" style="color: #56D364;">{confidence}</div><div class="metric-label">Evidence Confidence</div></div>',
            unsafe_allow_html=True
        )

# 2. Main Tabs
tabs = st.tabs(["📝 Scientific Synthesis", "⚡ Contradictions & Agreements", "📚 Ranked Clinical Evidence", "🔎 Claims Exploration"])

with tabs[0]:
    st.markdown("### 🔬 Executive Synthesis & Consensus Report")
    if synthesis_text:
        st.markdown(synthesis_text)
    else:
        st.info("No synthesis report found. Please run the contradiction and synthesis pipelines first.")

with tabs[1]:
    st.markdown("### ⚡ Pairwise Analysis & Scientific Disputes")
    if isinstance(contradictions, dict) and contradictions:
        subtab1, subtab2, subtab3 = st.tabs(["Contradictions", "Agreements", "Partial Agreements"])

        with subtab1:
            con_list = contradictions.get("contradictions", [])
            if con_list:
                for c in con_list:
                    with st.expander(f"⚡ Conflict: {c['claim_a_title'][:60]}... VS {c['claim_b_title'][:60]}..."):
                        st.markdown(f"**Claim A**: {c['claim_a_text']}")
                        st.markdown(f"**Claim B**: {c['claim_b_text']}")
                        st.markdown(f"**Cosine Similarity**: `{c['cosine_similarity']:.3f}` | **Confidence**: `{c['confidence']:.2f}` | **Weight**: `{c['evidence_weight']:.1f}`")
                        st.markdown(f"**Explanation**: {c['explanation']}")
            else:
                st.success("No direct contradictions detected in this cohort!")

        with subtab2:
            ag_list = contradictions.get("agreements", [])
            if ag_list:
                for a in ag_list:
                    with st.expander(f"✅ Agreement: {a['claim_a_title'][:60]}..."):
                        st.markdown(f"**Claim A**: {a['claim_a_text']}")
                        st.markdown(f"**Claim B**: {a['claim_b_text']}")
                        st.markdown(f"**Explanation**: {a['explanation']}")
            else:
                st.info("No explicit agreements found.")

        with subtab3:
            pa_list = contradictions.get("partial_agreements", [])
            if pa_list:
                for p in pa_list:
                    with st.expander(f"🔀 Partial: {p['claim_a_title'][:60]}..."):
                        st.markdown(f"**Claim A**: {p['claim_a_text']}")
                        st.markdown(f"**Claim B**: {p['claim_b_text']}")
                        st.markdown(f"**Explanation**: {p['explanation']}")
            else:
                st.info("No partial agreements found.")
    else:
        st.info("No contradiction data found.")

with tabs[2]:
    st.markdown("### 📚 Ranked Evidence (Oxford Level of Evidence)")
    if ranked_df is not None:
        min_score = st.slider("Filter by Evidence Score", 1.0, 10.0, 1.0, step=0.5)
        filtered_df = ranked_df[ranked_df["evidence_score"] >= min_score].sort_values("evidence_score", ascending=False)

        st.dataframe(
            filtered_df[["title", "evidence_score", "study_design", "sample_size", "source", "year"]],
            column_config={
                "title": "Paper Title",
                "evidence_score": st.column_config.ProgressColumn(
                    "Evidence Score", min_value=1.0, max_value=10.0, format="%.1f"
                ),
                "study_design": "Study Design",
                "sample_size": "Sample Size",
                "source": "Source",
                "year": "Year"
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No ranked evidence data found.")

with tabs[3]:
    st.markdown("### 🔎 Claim & Stance Exploration")
    if claims_df is not None:
        search_query = st.text_input("Filter claims by keyword:", "")
        stance_filter = st.multiselect("Stance:", ["support", "contradict", "neutral"], default=["support", "contradict", "neutral"])

        filtered_claims = claims_df.copy()
        if search_query:
            filtered_claims = filtered_claims[filtered_claims["claim"].str.contains(search_query, case=False, na=False)]
        filtered_claims = filtered_claims[filtered_claims["stance"].isin(stance_filter)]

        st.dataframe(
            filtered_claims[["title", "claim", "stance", "reason"]],
            column_config={
                "title": "Paper Title",
                "claim": "Extracted Claim",
                "stance": "Stance",
                "reason": "Supporting Reasoning"
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No extracted claims found.")

# 3. Interactive Q&A Session (Ask the LLM with Dataset Context)
st.sidebar.markdown("---")
st.sidebar.subheader("💬 Ask the Dataset (RAG)")
user_question = st.sidebar.text_input("Ask a question about this evidence:", placeholder="e.g., Does metformin decrease cancer recurrence?")
model_choice = st.sidebar.selectbox("Ollama Model:", ["llama3.1:8b"])

if st.sidebar.button("Query LLM") and user_question:
    with st.sidebar.status("Searching dataset & calling Ollama...", expanded=True) as status:
        context_list = []

        if claims_df is not None:
            keyword_matches = claims_df[claims_df['claim'].str.contains('|'.join(user_question.split()[:4]), case=False, na=False)].head(8)
            if len(keyword_matches) < 3:
                keyword_matches = claims_df.head(8)

            for _, r in keyword_matches.iterrows():
                context_list.append(
                    f"Claim: {r['claim']} (Stance: {r.get('stance', 'neutral')}, Reason: {r.get('reason', 'N/A')})"
                )

        if ranked_df is not None:
            top_ranked = ranked_df.sort_values(by="evidence_score", ascending=False).head(5)
            for _, r in top_ranked.iterrows():
                context_list.append(
                    f"Paper Title: {r['title']} | Score: {r['evidence_score']} | Abstract Summary: {str(r['abstract'])[:180]}..."
                )

        context_str = "\n".join(context_list)

        prompt = f"""You are a biomedical research assistant analyzing a local dataset of research papers.
Answer the user's question using the scientific evidence provided below.

USER QUESTION:
{user_question}

DATASET CONTEXT:
{context_str}

Please provide a structured, concise response backed by the contextual evidence above. State if evidence is missing or conflicting. Do not mention system prompts.
"""
        try:
            response = ollama.chat(
                model=model_choice,
                messages=[{"role": "user", "content": prompt}]
            )
            ans = response["message"]["content"]
            status.update(label="Response generated!", state="complete")
            st.sidebar.markdown("### 🤖 LLM Answer")
            st.sidebar.info(ans)
        except Exception as err:
            status.update(label=f"Ollama Error: {err}", state="error")
            st.sidebar.error(f"Failed to query Ollama. Make sure the service is running locally. Error: {err}")