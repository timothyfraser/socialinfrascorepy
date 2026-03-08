"""
socialinfrascorepy
==================

Python client for the Social Infrastructure Scorecard.

Communicates exclusively through Supabase Auth and PostgREST APIs.
Supports signup/signin, polygon lookup, request submission with
theme and grid configuration, scorecard downloads, and account
management. No direct Plumber API access is required.
"""

from socialinfrascorepy._client import SIClient, client
from socialinfrascorepy._auth import (
    sign_up,
    sign_in,
    send_password_reset,
    delete_account,
)
from socialinfrascorepy._polygons import (
    search_locations,
    get_boundary_by_osm_id,
    get_boundary_by_location_id,
    get_boundary_by_area_id,
    get_boundary_by_place_name,
)
from socialinfrascorepy._themes import (
    get_themes,
    get_theme_keywords,
)
from socialinfrascorepy._scorecard import get_scorecard
from socialinfrascorepy._sites import get_sites
from socialinfrascorepy._requests import (
    submit_request,
    get_request_status,
    get_requests,
)
from socialinfrascorepy._account import (
    get_subscription,
    get_usage,
    get_remaining_queries,
)
from socialinfrascorepy._utils import SIScorecardError

__version__ = "0.1.0"

__all__ = [
    "SIClient",
    "SIScorecardError",
    "client",
    "sign_up",
    "sign_in",
    "send_password_reset",
    "delete_account",
    "search_locations",
    "get_boundary_by_osm_id",
    "get_boundary_by_location_id",
    "get_boundary_by_area_id",
    "get_boundary_by_place_name",
    "get_themes",
    "get_theme_keywords",
    "get_scorecard",
    "get_sites",
    "submit_request",
    "get_request_status",
    "get_requests",
    "get_subscription",
    "get_usage",
    "get_remaining_queries",
]
