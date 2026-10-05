"""Client object for the Social Infrastructure Scorecard API."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from socialinfrascorepy._utils import SIScorecardError


# Public by design: the URL and the publishable (anon) key are already shipped
# in the scorecard web bundle, and row level security protects the data. The
# SI_SUPABASE_* environment variables only override them (testing, self-hosting).
PUBLIC_SUPABASE_URL = "https://annuvayiqynyksnzkpoy.supabase.co"
PUBLIC_SUPABASE_ANON_KEY = "sb_publishable_SS0DtvFh990Zcj-6q7t4nw_VRdCF_Vb"


def _default_url() -> str:
    """Return ``SI_SUPABASE_URL`` if set and non-empty, else the public URL."""
    return os.environ.get("SI_SUPABASE_URL", "").strip() or PUBLIC_SUPABASE_URL


def _default_key() -> str:
    """Return ``SI_SUPABASE_ANON_KEY`` if set and non-empty, else the public key."""
    return (
        os.environ.get("SI_SUPABASE_ANON_KEY", "").strip()
        or PUBLIC_SUPABASE_ANON_KEY
    )


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
    supabase_url: Optional[str] = None,
    anon_key: Optional[str] = None,
    access_token: Optional[str] = None,
    refresh_token: Optional[str] = None,
) -> SIClient:
    """Create a socialinfrascorepy API client.

    Call ``client()`` with no arguments: it connects to the Social
    Infrastructure Scorecard's public Supabase project. The URL and the
    publishable (anon) key are public by design and built in, so you do not set
    any environment variables. Row level security protects the data; you still
    need ``sign_in()`` for anything that is not public.

    For testing or self-hosting, point the package elsewhere with the
    environment variables ``SI_SUPABASE_URL`` and ``SI_SUPABASE_ANON_KEY``, or
    pass the arguments directly.

    Parameters
    ----------
    supabase_url : str, optional
        Supabase project URL (e.g. ``https://project.supabase.co``). Defaults
        to ``SI_SUPABASE_URL`` if set, otherwise the scorecard's public project.
    anon_key : str, optional
        Supabase anon / publishable API key. Defaults to ``SI_SUPABASE_ANON_KEY``
        if set, otherwise the scorecard's public key. Never pass a service-role
        or secret key.
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
        If *supabase_url* or *anon_key* is passed explicitly but is empty.

    Examples
    --------
    >>> import socialinfrascorepy as si
    >>> cli = si.client()
    """
    if supabase_url is None:
        supabase_url = _default_url()
    if anon_key is None:
        anon_key = _default_key()
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
