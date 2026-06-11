import pandas as pd

df = pd.read_csv(
    "reranker_training_data.csv"
)

print(
    "\nPain Similarity\n"
)

print(
    df["pain_similarity"].describe()
)

print(
    "\nSolution Similarity\n"
)

print(
    df["solution_similarity"].describe()
)

print(
    "\nCustomer Similarity\n"
)

print(
    df["customer_similarity"].describe()
)

print(
    "\nLabel Distribution\n"
)

print(
    df["label"].value_counts()
)