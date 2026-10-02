import shutil
from pathlib import Path

import pandas as pd

from langchain.agents import create_agent
from langchain_core.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI

from rag import get_retriever
from checker import flag_transactions
from guardrails import make_safe


# Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0
)


# RAG retriever
retriever = get_retriever()


# Temporary uploaded transaction file
UPLOAD_PATH = "data/_current_upload.csv"


# --------------------------------------------------
# TOOL 1 — MARKET DATA
# --------------------------------------------------

def market_data(ticker: str) -> str:

    import yfinance as yf

    ticker = ticker.strip().upper()

    hist = yf.Ticker(ticker).history(
        period="1mo"
    )

    if hist.empty:
        return f"No market data for {ticker}."

    price = hist["Close"].iloc[-1]
    month_ago = hist["Close"].iloc[0]

    change = (
        (price - month_ago)
        / month_ago
        * 100
    )

    return (
        f"{ticker}: "
        f"price ${price:.2f}, "
        f"1-month change {change:+.1f}%."
    )


# --------------------------------------------------
# TOOL 2 — RAG RESEARCH
# --------------------------------------------------

def research(query: str) -> str:

    hits = retriever.invoke(query)

    if not hits:
        return "No relevant documents."

    return "\n\n".join(
        f"[source] {document.page_content}"
        for document in hits
    )


# --------------------------------------------------
# TOOL 3 — TRANSACTION CHECKER
# --------------------------------------------------

def check_uploaded(_input: str) -> str:

    if not Path(UPLOAD_PATH).exists():

        return (
            "No transactions were uploaded "
            "for this question."
        )

    flagged = flag_transactions(
        pd.read_csv(UPLOAD_PATH)
    )

    if flagged.empty:

        return "No suspicious transactions found."

    return (
        "Suspicious transactions:\n"
        + flagged.to_string(index=False)
    )


# --------------------------------------------------
# CREATE TOOLS
# --------------------------------------------------

TOOLS = [

    Tool(
        name="MarketData",
        func=market_data,
        description=(
            "Get the current price and "
            "1-month trend for a stock ticker "
            "such as AAPL."
        )
    ),

    Tool(
        name="Research",
        func=research,
        description=(
            "Search the finance research "
            "documents to ground an answer "
            "about a company or financial topic."
        )
    ),

    Tool(
        name="CheckTransactions",
        func=check_uploaded,
        description=(
            "Check the user's uploaded "
            "transactions for suspicious activity."
        )
    )

]


# --------------------------------------------------
# AGENT INSTRUCTIONS
# --------------------------------------------------

SYSTEM_PROMPT = """
You are AdvisorIQ, a wealth-management
research assistant.

Use the available tools to ground your answers
in real data and research documents.

Use MarketData when the user asks about a stock
or market price.

Use Research when the question requires financial
research or company information.

Use CheckTransactions when the user has uploaded
transactions and asks about suspicious activity.

Never promise a specific return.

Never claim an investment is guaranteed.

Give concise, educational answers.

Do not present your response as personalized
financial advice.
"""


# --------------------------------------------------
# CREATE AGENT
# --------------------------------------------------

agent = create_agent(
    llm,
    TOOLS,
    system_prompt=SYSTEM_PROMPT
)


# --------------------------------------------------
# MAIN FUNCTION USED BY APP
# --------------------------------------------------

def run_advisor(
    question: str,
    csv_path: str | None = None
) -> str:

    # Store uploaded CSV
    if csv_path:

        shutil.copyfile(
            csv_path,
            UPLOAD_PATH
        )

    else:

        Path(
            UPLOAD_PATH
        ).unlink(
            missing_ok=True
        )

    # Run the agent
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question
                }
            ]
        }
    )

    # Get final response
    answer = result["messages"][-1].text

    # Find Research tool outputs
    sources = [
        message.content
        for message in result["messages"]
        if getattr(message, "name", "") == "Research"
        and "No relevant" not in message.content
    ]

    # Apply output guardrails
    return make_safe(
        answer,
        sources
    )