import inspect

import socialinfrascorepy as si


def test_public_api_symbols_present():
    expected = {
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
    }
    assert set(si.__all__) == expected


def test_function_signatures_match_contract():
    expected = {
        "client": ["supabase_url", "anon_key", "access_token", "refresh_token"],
        "sign_up": ["client", "email", "password", "name"],
        "sign_in": ["client", "email", "password"],
        "send_password_reset": ["client"],
        "delete_account": ["client"],
        "search_locations": ["client", "query", "country", "state", "limit"],
        "get_boundary_by_osm_id": ["client", "osm_id"],
        "get_boundary_by_location_id": ["client", "location_id"],
        "get_boundary_by_area_id": ["client", "area_id"],
        "get_boundary_by_place_name": ["client", "query", "country", "state"],
        "get_themes": ["client"],
        "get_theme_keywords": ["client", "theme_ids"],
        "get_scorecard": ["client", "osm_id", "location_id", "limit", "offset"],
        "get_sites": ["client", "location_id", "limit"],
        "submit_request": [
            "client",
            "geometry",
            "n_keywords",
            "name",
            "display_name",
            "place_name",
            "country",
            "state",
            "theme_ids",
            "sites_grid_sqkm",
        ],
        "get_request_status": ["client", "request_id"],
        "get_requests": ["client", "limit", "offset"],
        "get_subscription": ["client"],
        "get_usage": ["client", "start_date", "end_date"],
        "get_remaining_queries": ["client"],
    }

    for name, params in expected.items():
        sig = inspect.signature(getattr(si, name))
        assert list(sig.parameters.keys()) == params
