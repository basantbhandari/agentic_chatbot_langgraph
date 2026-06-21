from datetime import datetime
import dateparser
from langchain.tools import tool


@tool
def parse_date(date_text: str) -> str:
    """Convert natural language dates into YYYY-MM-DD format."""

    parsed = dateparser.parse(
        date_text,
        settings={
            "PREFER_DATES_FROM": "future",
            "RELATIVE_BASE": datetime.now(),
        },
    )

    if not parsed:
        return "Could not parse date"

    return parsed.strftime("%Y-%m-%d")
