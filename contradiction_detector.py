import pandas as pd
import ollama

claims_df = pd.read_csv(
    "dataset/claims.csv"
)

# Support multiple possible column names for LLM outputs
if "llm_output" in claims_df.columns:
    outputs = claims_df["llm_output"].astype(str).tolist()
elif "claim_output" in claims_df.columns:
    outputs = claims_df["claim_output"].astype(str).tolist()
else:
    print("Available columns:", list(claims_df.columns))
    raise SystemExit("No suitable LLM output column found in dataset/claims.csv")

all_claims = "\n".join(outputs)

prompt = f"""
You are a biomedical analyst.

Analyze these scientific claims.

Find:
1. Agreements
2. Contradictions
3. Possible reasons for disagreement

Claims:
{all_claims}
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

result = response[
    "message"
]["content"]

print(result)

with open(
    "dataset/contradictions.txt",
    "w",
    encoding="utf-8"
) as f:
    f.write(result)

print("Saved contradictions.txt")