import os
import tempfile

import gradio as gr

from agent import run_advisor
from guardrails import redact_pii


def advise(question: str, csv_file) -> str:

    if not (question or "").strip():
        return "Please type a question."

    csv_path = None

    if csv_file is not None:

        # Read uploaded CSV
        with open(csv_file.name, "r", encoding="utf-8") as f:
            content = f.read()

        # Remove personal information
        cleaned = redact_pii(content)

        # Save cleaned CSV
        csv_path = os.path.join(
            tempfile.gettempdir(),
            "advisoriq_upload.csv"
        )

        with open(
            csv_path,
            "w",
            encoding="utf-8"
        ) as f:
            f.write(cleaned)

    # Run AdvisorIQ
    return run_advisor(
        question,
        csv_path
    )


demo = gr.Interface(
    fn=advise,

    inputs=[
        gr.Textbox(
            label="Your question",
            lines=3,
            placeholder=(
                "Example: What are the risks of investing "
                "in Apple?"
            )
        ),

        gr.File(
            label="Upload transactions (CSV) — optional",
            file_types=[".csv"]
        )
    ],

    outputs=gr.Markdown(
        label="AdvisorIQ says"
    ),

    title="AdvisorIQ — Wealth-Management Copilot",

    description=(
        "Ask an investment research question and "
        "(optionally) upload your transactions. "
        "Educational only, not financial advice."
    )
)


if __name__ == "__main__":

    demo.launch(
        server_name="0.0.0.0",
        server_port=int(
            os.environ.get("PORT", 7860)
        )
    )