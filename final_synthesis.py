import pandas as pd
import ollama

# Load claims
claims_df = pd.read_csv(
    "dataset/claims.csv"
)

# Load ranked papers
ranked_df = pd.read_csv(
    "dataset/ranked_papers.csv"
)

# Combine top evidence papers
top_papers = ranked_df.sort_values(
    by="evidence_score",
    ascending=False
).head(10)

paper_context = ""

for i, row in top_papers.iterrows():

    paper_context += f"""
Title:
{row['title']}

Evidence Score:
{row['evidence_score']}

Abstract:
{row['abstract']}

"""

# Combine claims
claims_text = "\n".join(
    claims_df[
        "claim_output"
    ].astype(str)
)

prompt = f"""
You are an expert biomedical
research assistant.

You are analyzing scientific
evidence about metformin
and breast cancer.

Use:
1. Scientific claims
2. Evidence quality
3. Research contradictions

Write:

1. Overall conclusion
2. Supporting evidence
3. Contradictory evidence
4. Possible reasons for disagreement
5. Confidence level
(low/medium/high)

Claims:
{claims_text}

Top Evidence Papers:
{paper_context}
"""

response = ollama.chat(
    model="llama3.1:8b",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

final_answer = response[
    "message"
]["content"]

print("\n")
print("=" * 70)
print("FINAL SCIENTIFIC SYNTHESIS")
print("=" * 70)
print(final_answer)

# Save result
with open(
    "dataset/final_synthesis.txt",
    "w",
    encoding="utf-8"
) as f:
    f.write(final_answer)

print(
    "\nSaved final_synthesis.txt"
)