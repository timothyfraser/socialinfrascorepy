"""Account, subscription, and usage functions."""

from __future__ import annotations

from typing import Any, Optional

import pandas as pd
import requests as _requests

from socialinfrascorepy._client import SIClient, _require_auth
from socialinfrascorepy._utils import (
    SIScorecardError,
    _add_common_headers,
    _as_dataframe,
    _parse_response,
)


def get_subscription(client: SIClient) -> pd.DataFrame:
    """Get current subscription profile.

    Parameters
    ----------
    client : SIClient
        A client from :func:`~socialinfrascorepy.client` authenticated
        with :func:`~socialinfrascorepy.sign_in`.

    Returns
    -------
    pandas.DataFrame
        A single-row DataFrame with the user's profile including
        subscription tier.

    Examples
    --------
    >>> profile = si.get_subscription(authed)
    """
    _require_auth(client)

    resp = _requests.get(
        f"{client.supabase_url}/rest/v1/profiles",
        headers=_add_common_headers(client, use_auth=True),
        params={
            "select": "id,display_name,role,subscription_tier,created_at,updated_at",
            "limit": 1,
        },
    )
    return _as_dataframe(_parse_response(resp))


def get_usage(
    client: SIClient,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Get usage summary for a date range.

    Parameters
    ----------
    client : SIClient
        A client from :func:`~socialinfrascorepy.client` authenticated
        with :func:`~socialinfrascorepy.sign_in`.
    start_date : str, optional
        Start date in ``YYYY-MM-DD`` format.
    end_date : str, optional
        End date in ``YYYY-MM-DD`` format.

    Returns
    -------
    pandas.DataFrame
        Usage metrics from ``fn_get_user_usage``.

    Examples
    --------
    >>> usage = si.get_usage(authed, start_date="2025-01-01")
    """
    _require_auth(client)

    start_val = (
        str(start_date).strip()
        if start_date and str(start_date).strip()
        else None
    )
    end_val = (
        str(end_date).strip()
        if end_date and str(end_date).strip()
        else None
    )

    resp = _requests.post(
        f"{client.supabase_url}/rest/v1/rpc/fn_get_user_usage",
        headers=_add_common_headers(client, use_auth=True),
        json={"p_start_date": start_val, "p_end_date": end_val},
    )
    return _as_dataframe(_parse_response(resp))


#: Output columns of :func:`get_remaining_queries`, in order.
_FAIR_USE_COLUMNS = [
    "tier",
    "display_name",
    "per_day",
    "day_requests",
    "remaining_today",
    "per_hour",
    "hour_requests",
    "remaining_this_hour",
    "km2_per_day",
    "day_km2",
    "km2_per_hour",
    "hour_km2",
    "concurrent",
    "running",
    "waiting_limit",
    "waiting",
    "hour_resets_at",
    "day_resets_at",
]


def _limit_value(value: Any) -> Optional[float]:
    """Map a fair-use limit to a number, or ``None`` when unlimited.

    The server reports ``-1`` (or nothing) for an unlimited limit.
    """
    if value is None:
        return None
    try:
        num = float(value)
    except (TypeError, ValueError):
        return None
    if num < 0:
        return None
    return int(num) if num.is_integer() else num


def _usage_value(value: Any) -> float:
    """Map a usage counter to a number, treating missing as ``0``."""
    if value is None:
        return 0
    try:
        num = float(value)
    except (TypeError, ValueError):
        return 0
    return int(num) if num.is_integer() else num


def _remaining(limit: Optional[float], used: float) -> Optional[float]:
    """Remaining allowance (never negative), or ``None`` when unlimited."""
    if limit is None:
        return None
    return max(limit - used, 0)


def _timestamp(value: Any) -> pd.Timestamp:
    """Parse an ISO timestamp to a UTC :class:`pandas.Timestamp` (or NaT)."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return pd.NaT
    ts = pd.to_datetime(value, utc=True, errors="coerce")
    return pd.NaT if ts is None else ts


def _fair_use_frame(status: Any) -> pd.DataFrame:
    """Flatten an ``fn_fair_use_status`` payload into a one-row DataFrame."""
    if isinstance(status, list):
        status = status[0] if status else {}
    if not isinstance(status, dict):
        status = {}

    limits = status.get("limits") or {}
    usage = status.get("usage") or {}
    resets = status.get("resets") or {}

    per_day = _limit_value(limits.get("per_day"))
    per_hour = _limit_value(limits.get("per_hour"))
    day_requests = _usage_value(usage.get("day_requests"))
    hour_requests = _usage_value(usage.get("hour_requests"))

    row = {
        "tier": status.get("tier"),
        "display_name": status.get("display_name"),
        "per_day": per_day,
        "day_requests": day_requests,
        "remaining_today": _remaining(per_day, day_requests),
        "per_hour": per_hour,
        "hour_requests": hour_requests,
        "remaining_this_hour": _remaining(per_hour, hour_requests),
        "km2_per_day": _limit_value(limits.get("km2_per_day")),
        "day_km2": _usage_value(usage.get("day_km2")),
        "km2_per_hour": _limit_value(limits.get("km2_per_hour")),
        "hour_km2": _usage_value(usage.get("hour_km2")),
        "concurrent": _limit_value(limits.get("concurrent")),
        "running": _usage_value(usage.get("running")),
        "waiting_limit": _limit_value(limits.get("waiting")),
        "waiting": _usage_value(usage.get("waiting")),
        "hour_resets_at": _timestamp(resets.get("hour_at")),
        "day_resets_at": _timestamp(resets.get("day_at")),
    }

    df = pd.DataFrame([row], columns=_FAIR_USE_COLUMNS)
    # Limits and remaining counts may be missing (unlimited): keep them
    # numeric so ``None`` shows as NaN rather than an object column.
    for col in (
        "per_day",
        "remaining_today",
        "per_hour",
        "remaining_this_hour",
        "km2_per_day",
        "km2_per_hour",
        "concurrent",
        "waiting_limit",
    ):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def get_remaining_queries(client: SIClient) -> pd.DataFrame:
    """Get your fair-use limits, current usage, and what is left.

    The Social Infrastructure Scorecard is free. Each account gets
    rolling fair-use limits so the shared compute stays available to
    everyone. On the free tier these are:

    - 200 requests per day and 30 requests per hour;
    - 50,000 km² of drawn area per day and 15,000 km² per hour;
    - 3 requests running at once (further requests wait in a queue).

    The hourly window resets at ``hour_resets_at`` and the daily window
    at ``day_resets_at``. Limits that do not apply to your account
    (unlimited) are returned as missing values (``NaN``), and so are the
    matching ``remaining_*`` columns.

    Parameters
    ----------
    client : SIClient
        A client from :func:`~socialinfrascorepy.client` authenticated
        with :func:`~socialinfrascorepy.sign_in`.

    Returns
    -------
    pandas.DataFrame
        A single-row DataFrame with columns:

        - ``tier``, ``display_name`` --- your account tier and name.
        - ``per_day``, ``day_requests``, ``remaining_today`` --- daily
          request limit, requests used today, and requests left today.
        - ``per_hour``, ``hour_requests``, ``remaining_this_hour`` ---
          the same for the current hour.
        - ``km2_per_day``, ``day_km2``, ``km2_per_hour``, ``hour_km2``
          --- drawn-area limits and area used (km²).
        - ``concurrent``, ``running`` --- how many requests may run at
          once, and how many are running now.
        - ``waiting_limit``, ``waiting`` --- how many requests may wait
          in the queue, and how many are waiting now.
        - ``hour_resets_at``, ``day_resets_at`` --- when each window
          resets (UTC :class:`pandas.Timestamp`, or ``NaT``).

    Examples
    --------
    >>> left = si.get_remaining_queries(authed)
    >>> left[["per_day", "day_requests", "remaining_today"]]
    """
    _require_auth(client)

    resp = _requests.post(
        f"{client.supabase_url}/rest/v1/rpc/fn_fair_use_status",
        headers=_add_common_headers(client, use_auth=True),
        json={},
    )
    return _fair_use_frame(_parse_response(resp))
