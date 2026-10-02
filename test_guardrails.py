from guardrails import redact_pii, make_safe


text = (
    "My email is mahesh@example.com and "
    "my phone number is 9876543210. "
    "My account number is 123456789012."
)

print("===== PII TEST =====")
print(redact_pii(text))


print("\n===== SAFETY TEST =====")

answer = (
    "This investment has guaranteed profit "
    "and is risk-free."
)

safe_answer = make_safe(
    answer,
    ["Apple research document"]
)

print(safe_answer)