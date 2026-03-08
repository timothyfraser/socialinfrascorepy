"""Scorecard retrieval."""

from __future__ import annotations

from typing import Optional

import pandas as pd
import requests as _requests

from socialinfrascorepy._client import SIClient, _require_auth
from socialinfrascorepy._polygons import _si_get_polygon_by_osm_id
from socialinfrascorepy._utils import (
    SIScorecardError,
    _add_common_headers,
    _as_dataframe,
    _clamp_limit,
    _parse_response,
)


def get_scorecard(
    client: SIClient,
    osm_id: Optional[int] = None,
    location_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> pd.DataFrame:
    """Get scorecard results for a location.

    Provide exactly one of *osm_id* or *location_id*.

    Parameters
    ----------
    client : SIClient
        A client from :func:`~socialinfrascorepy.client` authenticated
        with :func:`~socialinfrascorepy.sign_in`.
    osm_id : int, optional
        OSM ID used to resolve a bounds area.
    location_id : str, optional
        Location ID for direct scorecard lookup.
    limit : int, default 100
        Maximum rows to return (hard-capped at 100).
    offset : int, default 0
        Pagination offset.

    Returns
    -------
    pandas.DataFrame
        Scorecard result rows with density, diversity, dispersion, and
        composite scores.

    Raises
    ------
    SIScorecardError
        If neither or both of *osm_id* / *location_id* are given, or
        if *offset* is negative.

    Examples
    --------
    >>> scores = si.get_scorecard(authed, osm_id=5128581)
    """
    _require_auth(client)

    limit = _clamp_limit(limit, max_limit=100)
    offset = int(offset)
    if offset < 0:
        raise SIScorecardError("`offset` must be a non-negative integer.")

    has_osm = osm_id is not None
    has_location = location_id is not None
    if has_osm == has_location:
        raise SIScorecardError(
            "Provide exactly one of `osm_id` or `location_id`."
        )

    if has_location:
        resp = _requests.post(
            f"{client.supabase_url}/rest/v1/rpc/fn_scorecard_result_by_location_id",
            headers=_add_common_headers(client, use_auth=True),
            json={
                "p_location_id": str(location_id),
                "p_limit": limit,
                "p_offset": offset,
            },
        )
        return _as_dataframe(_parse_response(resp))

    bounds_row = _si_get_polygon_by_osm_id(client, osm_id)
    if bounds_row.empty:
        return pd.DataFrame()

    bounds_id = str(bounds_row["id"].iloc[0])
    resp = _requests.get(
        f"{client.supabase_url}/rest/v1/scorecard_result",
        headers=_add_common_headers(client, use_auth=True),
        params={
            "area_type": "eq.bounds",
            "area_id": f"eq.{bounds_id}",
            "order": "computed_at.desc,id.desc",
            "limit": limit,
            "offset": offset,
        },
    )
    return _as_dataframe(_parse_response(resp))
