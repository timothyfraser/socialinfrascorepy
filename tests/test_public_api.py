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
        "get_scorecard": ["client", "osm_id", "location_id", "limit", "offset"],
        "get_sites": ["client", "location_id", "limit"],
        "submit_request": [
            "client",
            "geometry",
            "name",
            "display_name",
            "place_name",
            "country",
            "state",
            "theme_ids",
            "kwargs",
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


def test_google_era_helpers_are_not_public():
    assert "get_themes" not in si.__all__
    assert "get_theme_keywords" not in si.__all__
    assert callable(si._themes._get_themes)
    assert callable(si._themes._get_theme_keywords)


def test_no_google_wording_in_docstrings():
    import pkgutil

    for mod in pkgutil.iter_modules(si.__path__):
        m = __import__(f"socialinfrascorepy.{mod.name}", fromlist=["x"])
        for name, obj in vars(m).items():
            doc = getattr(obj, "__doc__", None) or ""
            assert "google" not in doc.lower(), f"{mod.name}.{name}"
        assert "google" not in (m.__doc__ or "").lower()
