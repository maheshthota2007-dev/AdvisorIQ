import re


def redact_pii(text: str) -> str:

    # Account/card numbers
    text = re.sub(
        r"\b\d{12,19}\b",
        "[ACCOUNT]",
        text
    )

    # Email addresses
    text = re.sub(
        r"[\w.+-]+@[\w-]+\.[\w.-]+",
        "[EMAIL]",
        text
    )

    # Phone numbers
    text = re.sub(
        r"\b\d{10}\b",
        "[PHONE]",
        text
    )

    return text


BANNED = [
    "guaranteed return",
    "guaranteed profit",
    "can't lose",
    "risk-free"
]


DISCLAIMER = (
    "\n\n"
    "_Disclaimer: This is educational information, "
    "not financial advice._"
)


def make_safe(answer: str, sources: list[str]) -> str:

    for phrase in BANNED:
        answer = re.sub(
            phrase,
            "may vary",
            answer,
            flags=re.I
        )

    if not sources:
        answer += (
            "\n\n"
            "_Note: limited source support for this answer._"
        )

    return answer + DISCLAIMER