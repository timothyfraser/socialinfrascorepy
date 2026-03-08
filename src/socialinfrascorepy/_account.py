"""Account, subscription, and usage functions."""

from __future__ import annotations

from typing import Optional

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


def get_remaining_queries(client: SIClient) -> pd.DataFrame:
    """Get remaining monthly query quota.

    Parameters
    ----------
    client : SIClient
        A client from :func:`~socialinfrascorepy.client` authenticated
        with :func:`~socialinfrascorepy.sign_in`.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with subscription tier and remaining query metrics.

    Examples
    --------
    >>> remaining = si.get_remaining_queries(authed)
    """
    _require_auth(client)

    resp = _requests.post(
        f"{client.supabase_url}/rest/v1/rpc/fn_get_user_remaining_queries",
        headers=_add_common_headers(client, use_auth=True),
        json={},
    )
    return _as_dataframe(_parse_response(resp))
