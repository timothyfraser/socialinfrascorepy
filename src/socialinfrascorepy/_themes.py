"""Theme and keyword lookup (internal).

The keyword-theme lookups date from the original keyword-search ingestion
pipeline.  Sites now come from Overture Maps open data, so these are internal
helpers.  The old public names remain for one release as deprecated aliases.
"""

from __future__ import annotations

import warnings
from typing import Optional, Sequence, Union

import pandas as pd

from socialinfrascorepy._client import SIClient
from socialinfrascorepy._http import perform
from socialinfrascorepy._utils import SIScorecardError, _as_dataframe


def _get_themes(client: SIClient) -> pd.DataFrame:
    """List available social-infrastructure themes (internal).

    Authentication is optional; the endpoint is public.

    Returns
    -------
    pandas.DataFrame
        Columns ``theme`` (int) and ``type`` (str).
    """
    data = perform(client, "/rest/v1/rpc/fn_get_themes", json={})
    return _as_dataframe(data)


def _get_theme_keywords(
    client: SIClient,
    theme_ids: Optional[Union[Sequence[int], str]] = None,
) -> pd.DataFrame:
    """List keywords for given theme IDs (internal).

    Authentication is optional; the endpoint is public.

    Parameters
    ----------
    theme_ids : list of int, str, or None
        Integer sequence or comma-separated string of theme IDs.
        Pass ``None`` to retrieve all keywords.

    Returns
    -------
    pandas.DataFrame
        Columns ``theme``, ``type``, and ``term``.
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

    data = perform(
        client,
        "/rest/v1/rpc/fn_get_theme_keywords",
        json={"p_theme_ids": theme_ids_csv},
    )
    return _as_dataframe(data)


def get_themes(client: SIClient) -> pd.DataFrame:
    """Deprecated alias of an internal helper.

    .. deprecated:: 0.2.0
        ``get_themes()`` is no longer part of the public API and will be
        removed in the next release.
    """
    warnings.warn(
        "`get_themes()` is deprecated and will be removed in the next "
        "release; it is no longer part of the public API.",
        DeprecationWarning,
        stacklevel=2,
    )
    return _get_themes(client)


def get_theme_keywords(
    client: SIClient,
    theme_ids: Optional[Union[Sequence[int], str]] = None,
) -> pd.DataFrame:
    """Deprecated alias of an internal helper.

    .. deprecated:: 0.2.0
        ``get_theme_keywords()`` is no longer part of the public API and will
        be removed in the next release.
    """
    warnings.warn(
        "`get_theme_keywords()` is deprecated and will be removed in the "
        "next release; it is no longer part of the public API.",
        DeprecationWarning,
        stacklevel=2,
    )
    return _get_theme_keywords(client, theme_ids)
