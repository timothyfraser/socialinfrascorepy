"""Client object for the Social Infrastructure Scorecard API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from socialinfrascorepy._utils import SIScorecardError


@dataclass(frozen=True)
class SIClient:
    """Lightweight, immutable configuration object used by every API call.

    Attributes
    ----------
    supabase_url : str
        Supabase project URL (e.g. ``https://project.supabase.co``).
    anon_key : str
        Supabase anon / publishable API key.
    access_token : str or None
        Authenticated access token (populated after sign-in).
    refresh_token : str or None
        Refresh token (populated after sign-in).
    """

    supabase_url: str
    anon_key: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None


def client(
    supabase_url: str,
    anon_key: str,
    access_token: Optional[str] = None,
    refresh_token: Optional[str] = None,
) -> SIClient:
    """Create a socialinfrascorepy API client.

    Parameters
    ----------
    supabase_url : str
        Supabase project URL (e.g. ``https://project.supabase.co``).
    anon_key : str
        Supabase anon / publishable API key.
    access_token : str, optional
        Authenticated access token.
    refresh_token : str, optional
        Refresh token.

    Returns
    -------
    SIClient
        A client object passed to all other package functions.

    Raises
    ------
    SIScorecardError
        If *supabase_url* or *anon_key* is empty.

    Examples
    --------
    >>> import os, socialinfrascorepy as si
    >>> cli = si.client(
    ...     os.environ["SUPABASE_URL"],
    ...     os.environ["SUPABASE_ANON_KEY"],
    ... )
    """
    if not isinstance(supabase_url, str) or not supabase_url.strip():
        raise SIScorecardError("`supabase_url` must be a non-empty string.")
    if not isinstance(anon_key, str) or not anon_key.strip():
        raise SIScorecardError("`anon_key` must be a non-empty string.")

    return SIClient(
        supabase_url=supabase_url.strip().rstrip("/"),
        anon_key=anon_key.strip(),
        access_token=str(access_token) if access_token is not None else None,
        refresh_token=str(refresh_token) if refresh_token is not None else None,
    )


def _require_auth(cl: SIClient) -> None:
    """Raise if the client has no access token."""
    if not cl.access_token:
        raise SIScorecardError(
            "This function requires an authenticated user. "
            "Call `sign_in()` first."
        )


def _with_session(
    cl: SIClient,
    access_token: Optional[str] = None,
    refresh_token: Optional[str] = None,
) -> SIClient:
    """Return a new client carrying the given session tokens."""
    return client(
        supabase_url=cl.supabase_url,
        anon_key=cl.anon_key,
        access_token=access_token,
        refresh_token=refresh_token,
    )
