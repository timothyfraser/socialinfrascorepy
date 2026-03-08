"""Authentication functions: sign-up, sign-in, password reset, account deletion."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

import requests as _requests

from socialinfrascorepy._client import SIClient, _require_auth, _with_session
from socialinfrascorepy._utils import (
    SIScorecardError,
    _add_common_headers,
    _parse_response,
)


def sign_up(
    client: SIClient,
    email: str,
    password: str,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Sign up a new user.

    Parameters
    ----------
    client : SIClient
        A client from :func:`~socialinfrascorepy.client`.
    email : str
        User email address.
    password : str
        User password.
    name : str, optional
        Display name stored in user metadata.

    Returns
    -------
    dict
        A dictionary with keys ``client`` (:class:`SIClient` carrying
        session tokens when immediately available), ``session``,
        ``user``, and ``data``.

    Examples
    --------
    >>> result = si.sign_up(cli, "you@example.com", "strong-password",
    ...                     name="Your Name")
    >>> authed = result["client"]
    """
    payload: Dict[str, Any] = {
        "email": str(email),
        "password": str(password),
    }
    if name and str(name).strip():
        payload["options"] = {"data": {"display_name": str(name)}}

    resp = _requests.post(
        f"{client.supabase_url}/auth/v1/signup",
        headers=_add_common_headers(client, use_auth=False),
        json=payload,
    )
    data = _parse_response(resp)

    session = data.get("session") or {}
    user = data.get("user")

    new_client: SIClient
    if session.get("access_token"):
        new_client = _with_session(
            client,
            access_token=session["access_token"],
            refresh_token=session.get("refresh_token"),
        )
    else:
        new_client = client

    return {
        "client": new_client,
        "session": session,
        "user": user,
        "data": data,
    }


def sign_in(
    client: SIClient,
    email: str,
    password: str,
) -> Dict[str, Any]:
    """Sign in with email and password.

    Parameters
    ----------
    client : SIClient
        A client from :func:`~socialinfrascorepy.client`.
    email : str
        User email address.
    password : str
        User password.

    Returns
    -------
    dict
        A dictionary with keys ``client`` (authenticated
        :class:`SIClient`), ``session``, and ``data``.

    Examples
    --------
    >>> auth = si.sign_in(cli, os.environ["EMAIL"], os.environ["PASSWORD"])
    >>> authed = auth["client"]
    """
    resp = _requests.post(
        f"{client.supabase_url}/auth/v1/token?grant_type=password",
        headers=_add_common_headers(client, use_auth=False),
        json={"email": str(email), "password": str(password)},
    )
    data = _parse_response(resp)

    new_client = _with_session(
        client,
        access_token=data.get("access_token"),
        refresh_token=data.get("refresh_token"),
    )

    return {
        "client": new_client,
        "session": {
            "access_token": data.get("access_token"),
            "refresh_token": data.get("refresh_token"),
            "expires_in": data.get("expires_in"),
            "token_type": data.get("token_type"),
        },
        "data": data,
    }


def send_password_reset(client: SIClient) -> Dict[str, Any]:
    """Request a password-reset email for the signed-in user.

    Parameters
    ----------
    client : SIClient
        A client from :func:`~socialinfrascorepy.client` authenticated
        with :func:`sign_in`.

    Returns
    -------
    dict
        Parsed response payload from Supabase auth.

    Raises
    ------
    SIScorecardError
        If the client is not authenticated or the user email cannot be
        resolved.
    """
    _require_auth(client)

    user_resp = _requests.get(
        f"{client.supabase_url}/auth/v1/user",
        headers=_add_common_headers(client, use_auth=True),
    )
    user = _parse_response(user_resp)

    email = user.get("email") if isinstance(user, dict) else None
    if not email or not isinstance(email, str) or not email.strip():
        raise SIScorecardError(
            "Could not resolve authenticated user email for password reset."
        )

    resp = _requests.post(
        f"{client.supabase_url}/auth/v1/recover",
        headers=_add_common_headers(client, use_auth=False),
        json={"email": email.strip()},
    )
    return _parse_response(resp)


def delete_account(client: SIClient) -> Dict[str, Any]:
    """Delete the currently authenticated account.

    Calls the ``fn_delete_account`` Supabase RPC which initiates
    account deletion via the Auth Admin API server-side.

    Parameters
    ----------
    client : SIClient
        A client from :func:`~socialinfrascorepy.client` authenticated
        with :func:`sign_in`.

    Returns
    -------
    dict
        A dictionary with ``status``, ``user_id``, and ``message``.
    """
    _require_auth(client)

    resp = _requests.post(
        f"{client.supabase_url}/rest/v1/rpc/fn_delete_account",
        headers=_add_common_headers(client, use_auth=True),
        json={},
    )
    data = _parse_response(resp)

    if isinstance(data, str):
        data = json.loads(data)
    return data
