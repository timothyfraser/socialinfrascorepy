"""Internal helpers shared across all modules."""

from __future__ import annotations

from typing import Any, Dict, Optional

import pandas as pd
import requests as _requests


class SIScorecardError(Exception):
    """Raised when a Supabase API call returns an error."""


def _clamp_limit(limit: Any, max_limit: int = 1000) -> int:
    """Coerce *limit* to an integer in ``[1, max_limit]``."""
    if max_limit < 1:
        raise ValueError("`max_limit` must be a positive integer.")
    try:
        lim = int(limit)
    except (TypeError, ValueError):
        lim = 1
    return max(1, min(lim, max_limit))


def _add_common_headers(
    client: Any,
    *,
    use_auth: bool = False,
) -> Dict[str, str]:
    """Build the headers dict used by every Supabase request.

    Parameters
    ----------
    client : SIClient
        Active client object.
    use_auth : bool
        If ``True`` and the client carries an access token, send that
        token as the ``Authorization`` bearer; otherwise fall back to
        the anon key.

    Returns
    -------
    dict
        HTTP headers.
    """
    headers: Dict[str, str] = {
        "apikey": client.anon_key,
        "Content-Type": "application/json",
    }
    if use_auth and client.access_token:
        headers["Authorization"] = f"Bearer {client.access_token}"
    else:
        headers["Authorization"] = f"Bearer {client.anon_key}"
    return headers


def _parse_response(resp: _requests.Response) -> Any:
    """Decode a Supabase response, raising on HTTP errors.

    Parameters
    ----------
    resp : requests.Response
        The raw HTTP response.

    Returns
    -------
    Any
        Parsed JSON payload (list, dict, or scalar).

    Raises
    ------
    SIScorecardError
        When the HTTP status code is >= 400.
    """
    if resp.status_code >= 400:
        try:
            body = resp.json()
        except ValueError:
            body = {}
        msg = (
            body.get("message")
            or body.get("error")
            or resp.text
            or f"HTTP {resp.status_code}"
        )
        raise SIScorecardError(msg)

    if not resp.text:
        return []
    try:
        return resp.json()
    except ValueError:
        return []


def _as_dataframe(data: Any) -> pd.DataFrame:
    """Convert a Supabase JSON payload to a :class:`pandas.DataFrame`.

    Parameters
    ----------
    data : Any
        Parsed JSON — typically a list of dicts, a single dict, or an
        empty structure.

    Returns
    -------
    pandas.DataFrame
    """
    if data is None:
        return pd.DataFrame()
    if isinstance(data, pd.DataFrame):
        return data
    if isinstance(data, list):
        if len(data) == 0:
            return pd.DataFrame()
        return pd.DataFrame(data)
    if isinstance(data, dict):
        return pd.DataFrame([data])
    return pd.DataFrame({"value": [data]})
