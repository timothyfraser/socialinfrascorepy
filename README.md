# `socialinfrascorepy`
<h3><b>Map Social Infrastructure in Your Neighborhood</b></h3>

---

<!-- badges: start -->
<!-- badges: end -->

**`socialinfrascorepy`** lets you use the [Social Infrastructure Scorecard](https://github.com/timothyfraser/scorecard)
from Python.
View social infrastructure sites (parks, community spaces, places of worship, and more),
request scorecards for new areas, and download results for analysis.

> Looking for R? See the companion package,
> **[`socialinfrascorer`](https://timothyfraser.github.io/scorecard/socialinfrascorer/)**.

## Installation

```bash
pip install git+https://github.com/timothyfraser/scorecard.git#subdirectory=socialinfrascorepy
```

For optional geometry support:

```bash
pip install "socialinfrascorepy[geo] @ git+https://github.com/timothyfraser/scorecard.git#subdirectory=socialinfrascorepy"
```

## Quick start

```python
import os
import socialinfrascorepy as si

# 1. Create a client
cli = si.client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_ANON_KEY"],
)

# 2. Sign in
auth = si.sign_in(cli, os.environ["EMAIL"], os.environ["PASSWORD"])
authed = auth["client"]

# 3. Look up a neighborhood boundary
poly = si.get_boundary_by_osm_id(authed, osm_id=5128581)

# 4. Get the scorecard
scores = si.get_scorecard(authed, osm_id=5128581)
```

See the [Getting Started](https://timothyfraser.github.io/scorecard/socialinfrascorepy/get-started.html)
guide for a detailed walkthrough.

## Example query and output

```python
boundary = si.get_boundary_by_place_name(
    authed,
    query="Ithaca",
    state="NY",
)
```

Expected output (sample):

```text
   location_id   osm_id place_name    county state country  area_km2 geom_type
0        84217  5128581     Ithaca  Tompkins    NY      US     15.41   Polygon
```

## Key capabilities

| Area | Functions |
|------|-----------|
| **Auth** | `sign_up()`, `sign_in()`, `send_password_reset()`, `delete_account()` |
| **Boundaries** | `search_locations()`, `get_boundary_by_osm_id()`, `get_boundary_by_place_name()`, ... |
| **Themes** | `get_themes()`, `get_theme_keywords()` |
| **Requests** | `submit_request()`, `get_request_status()`, `get_requests()` |
| **Scorecard** | `get_scorecard()`, `get_sites()` |
| **Account** | `get_subscription()`, `get_usage()`, `get_remaining_queries()` |

---

## Environment variables

To use the package and query the database, you need two environment variables.
Get your keys from the Social Infrastructure Dashboard!

| Variable | Required | Purpose |
|----------|----------|---------|
| `SUPABASE_URL` | Always | Supabase project URL |
| `SUPABASE_ANON_KEY` | Always | Supabase anon/publishable key |

---

## Methodology

The querying strategy behind Mapping Social Infrastructure is based on
the methodology described in:

> Fraser, T., Cherdchaiyapong, N., Tekle, W., Thomas, E., Zayas, J., Page-Tan, C., & Aldrich, D. P. (2022). Trust but verify: Validating new measures for mapping social infrastructure in cities. *Urban Climate*, 46, 101287.
> <https://doi.org/10.1016/j.uclim.2022.101287>

The scorecard design strategy is based on the methods described in:

> Fraser, T., Chen, S., Yin, C., Zhang, X., & Aldrich, D. P. (2025). Urban Anchors, Climate Shocks: Measuring Social Infrastructure and their Exposure to Natural Hazards in U.S. Cities. Cornell Systems Studio.
> DOI forthcoming.

The scorecard measures three dimensions of social infrastructure in a
neighborhood: **density** (how many facilities exist), **diversity** (the
variety of facility types), and **dispersion** (how evenly facilities are
spread across the area). These are combined into a composite letter-grade
score.

---

## Credits

**`socialinfrascorepy`** is developed by
**Tim Fraser** and **Nabira Ahmad**.

> For questions, please contact package maintainer **Tim Fraser** at <tmf77@cornell.edu>.

---

## License

> **`socialinfrascorepy` Source-Available License v1.0**.
> You may use unmodified copies,
> but modification and distribution of modified versions are not permitted.
> See [`LICENSE`](LICENSE).
