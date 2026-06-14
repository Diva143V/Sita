import pandas as pd

df = pd.read_csv(
    "dataset/final_papers.csv"
)

print("Before filtering:",
      len(df))

# Convert to lowercase
df["title"] = (
    df["title"]
    .fillna("")
    .str.lower()
)

df["abstract"] = (
    df["abstract"]
    .fillna("")
    .str.lower()
)

# Keep only breast cancer + metformin papers
filtered_df = df[
    (
        df["title"].str.contains(
            "metformin"
        ) |
        df["abstract"].str.contains(
            "metformin"
        )
    )
    &
    (
        df["title"].str.contains(
            "breast cancer"
        ) |
        df["abstract"].str.contains(
            "breast cancer"
        )
    )
]

print("After filtering:",
      len(filtered_df))

filtered_df.to_csv(
    "dataset/clean_papers.csv",
    index=False
)

print("Saved clean_papers.csv")