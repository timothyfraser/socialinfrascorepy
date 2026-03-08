"""Theme and keyword lookup functions."""

from __future__ import annotations

from typing import List, Optional, Sequence, Union

import pandas as pd
import requests as _requests

from socialinfrascorepy._client import SIClient
from socialinfrascorepy._utils import (
    SIScorecardError,
    _add_common_headers,
    _as_dataframe,
    _parse_response,
)


def get_themes(client: SIClient) -> pd.DataFrame:
    """List available social-infrastructure themes.

    Authentication is optional; the endpoint is public.

    Parameters
    ----------
    client : SIClient
        A client from :func:`~socialinfrascorepy.client`.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with columns ``theme`` (int) and ``type`` (str).

    Examples
    --------
    >>> themes = si.get_themes(cli)
    """
    resp = _requests.post(
        f"{client.supabase_url}/rest/v1/rpc/fn_get_themes",
        headers=_add_common_headers(client, use_auth=False),
        json={},
    )
    return _as_dataframe(_parse_response(resp))


def get_theme_keywords(
    client: SIClient,
    theme_ids: Optional[Union[Sequence[int], str]] = None,
) -> pd.DataFrame:
    """List keywords for given theme IDs.

    Authentication is optional; the endpoint is public.

    Parameters
    ----------
    client : SIClient
        A client from :func:`~socialinfrascorepy.client`.
    theme_ids : list of int, str, or None
        Integer sequence or comma-separated string of theme IDs.
        Pass ``None`` to retrieve all keywords.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with columns ``theme``, ``type``, and ``term``.

    Examples
    --------
    >>> kw = si.get_theme_keywords(cli, theme_ids=[1, 3, 4])
    """
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

    resp = _requests.post(
        f"{client.supabase_url}/rest/v1/rpc/fn_get_theme_keywords",
        headers=_add_common_headers(client, use_auth=False),
        json={"p_theme_ids": theme_ids_csv},
    )
    return _as_dataframe(_parse_response(resp))
