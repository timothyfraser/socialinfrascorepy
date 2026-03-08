"""Site retrieval for a location."""

from __future__ import annotations

import pandas as pd
import requests as _requests

from socialinfrascorepy._client import SIClient, _require_auth
from socialinfrascorepy._utils import (
    SIScorecardError,
    _add_common_headers,
    _as_dataframe,
    _clamp_limit,
    _parse_response,
)


def get_sites(
    client: SIClient,
    location_id: str,
    limit: int = 1000,
) -> pd.DataFrame:
    """Get social-infrastructure sites for a location.

    Returns a capped random sample of sites within the given location.

    Parameters
    ----------
    client : SIClient
        A client from :func:`~socialinfrascorepy.client` authenticated
        with :func:`~socialinfrascorepy.sign_in`.
    location_id : str
        Location identifier from ``public.location.location_id``.
    limit : int, default 1000
        Maximum rows to return (hard-capped at 1000).

    Returns
    -------
    pandas.DataFrame
        Site rows.

    Examples
    --------
    >>> sites = si.get_sites(authed, location_id="42")
    """
    _require_auth(client)

    if not isinstance(location_id, str) or not location_id.strip():
        raise SIScorecardError("`location_id` must be a non-empty string.")

    limit = _clamp_limit(limit, max_limit=1000)

    resp = _requests.post(
        f"{client.supabase_url}/rest/v1/rpc/fn_get_sites_by_location_id",
        headers=_add_common_headers(client, use_auth=True),
        json={
            "p_location_id": location_id.strip(),
            "p_limit": limit,
        },
    )
    return _as_dataframe(_parse_response(resp))
