import streamlit as st

st.set_page_config(
    page_title="Corvus Bio V1",
    layout="wide"
)

st.title(
    "🧬 Corvus Bio V1"
)

st.subheader(
    "AI Biomedical Research Assistant"
)

question = st.text_input(
    "Ask a biomedical question:",
    placeholder="Example: Does metformin improve breast cancer survival?"
)

if st.button("Analyze"):

    if question:

        st.success(
            "Question received!"
        )

        st.write(
            "Question:",
            question
        )

    else:
        st.warning(
            "Please enter a question."
        )