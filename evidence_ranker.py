import pandas as pd

# Load papers
df = pd.read_csv(
    "dataset/clean_papers.csv"
)

print("Loaded papers:",
      len(df))


def assign_score(text):
    text = str(text).lower()

    # Strongest evidence
    if (
        "meta-analysis" in text
        or "systematic review" in text
    ):
        return 10

    # Very strong
    elif (
        "randomized trial" in text
        or "clinical trial" in text
        or "phase iii" in text
    ):
        return 8

    # Medium
    elif (
        "cohort study" in text
        or "observational study" in text
    ):
        return 6

    # Weak
    elif "review" in text:
        return 5

    # Very weak
    elif "case report" in text:
        return 3

    # Unknown/default
    return 4


scores = []

for i, row in df.iterrows():

    combined_text = (
        str(row["title"])
        + " "
        + str(row["abstract"])
    )

    score = assign_score(
        combined_text
    )

    scores.append(score)

df["evidence_score"] = scores

# Save results
df.to_csv(
    "dataset/ranked_papers.csv",
    index=False
)

print(
    "Saved ranked_papers.csv"
)

print(
    "\nTop Evidence Scores:"
)

print(
    df[
        [
            "title",
            "evidence_score"
        ]
    ].head(10)
)