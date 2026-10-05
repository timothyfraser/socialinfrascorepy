"""The single HTTP choke point for the package.

Every request the package makes to Supabase (PostgREST, GoTrue) goes through
:func:`perform`.  No other module imports ``requests``.  That gives one place
to set headers, map errors, and swap the transport.

Browser (Pyodide / JupyterLite / Pyodide-based docs)
----------------------------------------------------
``requests`` cannot open sockets in the browser.  When this module is imported
under Pyodide (``sys.platform == "emscripten"``) it tries to import
``pyodide_http`` and call ``pyodide_http.patch_all()``, which reroutes
``requests`` through the browser's ``XMLHttpRequest``/``fetch``.  The browser
must therefore install it before importing this package::

    import micropip
    await micropip.install(["pyodide-http", "socialinfrascorepy"])

Supabase answers CORS for any origin when the anon key is sent, so reads,
sign-in and request submission all work from a web page.  ``pyodide-http`` is
**not** a dependency of the package; it is only needed in the browser.
"""

from __future__ import annotations

import sys
from typing import Any, Dict, Mapping, Optional

import requests as _requests

from socialinfrascorepy._client import SIClient, _require_auth
from socialinfrascorepy._utils import (
    SIScorecardError,
    _add_common_headers,
    _parse_response,
)

#: Seconds to wait for Supabase before giving up.
DEFAULT_TIMEOUT = 60

_PYODIDE_PATCHED = False


def _patch_for_pyodide() -> bool:
    """Route ``requests`` through the browser when running under Pyodide.

    Returns ``True`` if the patch was applied.  Outside Pyodide this is a
    no-op; inside Pyodide without ``pyodide-http`` installed it leaves
    ``requests`` untouched (calls will then fail with a clear transport
    error).
    """
    global _PYODIDE_PATCHED
    if _PYODIDE_PATCHED:
        return True
    if sys.platform != "emscripten":
        return False
    try:
        import pyodide_http  # type: ignore[import-not-found]

        pyodide_http.patch_all()
    except ImportError:
        return False
    _PYODIDE_PATCHED = True
    return True


_patch_for_pyodide()


def perform(
    client: SIClient,
    path: str,
    method: str = "POST",
    json: Any = None,
    params: Optional[Mapping[str, Any]] = None,
    auth: bool = False,
) -> Any:
    """Send one request to the client's Supabase project.

    Parameters
    ----------
    client : SIClient
        Supplies the project URL, the ``apikey`` and (when *auth* is true) the
        user's bearer token.
    path : str
        Path under the project URL, e.g. ``"/rest/v1/rpc/fn_get_themes"``.
    method : str, default ``"POST"``
        HTTP verb.
    json : object, optional
        JSON request body.
    params : mapping, optional
        Query-string parameters.
    auth : bool, default False
        When true the call needs a signed-in user: the client's access token is
        sent as the ``Authorization`` bearer, and an unauthenticated client
        raises :class:`~socialinfrascorepy.SIScorecardError` before any
        network traffic.  When false the anon key is the bearer.

    Returns
    -------
    object
        The decoded JSON payload (``[]`` for an empty body).

    Raises
    ------
    SIScorecardError
        On HTTP status >= 400 (carrying the server's message) or when the
        request cannot be sent at all.
    """
    if auth:
        _require_auth(client)

    url = f"{client.supabase_url}/{path.lstrip('/')}"
    headers: Dict[str, str] = _add_common_headers(client, use_auth=auth)

    try:
        resp = _requests.request(
            method.upper(),
            url,
            headers=headers,
            json=json,
            params=params,
            timeout=DEFAULT_TIMEOUT,
        )
    except _requests.RequestException as exc:
        raise SIScorecardError(f"Request to {url} failed: {exc}") from exc

    return _parse_response(resp)
