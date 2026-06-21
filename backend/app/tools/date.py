import re
import dateparser
from datetime import datetime, date
from typing import Optional
from app.config.logger import logger

NORMALIZATIONS = {
    r"\bday after tomorrow\b": "in 2 days",
    r"\bday before yesterday\b": "2 days ago",
    r"\beod\b": "end of today",
    r"\beom\b": "end of this month",
    r"\beoy\b": "end of this year",
    r"\bq1\b": "january 1",
    r"\bq2\b": "april 1",
    r"\bq3\b": "july 1",
    r"\bq4\b": "october 1",
    r"\bfortnightly\b": "in 2 weeks",
    r"\ba week\b": "1 week",
    r"\ba month\b": "1 month",
    r"\bcouple( of)? days\b": "2 days",
}

BASE_SETTINGS = {
    "PREFER_DAY_OF_MONTH": "first",
    "RETURN_TIME_AS_PERIOD": False,
    "PARSERS": ["relative-time", "absolute-time", "timestamp", "custom-formats"],
}


def resolve_date(
    date_text: str,
    *,
    prefer: str = "future",
    timezone: str = "UTC",
    relative_base: Optional[datetime] = None,
    languages: Optional[list[str]] = None,
    return_datetime: bool = False,
) -> Optional[str | date | datetime]:
    """Parse natural language date text into an ISO date string or datetime."""
    if not date_text or not date_text.strip():
        return None

    original = date_text.strip()
    normalized = re.sub(
        "|".join(NORMALIZATIONS),
        lambda m: next(
            v for k, v in NORMALIZATIONS.items() if re.match(k, m.group(), re.I)
        ),
        original.lower(),
        flags=re.IGNORECASE,
    )

    settings = {
        **BASE_SETTINGS,
        "PREFER_DATES_FROM": prefer,
        "TIMEZONE": timezone,
        "RELATIVE_BASE": relative_base or datetime.now(),
        **({"LANGUAGES": languages} if languages else {}),
    }

    parsed = dateparser.parse(normalized, settings=settings) or dateparser.parse(
        original, settings=settings
    )

    if parsed is None:
        logger.debug("resolve_date: failed to parse %r", original)
        return None

    return parsed if return_datetime else parsed.date().isoformat()
