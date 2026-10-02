from agent import run_advisor


answer = run_advisor(
    """
    Check my recent transactions and tell me
    if anything looks suspicious.
    """,
    "data/sample_transactions.csv"
)


print("\n==============================")
print("ADVISORIQ RESPONSE")
print("==============================\n")

print(answer)