"""Request submission and status tracking."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional, Sequence, Union

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


def submit_request(
    client: SIClient,
    geometry: Any,
    n_keywords: Optional[int] = None,
    name: Optional[str] = None,
    display_name: Optional[str] = None,
    place_name: Optional[str] = None,
    country: str = "US",
    state: Optional[str] = None,
    theme_ids: Optional[Union[Sequence[int], str]] = None,
    sites_grid_sqkm: float = 2,
) -> Dict[str, Any]:
    """Submit a scorecard request for a new area.

    Validates geometry, checks quota, inserts bounds + location + request
    row, and triggers asynchronous processing -- all server-side via
    ``fn_submit_request`` in PostgreSQL.

    Parameters
    ----------
    client : SIClient
        A client from :func:`~socialinfrascorepy.client` authenticated
        with :func:`~socialinfrascorepy.sign_in`.
    geometry : dict or str
        GeoJSON geometry (Polygon or MultiPolygon, CRS 4326) as a Python
        dictionary or a JSON string.
    n_keywords : int, optional
        Number of ingestion keywords.  When ``None`` and *theme_ids* is
        provided, the server derives the count from matching theme
        keywords.
    name : str, optional
        Short identifier for the polygon.
    display_name : str, optional
        User-facing polygon label.
    place_name : str, optional
        Place name metadata.
    country : str, default ``"US"``
        Country code or name.
    state : str, optional
        State / region metadata.
    theme_ids : list of int, str, or None
        Integer sequence or comma-separated string of theme IDs for
        keyword selection.
    sites_grid_sqkm : float, default 2
        Query-grid cell size in sq km for Google Places ingestion.

    Returns
    -------
    dict
        A dictionary with ``request``, ``bounds_id``, ``location_id``,
        ``required_queries``, and ``usage`` fields.

    Examples
    --------
    >>> geom = {
    ...     "type": "Polygon",
    ...     "coordinates": [[
    ...         [-122.32, 47.60], [-122.30, 47.60],
    ...         [-122.30, 47.62], [-122.32, 47.62],
    ...         [-122.32, 47.60],
    ...     ]],
    ... }
    >>> result = si.submit_request(
    ...     authed, geometry=geom, theme_ids=[1, 3, 4],
    ... )
    """
    _require_auth(client)

    if isinstance(geometry, str):
        geometry_obj = json.loads(geometry)
    elif isinstance(geometry, dict):
        geometry_obj = geometry
    else:
        geometry_obj = json.loads(json.dumps(geometry))

    theme_ids_csv: Optional[str] = None
    if theme_ids is not None:
        if isinstance(theme_ids, str):
            theme_ids_csv = theme_ids.strip()
        elif hasattr(theme_ids, "__iter__"):
            theme_ids_csv = ",".join(str(int(tid)) for tid in theme_ids)
        else:
            raise SIScorecardError(
                "`theme_ids` must be a list of ints or a comma-separated string."
            )

    country_val = str(country).strip() if country and str(country).strip() else "US"

    payload: Dict[str, Any] = {
        "p_geometry_geojson": geometry_obj,
        "p_name": name,
        "p_display_name": display_name,
        "p_country": country_val,
        "p_state": str(state).strip() if state else None,
        "p_place_name": str(place_name).strip() if place_name else None,
        "p_theme_ids": theme_ids_csv,
        "p_n_keywords": int(n_keywords) if n_keywords is not None else None,
        "p_sites_grid_sqkm": float(sites_grid_sqkm),
    }

    resp = _requests.post(
        f"{client.supabase_url}/rest/v1/rpc/fn_submit_request",
        headers=_add_common_headers(client, use_auth=True),
        json=payload,
    )
    data = _parse_response(resp)

    if isinstance(data, str):
        data = json.loads(data)
    return data


def get_request_status(
    client: SIClient,
    request_id: str,
) -> pd.DataFrame:
    """Get status of a submitted request.

    Row-level security restricts results to the authenticated user's
    own requests.

    Parameters
    ----------
    client : SIClient
        A client from :func:`~socialinfrascorepy.client` authenticated
        with :func:`~socialinfrascorepy.sign_in`.
    request_id : str
        Request UUID string.

    Returns
    -------
    pandas.DataFrame
        A single-row DataFrame, or empty if not found.

    Examples
    --------
    >>> status = si.get_request_status(authed, result["request"]["id"])
    """
    _require_auth(client)

    if not isinstance(request_id, str) or not request_id.strip():
        raise SIScorecardError("`request_id` must be a non-empty UUID string.")

    resp = _requests.get(
        f"{client.supabase_url}/rest/v1/requests",
        headers=_add_common_headers(client, use_auth=True),
        params={
            "id": f"eq.{request_id.strip()}",
            "select": "*",
            "limit": 1,
        },
    )
    return _as_dataframe(_parse_response(resp))


def get_requests(
    client: SIClient,
    limit: int = 100,
    offset: int = 0,
) -> pd.DataFrame:
    """Get request history for the current user.

    Parameters
    ----------
    client : SIClient
        A client from :func:`~socialinfrascorepy.client` authenticated
        with :func:`~socialinfrascorepy.sign_in`.
    limit : int, default 100
        Maximum rows (hard-capped at 500).
    offset : int, default 0
        Pagination offset.

    Returns
    -------
    pandas.DataFrame
        Request rows.

    Examples
    --------
    >>> history = si.get_requests(authed)
    """
    _require_auth(client)

    limit = _clamp_limit(limit, max_limit=500)
    offset = int(offset)
    if offset < 0:
        raise SIScorecardError("`offset` must be a non-negative integer.")

    resp = _requests.post(
        f"{client.supabase_url}/rest/v1/rpc/fn_get_user_requests",
        headers=_add_common_headers(client, use_auth=True),
        json={"p_limit": limit, "p_offset": offset},
    )
    return _as_dataframe(_parse_response(resp))
