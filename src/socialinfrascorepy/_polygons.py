"""Polygon / boundary lookup functions."""

from __future__ import annotations

import re
from typing import Optional

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

_UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}"
    r"-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$"
)


def _normalize_opt_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


# -- internal implementations ------------------------------------------------


def _si_get_polygon_by_osm_id(client: SIClient, osm_id: int) -> pd.DataFrame:
    _require_auth(client)

    try:
        osm_id_num = int(osm_id)
    except (TypeError, ValueError):
        raise SIScorecardError("`osm_id` must be numeric.")

    resp = _requests.get(
        f"{client.supabase_url}/rest/v1/bounds",
        headers=_add_common_headers(client, use_auth=True),
        params={
            "select": "id,name,display_name,osm_id,geometry",
            "osm_id": f"eq.{osm_id_num}",
            "limit": 1,
        },
    )
    return _as_dataframe(_parse_response(resp))


def _si_get_polygon_by_location_id(
    client: SIClient, location_id: str
) -> pd.DataFrame:
    _require_auth(client)

    if not isinstance(location_id, str) or not location_id.strip():
        raise SIScorecardError("`location_id` must be a non-empty string.")

    resp = _requests.post(
        f"{client.supabase_url}/rest/v1/rpc/fn_bounds_by_location_id",
        headers=_add_common_headers(client, use_auth=True),
        json={"p_location_id": location_id.strip()},
    )
    return _as_dataframe(_parse_response(resp))


def _si_get_polygon_by_area_id(client: SIClient, area_id: str) -> pd.DataFrame:
    _require_auth(client)

    area_id = str(area_id).strip()
    if not area_id:
        raise SIScorecardError("`area_id` must be a non-empty UUID string.")
    if not _UUID_RE.match(area_id):
        raise SIScorecardError("`area_id` must be a valid UUID string.")

    resp = _requests.post(
        f"{client.supabase_url}/rest/v1/rpc/fn_bounds_by_area_id",
        headers=_add_common_headers(client, use_auth=True),
        json={"p_area_id": area_id},
    )
    return _as_dataframe(_parse_response(resp))


def _si_get_polygon_lookup_by_place_name(
    client: SIClient,
    place_name: str,
    country: Optional[str] = None,
    state: Optional[str] = None,
    limit: int = 5,
) -> pd.DataFrame:
    _require_auth(client)

    place_name = str(place_name).strip()
    if not place_name:
        raise SIScorecardError("`place_name` must be a non-empty string.")

    resp = _requests.post(
        f"{client.supabase_url}/rest/v1/rpc/fn_location_lookup_by_place_name",
        headers=_add_common_headers(client, use_auth=True),
        json={
            "p_place_name": place_name,
            "p_country": _normalize_opt_text(country),
            "p_state": _normalize_opt_text(state),
            "p_limit": _clamp_limit(limit, max_limit=5),
        },
    )
    return _as_dataframe(_parse_response(resp))


def _si_get_polygon_by_place_name(
    client: SIClient,
    place_name: str,
    country: Optional[str] = None,
    state: Optional[str] = None,
) -> pd.DataFrame:
    _require_auth(client)

    place_name = str(place_name).strip()
    if not place_name:
        raise SIScorecardError("`place_name` must be a non-empty string.")

    resp = _requests.post(
        f"{client.supabase_url}/rest/v1/rpc/fn_bounds_by_place_name",
        headers=_add_common_headers(client, use_auth=True),
        json={
            "p_place_name": place_name,
            "p_country": _normalize_opt_text(country),
            "p_state": _normalize_opt_text(state),
        },
    )
    return _as_dataframe(_parse_response(resp))


# -- public wrappers (match R package names) ---------------------------------


def search_locations(
    client: SIClient,
    query: str,
    country: Optional[str] = None,
    state: Optional[str] = None,
    limit: int = 5,
) -> pd.DataFrame:
    """Search for locations by place name.

    Parameters
    ----------
    client : SIClient
        A client from :func:`~socialinfrascorepy.client` authenticated
        with :func:`~socialinfrascorepy.sign_in`.
    query : str
        Place name to search.
    country : str, optional
        Country filter.
    state : str, optional
        State / region filter.
    limit : int, default 5
        Maximum rows to return (hard-capped at 5).

    Returns
    -------
    pandas.DataFrame
        Matching location rows.

    Examples
    --------
    >>> candidates = si.search_locations(authed, query="Ithaca", state="NY")
    """
    return _si_get_polygon_lookup_by_place_name(
        client, place_name=query, country=country, state=state, limit=limit
    )


def get_boundary_by_osm_id(client: SIClient, osm_id: int) -> pd.DataFrame:
    """Get boundary by OpenStreetMap ID.

    Parameters
    ----------
    client : SIClient
        A client from :func:`~socialinfrascorepy.client` authenticated
        with :func:`~socialinfrascorepy.sign_in`.
    osm_id : int
        Numeric OSM identifier.

    Returns
    -------
    pandas.DataFrame
        A single-row DataFrame with boundary geometry, or empty if not
        found.

    Examples
    --------
    >>> poly = si.get_boundary_by_osm_id(authed, osm_id=5128581)
    """
    return _si_get_polygon_by_osm_id(client, osm_id)


def get_boundary_by_location_id(
    client: SIClient, location_id: str
) -> pd.DataFrame:
    """Get boundary by location ID.

    Parameters
    ----------
    client : SIClient
        A client from :func:`~socialinfrascorepy.client` authenticated
        with :func:`~socialinfrascorepy.sign_in`.
    location_id : str
        Location identifier from ``public.location.location_id``.

    Returns
    -------
    pandas.DataFrame
        A single-row DataFrame with boundary geometry, or empty if not
        found.
    """
    return _si_get_polygon_by_location_id(client, location_id)


def get_boundary_by_area_id(client: SIClient, area_id: str) -> pd.DataFrame:
    """Get boundary by area ID.

    Parameters
    ----------
    client : SIClient
        A client from :func:`~socialinfrascorepy.client` authenticated
        with :func:`~socialinfrascorepy.sign_in`.
    area_id : str
        UUID area identifier from ``public.location.area_id``.

    Returns
    -------
    pandas.DataFrame
        A single-row DataFrame with boundary geometry, or empty if not
        found.

    Raises
    ------
    SIScorecardError
        If *area_id* is not a valid UUID.
    """
    return _si_get_polygon_by_area_id(client, area_id)


def get_boundary_by_place_name(
    client: SIClient,
    query: str,
    country: Optional[str] = None,
    state: Optional[str] = None,
) -> pd.DataFrame:
    """Get boundary by place name.

    Resolves a single boundary polygon from a place-name search.

    Parameters
    ----------
    client : SIClient
        A client from :func:`~socialinfrascorepy.client` authenticated
        with :func:`~socialinfrascorepy.sign_in`.
    query : str
        Place name to resolve.
    country : str, optional
        Country filter.
    state : str, optional
        State / region filter.

    Returns
    -------
    pandas.DataFrame
        A single-row DataFrame with boundary geometry, or empty if not
        found.

    Examples
    --------
    >>> boundary = si.get_boundary_by_place_name(
    ...     authed, query="Ithaca", state="NY"
    ... )
    """
    return _si_get_polygon_by_place_name(
        client, place_name=query, country=country, state=state
    )
