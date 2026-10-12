# Changelog

## 0.2.0 (2026-10-11)

### Changed

- `get_remaining_queries()` now reports the scorecard's rolling fair-use
  limits. It calls the `fn_fair_use_status` RPC (replacing
  `fn_get_user_remaining_queries`) and returns one row with `tier`,
  `display_name`, `per_day`, `day_requests`, `remaining_today`,
  `per_hour`, `hour_requests`, `remaining_this_hour`, `km2_per_day`,
  `day_km2`, `km2_per_hour`, `hour_km2`, `concurrent`, `running`,
  `waiting_limit`, `waiting`, `hour_resets_at` and `day_resets_at`.
  Free-tier limits are 200 requests per day, 30 per hour, 50,000 km² per
  day, 15,000 km² per hour, and 3 running at once. Unlimited values are
  returned as missing (`NaN` / `NaT`), and remaining counts never go
  below zero.
- Documentation describes fair-use limits instead of a monthly allowance.

### Removed

- There is no `change_subscription()`: the scorecard is free and has no
  paid tiers to switch between. A test now guards that it stays out of
  the public API.

## 0.1.0

- Initial release.
